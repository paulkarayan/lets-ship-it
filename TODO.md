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

| #  | Chapter                | What works after this                                          |
|----|------------------------|----------------------------------------------------------------|
| 00 | Simple HTTP API        | `/healthz` endpoint, pytest passing                            |
| 01 | KIND Cluster           | Local k8s running, kubectl works                               |
| 02 | Deploy with Manifests  | API running in cluster, port-forward to test                   |
| 03 | Helm Chart             | `helm install job-dashboard ./charts/job-dashboard` works      |
| 04 | Jobs Can Be Created    | POST `/jobs` creates a k8s Job, GET `/jobs` lists them         |
| 05 | Job Output Streaming   | GET `/jobs/{id}/logs` streams stdout                           |
| 06 | Kopf Operator          | Operator watches Jobs, updates dashboard state (CRD)           |
| 07 | Add State (PG/Redis)   | Jobs persist, survive API restart                              |
| 08 | gRPC API               | Same functionality, gRPC interface alongside HTTP              |
| 09 | mTLS                   | Secure connection between client and API                       |
| 10 | Logging + Monitoring   | Prometheus metrics, structured logs, maybe Grafana             |
| 11 | Flux                   | GitOps deployment, changes via PR                              |
| 12 | Flagger                | Canary deploys for the dashboard                               |
| 13 | Autoscaling            | HPA based on job queue depth or requests                       |
| 14 | RBAC                   | Users can only see/manage their own jobs                       |
| 15 | Secrets with AWS       | Credentials from Secrets Manager or Parameter Store            |
| 16 | Go Operator            | Rewrite Kopf operator in Go with kubebuilder                   |
| 17 | Failure Mode Analysis  | Runbook covering failure scenarios                             |
