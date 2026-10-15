# infra/compose/

Arquivos do Docker Compose (doc 12 §2).

- `dev.yml`: ambiente local (api, worker, postgres+pgvector, redis, firestore-emulator, mock da API) → S1-02 e S0-14
- `base.yml` + `staging.yml` / `production.yml`: ambientes na VM (projetos `arclou-stg` e `arclou-prd`) → S0-12
- `edge.yml`: Caddy com TLS automático, compartilhado pelos dois ambientes → S0-08
