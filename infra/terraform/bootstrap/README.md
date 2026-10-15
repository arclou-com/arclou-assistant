# bootstrap

Cria o que os outros ambientes precisam para existir (S0-03): projetos `arclou-stg` e `arclou-prd`, APIs, bucket do state (`arclou-prd-tfstate`, versionado) e o orçamento mensal da conta de billing (R$ 350, alertas em 50%, 90%, 100% e 100% previsto).

É o **único apply manual**. Os outros rodam pelo GitHub Actions (S0-09).

## Rodar
```bash
cp terraform.tfvars.example terraform.tfvars        # preencha org_id e billing_account (não vai para o git)
export GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token --account=<conta admin da org>)
terraform init
terraform plan
terraform apply
```
O `GOOGLE_OAUTH_ACCESS_TOKEN` evita depender do ADC (`gcloud auth application-default login`), que pode estar com outra conta. O token vale 1 hora.

## Do zero (primeira vez)
1. Comente o bloco de `backend.tf` (o bucket ainda não existe) e rode `terraform init && terraform apply`.
2. Descomente o `backend.tf` e rode `terraform init -migrate-state`.
3. `terraform plan` deve mostrar **No changes**.

## Pegadinhas
- Com `auto_create_network = false`, o provider apaga a rede `default` do projeto novo. Se a API do Compute ainda não estiver ativa, o apply falha e o projeto fica "tainted". Nesse caso: `terraform untaint 'google_project.this["stg"]'`, rode o apply de novo e apague a rede `default` que sobrou (`gcloud compute firewall-rules delete …` e `gcloud compute networks delete default`).
- Os projetos têm `deletion_policy = "PREVENT"`: um `destroy` não apaga projeto por engano.
- O `gcloud billing budgets list` precisa de `--billing-project=arclou-prd`.
