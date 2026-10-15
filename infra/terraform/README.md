# infra/terraform/

Toda a infraestrutura na GCP (doc 12 §3). Nada é criado à mão no console.

```
bootstrap/   projetos, billing, APIs, bucket de state, budgets, WIF (apply manual, 1x)   → S0-03
modules/     env-services, vm-host, dns, registry                                        → S0-04 a S0-08
envs/        shared, staging, production (state no GCS, um prefixo por pasta)
```
