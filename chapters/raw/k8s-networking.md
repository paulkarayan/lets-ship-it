# Overview of networking in k8s

Here's a map of the territories
┌─────────────────────────────────────────────────────────────────┐
│                        EXTERNAL TRAFFIC                         │
│                              │                                  │
│                              ▼                                  │
│                    ┌─────────────────┐                          │
│                    │  Load Balancer  │  (AWS ALB, NLB, etc.)    │
│                    └────────┬────────┘                          │
│                              │                                  │
│                              ▼                                  │
│                    ┌─────────────────┐                          │
│                    │     Ingress     │  (nginx, traefik, etc.)  │
│                    └────────┬────────┘                          │
│                              │                                  │
├──────────────────────────────┼──────────────────────────────────┤
│           CLUSTER INTERNAL   │                                  │
│                              ▼                                  │
│                    ┌─────────────────┐                          │
│                    │     Service     │  (stable virtual IP)     │
│                    └────────┬────────┘                          │
│                              │                                  │
│              ┌───────────────┼───────────────┐                  │
│              ▼               ▼               ▼                  │
│         ┌────────┐      ┌────────┐      ┌────────┐              │
│         │ Pod A  │      │ Pod B  │      │ Pod C  │              │
│         │10.1.1.5│      │10.1.2.3│      │10.1.3.8│              │
│         └────────┘      └────────┘      └────────┘              │
│                                                                 │
│         (Pod IPs change constantly — Services don't)            │
└─────────────────────────────────────────────────────────────────┘

### The Kubernetes Network Model

Kubernetes mandates three things (the [Kubernetes network model](https://kubernetes.io/docs/concepts/services-networking/#the-kubernetes-network-model)):

1. **Every Pod gets its own unique cluster-wide IP address**
2. **All pods can communicate with all other pods** — across nodes, without NAT
3. **Agents on a node can communicate with all pods on that node**

From these invariants,implementation is delegated to a CNI plugin (Calico, Cilium, Flannel, etc.). The CNI sets up the routing tables, virtual interfaces, and overlay networks to make it work.

Remember that pods are ephemeral ("cattle, not pets") so their IPs aren't hardcoded. We use a Service as a stable abstraction.

A Service has a fixed virtual IP, and when you connect to it the kube-proxy's iptables rules (or eBPF if using Cilium) rewrite your packet's destination to a healthy pod IP.
DNS makes it human-friendly. Instead of remembering 10.96.45.123, you use my-app.production.svc.cluster.local

# It's always DNS

Every pod in your cluster is automatically configured to use CoreDNS for name resolution. This is how pods find each other by name instead of IP.

We can watch it running:

```bash
kubectl get pods -n kube-system
```

```
➜  lets-ship-it git:(main) kubectl get pods -n kube-system                              ()
NAME                                                 READY   STATUS    RESTARTS   AGE
coredns-7d764666f9-7qs77                             1/1     Running   0          20h
coredns-7d764666f9-z4mg6                             1/1     Running   0          20h
etcd-lets-ship-it-control-plane                      1/1     Running   0          20h
kindnet-m45tz                                        1/1     Running   0          20h
kube-apiserver-lets-ship-it-control-plane            1/1     Running   0          20h
kube-controller-manager-lets-ship-it-control-plane   1/1     Running   0          20h
kube-proxy-4jlfk                                     1/1     Running   0          20h
kube-scheduler-lets-ship-it-control-plane            1/1     Running   0          20h
```

The kube-dns service IP (usually 10.96.0.10) is injected into every pod's /etc/resolv.conf

## DNS Resolution from Inside a Pod

We're going to jump into a pod using `exec` and watch the magic happen. Notice that the pod name is not static so I have to do some trickery to make it work.
Also we selected a base image to build our app on that uses `bash`, but often you'll need to run `sh` instead (such as with python-3.13-slim).

```bash
# make sure you have a service and pods running
kubectl get svc -n fastapi
kubectl get pods -n fastapi

# Get the pod name (it'll be something like fastapi-xxxxx-yyyyy)
POD_NAME=$(kubectl get pods -n fastapi -o jsonpath='{.items[0].metadata.name}')

# Exec into the pod - basically, get a shell inside of it
kubectl exec -it $POD_NAME -n fastapi -- bash
```

Now inside the pod:
```bash
# Look at DNS configuration
cat /etc/resolv.conf
```

You'll see something like:
```
root@lets-ship-it-584c4f66f8-htx9q:/app# cat /etc/resolv.conf
search fastapi.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
root@lets-ship-it-584c4f66f8-htx9q:/app# cat /etc/resolv.conf
search fastapi.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
```

Now let's pull out our trusty nslookup, which will need to be installed.

```
apt-get update && apt-get install -y dnsutils

# Full DNS name (FQDN)
nslookup lets-ship-it.fastapi.svc.cluster.local

# Short name (works because of search domains)
nslookup lets-ship-it
```

note that the error `;; Got recursion not available from 10.96.0.10` isn't a problem. CoreDNS just won't do recursive lookups for external domains by default from within cluster queries.


# What's happening under the kube-proxy?

When you curl http://lets-ship-it:8000, something has to translate that Service IP into an actual pod IP. That's the job of the `service proxy`.

Say it with me: when you curl a Service name, iptables rules (or eBPF programs) are doing the translation from virtual IP to pod IP, *entirely in the kernel*.

`kube-proxy` runs on every node as a DaemonSet. It watches the Kubernetes API for Services and EndpointSlices, then programs `iptables` rules to intercept and redirect traffic.


When a packet arrives destined for a Service IP (like 10.96.x.x), that IP doesn't actually exist on any machine (it's a virtual IP). The iptables rules catch the packet and rewrite its destination to one of the real pod IPs (aka DNAT — Destination Network Address Translation). This happens in the kernel's netfilter subsystem, before the packet ever reaches userspace.

App sends to 10.96.100.50:8000 (Service IP)
         │
         ▼
   ┌─────────────┐
   │  iptables   │  ← kube-proxy wrote these rules
   │   (DNAT)    │
   └─────────────┘
         │
         ▼
Packet rewritten to 10.244.1.15:8000 (Pod IP)
         │
         ▼
    Actual pod


You can see the iptables yourself. In kind, you can docker exec into the node container:
```bash

# List the kind nodes (they're just Docker containers)
docker ps --filter "name=kind"

# Exec into the control-plane node
# note the docker exec hasnt got a --
docker exec -it kind-control-plane bash

# Now you're on the "node" — run iptables
iptables -t nat -L KUBE-SERVICES -n
```


## Clillium and eBPF

iptables rules form a linear chain. With 10 services, it's fine. With 10,000 services, you have hundreds of thousands of rules, and every packet traverses them sequentially. Updates are also expensive — kube-proxy replaces the entire ruleset atomically.

The Modern Alternative is using eBPF with a tool like Cilium.
`eBPF` (extended Berkeley Packet Filter) lets you load small, verified programs directly into the Linux kernel. These programs run in response to events — network packets, system calls, tracepoints — at kernel speed, without context switching to userspace.

**Cilium** uses eBPF to replace iptables entirely for Kubernetes networking. Instead of linear rule chains and its O(n) lookups , it uses kernel-level **hash maps** for O(1) lookups.
The eBPF program intercepts packets at the socket level — sometimes before they even hit the full network stack — looks up the destination in a BPF map, and rewrites it directly.

### Why eBPF Matters Beyond Performance
Cilium's eBPF approach enables things iptables can't do:
1. L7 Network Policies — allow only HTTP GET to /api, deny POST to /admin. iptables only sees L3/L4 (IPs and ports), not HTTP methods or paths.
2. Transparent encryption — encrypt pod-to-pod traffic (WireGuard) without application changes.
3. Deep observability — Hubble (Cilium's observability layer) shows every network flow with HTTP-level detail, without performance penalty.
4. Runtime security — eBPF tracepoints detect when a container opens /etc/shadow, spawns a shell, or makes suspicious syscalls, alerting in milliseconds. This is how Falco works.


# Todo section
    - Can poke at: kubectl get endpoints / kubectl get endpointslices — see the actual pod IPs behind your Service
    - Can poke at: kubectl exec into a pod, curl another pod by Service name vs pod IP — show why Services matter
    - Can poke at: different Service types — change NodePort to ClusterIP, see what breaks
    - Describe Ingress / Gateway API — for external traffic.
