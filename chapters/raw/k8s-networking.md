 k8s-networking.md — mix of description AND hands-on:
  - Can poke at: CoreDNS — exec into a pod, nslookup
  lets-ship-it.fastapi.svc.cluster.local. Service discovery
  is live in your cluster right now
  - Can poke at: kubectl get endpoints / kubectl get
  endpointslices — see the actual pod IPs behind your Service
  - Can poke at: kubectl exec into a pod, curl another pod by
   Service name vs pod IP — show why Services matter
  - Can poke at: different Service types — change NodePort to
   ClusterIP, see what breaks
  - Describe only: Ingress / Gateway API — kind supports
  ingress-nginx but it's a lot of setup for a chapter. Maybe
  just explain the concept and say "we'll use this when we
  need external traffic"
  - Describe only: eBPF/Cilium (NOTES §2) — too deep for this
   stage, but good to mention as "what's actually happening
  under kube-proxy"
  - Describe only: full traffic path (DNS → LB → ingress →
  Service → iptables → pod)