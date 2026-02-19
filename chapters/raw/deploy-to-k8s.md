# basic setup

```
kind get clusters

# and if that doesn't work
kind create cluster --name lets-ship-it
```

This is a tacit check that your local k8s cluster is running with kind.

```
# if you have multiple clusters, switch to ours
kubectl cluster-info --context kind-lets-ship-it
# check if nodes show up
kubectl get nodes
# explained later
kubectl create namespace fastapi

```

# deploy the app in docker container to kubernetes

kind can't pull from your local Docker daemon directly. later we can setup a proper image registry but for now just load it:
```bash
docker build -t lets-ship-it .
kind load docker-image lets-ship-it --name lets-ship-it
```

now we need to write the k8s manifest, which is a yaml file that contains all the configuration information.
Yes - it's a lot. 


```bash
cat <<'EOF' > manifests/app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lets-ship-it
  namespace: fastapi
spec:
  replicas: 1
  selector:
    matchLabels:
      app: lets-ship-it
  template:
    metadata:
      labels:
        app: lets-ship-it
    spec:
      containers:
        - name: lets-ship-it
          image: lets-ship-it
          imagePullPolicy: Never
          ports:
            - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: lets-ship-it
  namespace: fastapi
spec:
  type: NodePort
  selector:
    app: lets-ship-it
  ports:
    - port: 8000
      targetPort: 8000
EOF
```

We are building two objects here
### Deployment 
This which will manage the running containers as Pods, including how many of them there are ("replicas").

`imagePullPolicy: Never` is important because it dictates whether to pull down a new docker image or not,
which is a common gotcha if you update the image but don't tell the Deployment to pull down the new image.
we are using the local image we loaded in this case.

### Service
A Service is a stable network endpoint for accessing your pods. Pods are ephemeral - this is really important - so they get new IPs when they restart or reschedule because they ARE new. So a Service gives you a fixed DNS name and IP that routes traffic to whatever pods match its
selector, regardless of how they come and go.

In your manifest, the Service watches for pods with app:lets-ship-it 
and forwards traffic on port 8000 to them.

type: NodePort also exposes it on a high port on the node itself, which is how you can reach it from outside the
cluster (or via kubectl port-forward).

# deploy the app

```bash
kubectl apply -f manifests/app.yaml -n fastapi

# check the two objects we made
kubectl get pods -n fastapi
kubectl get svc lets-ship-it -n fastapi

# set it up so we can check health
kubectl port-forward svc/lets-ship-it 8042:8000 -n fastapi

# in a separate terminal
curl http://localhost:8042/healthz
```

Here's what's happening behind the scenes:


1. `kubectl apply` sends your manifest to the API server.
2. The API server stores it in etcd.
3. Controllers (operators) are watching etcd for changes — the Deployment controller sees the new Deployment (which creates a ReplicaSet, the and the ReplicaSet controller creates Pods).
4. the scheduler assigns the Pod(s) to a node.
5. the kubelet on that node pulls the image and starts the container(s) in the Pod.

Each controller runs as its own goroutine inside `kube-controller-manager`, which is logically independent so you can think about them like OS processes even thought they're not.

Each controller only watches for its own resource type and reconciles desired state vs actual state.

`Watch` is an important concept. Controllers don't poll. They open a long-lived HTTP streaming connection to the API server (GET /api/v1/pods?watch=true). The API server pushes events down that connection whenever a resource changes — like ADDED, MODIFIED, DELETED.

The controller receives the event, compares desired state to actual state, and takes action if they differ. This is why k8s reacts quickly to changes without hammering the API server with requests.

# scale up to 2 replicas


## 1. Modify the manifest and re-apply:
change `replicas: 1` to `replicas: 2` in manifests/app.yaml,
then re-apply:
`kubectl apply -f manifests/app.yaml -n fastapi`

## 2. Edit in place (no file change):

`kubectl scale deployment lets-ship-it -n fastapi --replicas=2`
or what i more commonly do is:
`kubectl edit deployment lets-ship-it -n fastapi`

Which opens the live deployment spec in your $EDITOR. Change replicas, save and quit — k8s applies it immediately.

Note: option 2 creates drift — your manifest still says 1 but the cluster has 2. Next time you kubectl apply, it'll scale back down to 1.


# namespace gotchas

if we don't specify, we're running in the `default` namespace. we need to be sure we're specifying what namespace we're in by adding
--namespace

run
```bash
kubectl get namespaces
```

i use the `kubens` - part of the kubectx project (https://github.com/ahmetb/kubectx)
to not get confused.

```bash
brew install kubectx
alias kns=kubens

kns fastapi
```

note that i've actually changed this in the manifest itself.

```bash
kubectl apply -f manifests/app.yaml
```