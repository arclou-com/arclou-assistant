# infra/scripts/

Scripts de operação executados na VM ou pelo pipeline:

- `deploy.sh <env> <tag>`: segredos → `.env`, pull, migrate, up, health check e rollback (S0-12)
- `set-secret.sh <env> <nome>`: grava uma versão nova de um segredo no Secret Manager (S0-07)
- `backup.sh` / `restore.sh`: Postgres → GCS (S1-08)
