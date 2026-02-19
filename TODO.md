# TODO

## Underlying helper tech
- add copyediting and ai-slop
- improve the narrative 


## Blog Posts

- Blog post on `sed 's/[[:space:]]*$//'` vs slash command — stripping trailing whitespace from files
- Tonic.ai examples
- Why I built the repo this way
- How the tech helpers work


## Draft of Chapters - likely out of date with reality

| #  | Chapter                | What works after this                                          | NOTES sections     |
|----|------------------------|----------------------------------------------------------------|--------------------|
| 00 | Simple HTTP API        | `/healthz` endpoint, pytest passing                            |                    |
| 01 | Docker                 | App containerized, runs with `docker run`                      |                    |
| 02 | KIND Cluster           | Local k8s running, kubectl works                               |                    |
| 03 | Deploy with Manifests  | API running in cluster, port-forward to test                   |                    |
| 04 | K8s Architecture       | Understand control plane, watch, reconcile loops               | §1, §4             |
| 05 | K8s Networking         | CoreDNS, Services deep dive, traffic path                      | §2, §14            |
| 06 | Helm Chart             | `helm install job-dashboard ./charts/job-dashboard` works      | §15                |
| 07 | Jobs Can Be Created    | POST `/jobs` creates a k8s Job, GET `/jobs` lists them         |                    |
| 08 | Job Output Streaming   | GET `/jobs/{id}/logs` streams stdout                           |                    |
| 09 | Kopf Operator          | Operator watches Jobs, updates dashboard state (CRD)           | §4                 |
| 10 | Add State (PG/Redis)   | Jobs persist, survive API restart                              | §8                 |
| 11 | ConfigMaps & Secrets   | App config externalized, secrets not hardcoded                 | §6, §7             |
| 12 | gRPC API               | Same functionality, gRPC interface alongside HTTP              |                    |
| 13 | mTLS & Certs           | Secure connection between client and API                       | §10, §11           |
| 14 | Logging + Monitoring   | Prometheus metrics, structured logs, Grafana                   | §16, §17           |
| 15 | Flux                   | GitOps deployment, changes via PR                              | §19                |
| 16 | Flagger                | Canary deploys for the dashboard                               |                    |
| 17 | Autoscaling            | HPA based on job queue depth or requests                       | §18                |
| 18 | RBAC                   | Users can only see/manage their own jobs                       | §5                 |
| 19 | Secrets with AWS       | Credentials from Secrets Manager, ESO                          | §7                 |
| 20 | Image Registry         | ECR/Harbor, Trivy scanning, Cosign signing                     | §12                |
| 21 | Admission Webhooks     | Policy enforcement before pods start                           | §3                 |
| 22 | Terraform              | Cluster infra as code                                          | §13                |
| 23 | Go Operator            | Rewrite Kopf operator in Go with kubebuilder                   | §4                 |
| 24 | Failure Mode Analysis  | Runbook covering failure scenarios                             |                    |
