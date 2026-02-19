- Control plane vs data plane breakdown (NOTES §1)

  - Operators / reconcile loops conceptually (NOTES §4) —
  sets up chapter 06 (Kopf) and 16 (Go operator)
  - Admission webhooks conceptually (NOTES §3) — sets up why
  image signing, policy enforcement matter later


# Control Plane vs Data Plane

Every Kubernetes cluster has two distinct halves.

## Control Plane Components

### etcd
etcd is the single source of truth.

It's a distributed key-value store where everything in the cluster is persisted. If etcd dies and you don't have a backup, your cluster is gone.
The entire rest of the control plane is essentially a cache and computation layer on top of etcd.

etcd uses the Raft consensus algorithm, which means it needs a quorum of nodes to agree on writes. That's why control planes run 3 or 5 etcd instances.

### kube-apiserver
kube-apiserver is the only thing that ever talks to etcd. Everything else — kubectl, controllers, kubelets — talks to the API server, which then reads and writes etcd. 

It's a REST API. When you run kubectl get pods, you're making an HTTP GET to the API server. The API server validates your request, applies admission webhooks, authenticates you, and then writes to etcd.

kube-scheduler watches the API server for pods that have been created but not yet assigned to a node (their `spec.nodeName` is empty). When it sees one, it runs a scoring algorithm — does this node have enough CPU and memory? Does it satisfy affinity rules? Does it have the right taints/tolerations?

It picks a node and writes that node name back to the pod spec in etcd.

Critically, the scheduler doesn't start anything. It just makes a decision and writes it down.

### kube-controller-manager

kube-controller-manager is a collection of control loops running in a single process (remember the goroutines?). 

The Deployment controller watches for Deployments and creates/updates ReplicaSets.
The ReplicaSet controller watches for ReplicaSets and creates/deletes Pods.
The Job controller watches for Jobs and creates Pods.
etc...

Each controller does the same thing: watch etcd (via the API server) for the current state, compare it to the desired state, and take action to close the gap. This reconciliation loop pattern is the fundamental pattern in Kubernetes — everything is built on it.

### cloud-controller-manager
cloud-controller-manager handles cloud-specific stuff — provisioning load balancers when you create a Service of type LoadBalancer, managing node lifecycle in AWS/GCP, attaching volumes.

## Data Plane

### kubelet

kubelet is the agent running on every worker node. It watches the API server for pods that have been scheduled to its node. When it sees one, it calls the container runtime to actually start the containers.

It also continuously reports back to the API server — "these pods are running, here are their resource usages, this node has this much free memory." If kubelet dies on a node, that node's pods stop being reported and eventually get rescheduled elsewhere.

It's really just an HTTP client with some sugar. It reads ~/.kube/config to get the API server address and credentials (a client certificate, or a token, or an OIDC token), constructs REST requests, and pretty-prints the responses. You could do everything kubectl does with curl.

### kube-proxy
kube-proxy runs on every node and manages iptables (or ipvs) rules to implement Services. 

When you create a Service, kube-proxy on every node updates the firewall rules so that traffic to the Service's virtual IP gets load-balanced to the right pods.

### Container Runtime
The Container Runtime is what actually runs containers — containerd or CRI-O in modern clusters (Docker was deprecated as a runtime, but the images you build with Docker work identically on containerd or CRI-O). The kubelet talks to it via the CRI (Container Runtime Interface).

### CNI plugin
CNI plugin (e.g. Calico, Cilium, Flannel) handles pod networking. Every pod gets its own IP address, and the CNI plugin sets up the routing so pods can talk to each other across nodes. This is also where Network Policies are enforced — for example, Cilium uses eBPF to enforce network policies at the kernel level.

# How a Pod Actually Gets Created — End to End

1. kubectl serializes your manifest's YAML to JSON and POSTs it to the API server
2. API server authenticates you, runs admission webhooks (mutating first, then validating), validates the manifest schema, and writes the Deployment to etcd
3. The Deployment controller sees a new Deployment via its watch, creates a ReplicaSet, writes that to etcd
4. The ReplicaSet controller sees the new ReplicaSet, creates N Pod objects with empty nodeName, writes those to etcd
5. The scheduler sees pods with no node assigned via its watch, scores nodes, writes nodeName to each pod spec
6. The kubelet on the assigned node sees a pod assigned to it via its watch, calls containerd to pull the image and start the containers, then updates the pod's status in etcd
7. kube-proxy on all nodes sees the pods come up and updates iptables rules if a Service selects these pods

