# Sprint 0 — Infra, Terraform, workflow e contrato de API

**Datas:** 19/10 – 30/10/2026 · **Pontos:** 40 (back/infra) + 13 (front)
**Objetivo:** repositório protegido, toda a infra criada por Terraform e um "hello world" da API e do web publicado em staging e production na VM pelo pipeline. Em paralelo, a **trilha de front** monta a base pixel perfect (tokens, componentes, layout e login) contra o mock do contrato.
**Referências:** [doc 12 — Ambientes e workflow](../12-ambientes-e-workflow.md) · [doc 04 — Arquitetura](../04-arquitetura.md) · [doc 05 — Backlog](../05-backlog-sprints.md)

Ordem sugerida (back/infra): S0-01 → S0-02 → S0-03 → (S0-06, S0-07, S0-04 → S0-05, S0-08) → S0-10 → S0-11 → S0-09 → S0-12 → S0-14 → S0-13.
Ordem sugerida (front): S0-10 (web) → S0-14 (mock + cliente) → S0-F01 → S0-F02 → S0-F03.

---

### S0-01 · Monorepo, pre-commit e Conventional Commits

**Contexto**
O repositório `arclou-com/arclou-assistant` hoje só tem `docs/` e `scripts/`. Antes de qualquer código, precisamos da estrutura do monorepo e das ferramentas que garantem a qualidade de cada commit, para que todo o trabalho seguinte já nasça no padrão.

**Escopo**
- Criar a estrutura de pastas de doc 04 §6: `backend/`, `web/`, `api/`, `infra/terraform/`, `infra/compose/`, `infra/caddy/`, `infra/scripts/`, cada uma com um `README.md` curto explicando o que vai nela.
- `.editorconfig`, `.gitattributes` (LF) e `.gitignore` completo (Python, Node, Terraform, `.env*`).
- `.pre-commit-config.yaml` com: `ruff` (lint + format), `mypy` (só em `backend/`), `eslint` e `prettier` (só em `web/`), `terraform_fmt` e `terraform_validate` (pre-commit-terraform), `gitleaks`, `check-yaml`, `end-of-file-fixer`, `trailing-whitespace` e `check-added-large-files` (500 KB).
- Conventional Commits com `commitlint` no hook `commit-msg`. Tipos: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `build`, `perf`. Escopos: `api`, `web`, `agent`, `infra`, `ci`, `docs`.
- `CONTRIBUTING.md`: como instalar o pre-commit, padrão de branch (`feature/S0-01-monorepo`), padrão de commit e de título de PR (`S0-01 feat: …`).
- `Makefile` na raiz com os alvos `setup`, `lint`, `test` e `fmt` (os que ainda não têm código só imprimem "n/a").

**Fora do escopo:** código da aplicação (S0-10), CI (S0-11).

**Critérios de aceite**
- [ ] Estrutura de pastas criada e documentada no README da raiz
- [ ] `pre-commit install && pre-commit run --all-files` passa num clone limpo
- [ ] Commit com mensagem fora do padrão (ex.: `ajustes`) é rejeitado pelo hook
- [ ] Um segredo de teste (ex.: `AKIA…` falso) num arquivo é bloqueado pelo gitleaks
- [ ] `CONTRIBUTING.md` explica o fluxo de ponta a ponta

**Testes / como validar**
1. Clonar o repo numa pasta nova, rodar `make setup` e depois `pre-commit run --all-files`: tudo verde.
2. `git commit -m "ajustes"` → rejeitado. `git commit -m "chore(ci): teste"` → aceito.
3. Criar `segredo.txt` com uma chave falsa → o commit é bloqueado.

**Dependências:** nenhuma.

---

### S0-02 · Proteção de branches, Environments e padrões do GitHub

**Contexto**
O fluxo combinado é `feature/* → PR → develop` (staging) e `develop → PR de release → main` (production). Ninguém faz push direto em `main` nem em `develop` (doc 12 §4).

> **Já feito em 15/10/2026:** o repo virou **público** (decisão do owner, para ter rulesets e Environments no plano Free). Os rulesets `protect-main` e `protect-develop` já bloqueiam push direto, force push e exclusão, e exigem PR (squash na `develop`). Os Environments `staging` (só `develop`) e `production` (só `main`, com aprovação do owner) já existem. **Falta:** os status checks obrigatórios (depois do S0-11), os templates, o CODEOWNERS e o CONTRIBUTING.
>
> Com o repo público, **nenhum segredo entra no código**: o gitleaks (S0-01 e S0-11) e o Secret Manager (S0-07) são obrigatórios.

**Escopo**
- **Ruleset `main`:** só via PR; status checks obrigatórios (`ci / backend`, `ci / web`, `ci / contract`, `terraform / plan`), branch atualizada antes do merge, merge commit permitido (release), sem force push e sem exclusão.
- **Ruleset `develop`:** só via PR, os mesmos checks, **só squash merge**, histórico linear, sem force push e sem exclusão.
- Aprovações: 0 enquanto o time tiver uma pessoa; 1 quando entrar a segunda (documentar no CONTRIBUTING).
- Environments: `staging` (deploy só a partir de `develop`) e `production` (deploy só a partir de `main`, **required reviewer** = owner, tempo de espera de 0 min).
- `.github/pull_request_template.md`: link da issue (`Closes #`), o que mudou, como testar, checklist da DoD, prints (quando for front).
- `.github/ISSUE_TEMPLATE/`: `task.yml` (contexto, escopo, critérios, testes), `bug.yml` (passos, esperado × obtido, ambiente) e `config.yml` (desliga issue em branco).
- `CODEOWNERS`: `* @arclouai`; `infra/` e `.github/` exigem o owner.
- Configurações do repo: apagar a branch depois do merge (já ativo), auto-merge (já ativo), desligar wiki e projects clássicos.

**Critérios de aceite**
- [ ] `git push origin main` (e `develop`) direto é **rejeitado**
- [ ] PR com check vermelho não pode ser mergeado
- [ ] PR para `develop` só mostra a opção squash
- [ ] Um deploy em `production` fica aguardando aprovação
- [ ] Templates de PR e de issue aparecem ao abrir um PR ou uma issue nova

**Testes / como validar**
1. Fazer um commit trivial em `main` local e dar `git push` → `GH013: Repository rule violations`.
2. Abrir um PR de teste com um check falhando de propósito → botão de merge bloqueado.
3. Disparar o workflow de deploy em `production` (S0-12) → status "Waiting for review".

**Dependências:** decisão do plano do GitHub. Os nomes dos checks obrigatórios são ajustados depois do S0-11.

---

### S0-03 · Terraform bootstrap: projetos, billing, APIs, state e orçamento

**Contexto**
Tudo na GCP é criado por Terraform. O bootstrap é a única parte aplicada manualmente (uma vez), com o seu login no terminal. Ele cria o que os outros módulos precisam para existir: projetos, APIs, bucket do state e alertas de custo.

**Escopo** (`infra/terraform/bootstrap/`)
- Providers `google` e `google-beta` com versões fixadas (`~> 6.x`), `required_version` do Terraform `>= 1.9`.
- Projetos `arclou-stg` e `arclou-prd` (se o ID estiver ocupado, usar o sufixo `-<4 dígitos>`, centralizado em `locals`), ligados à conta de billing via variável `billing_account`.
- APIs por projeto: `compute`, `iap`, `iam`, `iamcredentials`, `sts`, `cloudresourcemanager`, `serviceusage`, `secretmanager`, `artifactregistry`, `firestore`, `firebase`, `identitytoolkit`, `aiplatform`, `dns`, `monitoring`, `logging`, `storage`, `cloudbilling`, `billingbudgets`.
- Bucket `arclou-tfstate-<sufixo>` em `southamerica-east1`: versionamento ligado, `uniform_bucket_level_access`, `public_access_prevention = enforced`, lifecycle que mantém 20 versões antigas.
- Budget mensal na conta de billing (variável, padrão **US$ 60**), com alertas por e-mail em 50%, 90% e 100% (real) e 100% (previsto).
- Labels em tudo: `app=arclou`, `env=<stg|prd|shared>`, `managed_by=terraform`.
- Depois do primeiro apply, migrar o state do bootstrap para o próprio bucket (`backend "gcs"`, prefixo `bootstrap`).
- `README.md` da pasta com o passo a passo (login, `terraform init/plan/apply`, migração do state).

**Critérios de aceite**
- [ ] `terraform apply` do zero cria os 2 projetos com as APIs habilitadas
- [ ] O state está no GCS, versionado, e o lock funciona (dois `plan` simultâneos → o segundo espera)
- [ ] O budget aparece em Billing → Budgets com os 4 limites
- [ ] Um segundo `terraform plan` mostra **"No changes"**
- [ ] Nada criado à mão no console

**Testes / como validar**
1. `gcloud projects list` mostra os dois projetos. `gcloud services list --project arclou-stg` mostra as APIs.
2. `gsutil versioning get gs://arclou-tfstate-…` → `Enabled`.
3. Rodar `terraform plan` em dois terminais ao mesmo tempo → um deles mostra "Error acquiring the state lock".

**Dependências:** **P2** — você faz `gcloud auth login` e `gcloud auth application-default login` no terminal e informa o ID da conta de billing.

---

### S0-04 · Terraform da VM: rede, firewall, IP, disco de dados e Docker

**Contexto**
Uma VM do Compute Engine roda staging e production em Docker Compose (doc 12 §2). Os dados ficam num disco separado, para que recriar a VM nunca apague os bancos.

**Escopo** (`infra/terraform/modules/vm-host/` usado por `envs/shared/`)
- VPC `arclou-vpc` (modo custom) + subnet `southamerica-east1` (`10.10.0.0/24`).
- Firewall: `allow-web` (tcp 80/443 de `0.0.0.0/0`, tag `web`); `allow-iap-ssh` (tcp 22 só de `35.235.240.0/20`, tag `ssh-iap`); nenhuma outra regra de entrada.
- IP externo estático `arclou-vm-ip`.
- Service account `vm-host@arclou-prd` com papéis mínimos: `logging.logWriter`, `monitoring.metricWriter`, `artifactregistry.reader`, e `secretmanager.secretAccessor` + `datastore.user` + `aiplatform.user` **nos dois projetos**.
- VM `arclou-vm`: `e2-standard-2`, Ubuntu 24.04 LTS, boot de 30 GB `pd-balanced`, Shielded VM, OS Login ligado, metadata `block-project-ssh-keys = true`.
- Disco de dados `arclou-data` (50 GB `pd-balanced`) anexado como `data`, com política de **snapshot diário às 19h** (retenção de 7 dias).
- Startup script idempotente: formata o disco só se ele estiver vazio, monta em `/mnt/data` (fstab por UUID), instala Docker Engine + Compose plugin, cria `/opt/arclou/{edge,staging,production}` e configura o `gcloud` como credential helper do Artifact Registry.
- `deletion_protection = true` na VM e `prevent_destroy` no disco de dados.
- Outputs: IP, nome da VM e zona.

**Critérios de aceite**
- [ ] A VM sobe e o `docker info` funciona via `gcloud compute ssh arclou-vm --tunnel-through-iap`
- [ ] **SSH sem IAP falha** (porta 22 fechada para a internet)
- [ ] `/mnt/data` montado depois de reiniciar
- [ ] Recriar a VM (`terraform apply -replace=…vm`) mantém os arquivos de `/mnt/data`
- [ ] O snapshot diário aparece na política

**Testes / como validar**
1. `nc -vz <ip> 22` de fora → timeout. `curl http://<ip>` → conexão aceita (Caddy entra no S0-08).
2. Criar `/mnt/data/teste.txt`, recriar a VM com `-replace` e conferir que o arquivo continua lá.
3. `sudo reboot` → depois do boot, `df -h /mnt/data` mostra o disco.

**Dependências:** S0-03.

---

### S0-05 · Agenda de liga/desliga da VM e workflow manual

**Contexto**
Para gastar o mínimo, a VM só fica ligada no horário comercial. Fora dele, quem precisar liga pelo GitHub Actions.

**Escopo**
- `google_compute_resource_policy` `arclou-office-hours` com `instance_schedule_policy`: start `0 8 * * 1-5`, stop `0 20 * * 1-5`, `time_zone = "America/Sao_Paulo"`, anexada à VM.
- Conceder ao service agent do Compute (`service-<n>@compute-system.iam.gserviceaccount.com`) o papel `compute.instanceAdmin.v1` na VM (exigido pelo instance schedule).
- Variáveis `schedule_start`, `schedule_stop` e `schedule_enabled` (para desligar a agenda sem destruir a política).
- Workflow `.github/workflows/vm-power.yml` (`workflow_dispatch`, input `action: start|stop|status`), autenticado por WIF (S0-06), que roda `gcloud compute instances start|stop|describe` e escreve o resultado no summary do job.
- Seção no runbook (S0-13): como ligar fora do horário e quanto custa cada hora.

**Critérios de aceite**
- [ ] A VM desliga sozinha às 20h e liga às 08h (seg–sex), no horário de Brasília
- [ ] No sábado e no domingo ela fica desligada
- [ ] O workflow liga, desliga e mostra o status da VM
- [ ] `schedule_enabled = false` remove a agenda sem recriar a VM

**Testes / como validar**
1. Temporariamente, configurar o stop para daqui a 10 minutos → a VM vai para `TERMINATED`. Voltar ao valor normal.
2. Rodar o workflow com `start` → a VM fica `RUNNING` em menos de 2 minutos.
3. `gcloud compute resource-policies describe arclou-office-hours` mostra o cron e o fuso.

**Dependências:** S0-04, S0-06.

---

### S0-06 · Artifact Registry, service accounts e Workload Identity Federation

**Contexto**
O GitHub Actions precisa publicar imagens, aplicar o Terraform e fazer deploy **sem chave JSON**. A Workload Identity Federation troca o token OIDC do GitHub por credenciais de curta duração.

**Escopo**
- Artifact Registry `arclou` (Docker, `southamerica-east1`, no `arclou-prd`) com política de limpeza: manter as 10 versões mais recentes de cada imagem e apagar as não tagueadas com mais de 7 dias.
- Workload Identity Pool `github` + provider `github-oidc` (issuer `https://token.actions.githubusercontent.com`), com `attribute_condition` restrita a `assertion.repository == "arclou-com/arclou-assistant"`.
- Service accounts:
  - `gh-deployer`: `artifactregistry.writer`, `compute.instanceAdmin.v1` (só na VM), `iap.tunnelResourceAccessor`, `compute.osAdminLogin` (com OS Login) e `iam.serviceAccountUser` na SA da VM.
  - `gh-terraform`: papéis para gerenciar os recursos dos dois projetos e o bucket de state. `plan` em PR usa `gh-terraform-ro` (só leitura).
- Bindings `workloadIdentityUser`: `gh-deployer` só para as refs `refs/heads/develop` e `refs/heads/main`; `gh-terraform` (escrita) só para `main`/`develop`; `gh-terraform-ro` para qualquer PR do repo.
- Outputs (`workload_identity_provider` e e-mails das SAs) salvos como **Variables** do repo (não são segredos).

**Critérios de aceite**
- [ ] Um workflow de teste com `google-github-actions/auth@v2` autentica e roda `gcloud auth list`
- [ ] O mesmo workflow num **fork** ou em outro repo **não** consegue autenticar
- [ ] Um PR não consegue usar a SA de deploy
- [ ] Nenhuma chave de service account existe (`gcloud iam service-accounts keys list` só mostra chaves gerenciadas pelo Google)

**Testes / como validar**
1. Workflow `auth-smoke.yml` (manual) num branch → falha com `gh-deployer` e passa com `gh-terraform-ro`.
2. `docker push` de uma imagem `hello` pelo workflow → aparece no Artifact Registry.

**Dependências:** S0-03.

---

### S0-07 · Serviços gerenciados por ambiente: Firestore, Firebase Auth, Vertex e Secret Manager

**Contexto**
Cada ambiente tem o próprio projeto, então usuários, conversas e segredos de staging nunca se misturam com os de produção.

**Escopo** (`infra/terraform/modules/env-services/`, usado por `envs/staging` e `envs/production`)
- `google_firebase_project` (google-beta) ligando o Firebase ao projeto.
- Firebase Auth via Identity Platform (`google_identity_platform_config`) com os provedores **e-mail/senha** e **Google** habilitados. Domínios autorizados: `app.stg.arclou.com.br` / `app.arclou.com.br` e `localhost`.
- App Web do Firebase (`google_firebase_web_app`); a config pública (apiKey, authDomain, projectId) vai para o output e é usada no build do `web/`.
- Firestore `(default)`, modo Native, `southamerica-east1`, **TTL** no campo `expires_at` do grupo de coleções `messages`, PITR desligado em staging e ligado em production.
- Vertex AI: API habilitada (S0-03) e quota padrão; sem recurso extra.
- Secret Manager: só os **contêineres** dos segredos (sem valores): `meta-app-secret`, `meta-access-token`, `meta-verify-token`, `oauth-google-client-secret`, `crypto-master-key`, `sentry-dsn-api`, `langfuse-secret-key`, `postgres-password`, `redis-password`. Replicação em `southamerica-east1`.
- Script `infra/scripts/set-secret.sh <env> <nome>` que lê o valor do stdin e roda `gcloud secrets versions add` (o valor nunca passa pelo Terraform nem pelo histórico do shell).

**Critérios de aceite**
- [ ] Nos dois projetos: Firestore Native em SP com a política de TTL ativa
- [ ] Login por e-mail/senha e por Google habilitado no Firebase Auth de cada ambiente
- [ ] Os segredos existem e nenhum valor aparece no state (`terraform state pull | grep -i token` não retorna valor)
- [ ] O `set-secret.sh` cria uma versão nova e a VM consegue ler (`gcloud secrets versions access latest`)

**Testes / como validar**
1. `gcloud firestore fields ttls list --project arclou-stg` mostra `expires_at`.
2. Criar um usuário de teste no Firebase de staging → ele **não** aparece no de produção.
3. Na VM: `gcloud secrets versions access latest --secret meta-verify-token --project arclou-stg`.

**Dependências:** S0-03, S0-04 (para o teste de acesso pela VM).

---

### S0-08 · Cloud DNS, subdomínios e Caddy com TLS

**Contexto**
Quatro hosts apontam para a mesma VM, e o Caddy decide para qual ambiente cada requisição vai, emitindo os certificados sozinho.

**Escopo**
- Terraform `modules/dns`: zona `arclou-com-br` no Cloud DNS (projeto `arclou-prd`) e registros A (TTL 300) para `app`, `api`, `app.stg` e `api.stg` apontando para o IP estático. Output com os name servers.
- Delegar o domínio no registro.br para os name servers do Cloud DNS (passo manual, documentado).
- `infra/compose/edge.yml`: Caddy 2 (imagem fixada por digest), portas 80/443, volume `/mnt/data/caddy` (certificados) e rede Docker externa `edge`.
- `infra/caddy/Caddyfile`:
  - `api.arclou.com.br` → `arclou-prd-api:8000`; `app.arclou.com.br` → `arclou-prd-web:3000`
  - `api.stg.arclou.com.br` → `arclou-stg-api:8000`; `app.stg.arclou.com.br` → `arclou-stg-web:3000`
  - Headers de segurança (HSTS, `X-Content-Type-Options`, `Referrer-Policy`), compressão (gzip/zstd), log JSON e e-mail do ACME.
  - Staging com `X-Robots-Tag: noindex`.
  - Enquanto a app não existe, cada host responde com `respond "ok <host>" 200`.

**Critérios de aceite**
- [ ] `dig +short api.stg.arclou.com.br` retorna o IP da VM
- [ ] Os 4 hosts respondem em HTTPS com certificado válido (Let's Encrypt)
- [ ] HTTP redireciona para HTTPS
- [ ] Os certificados sobrevivem a um restart do Caddy e da VM (sem reemitir)

**Testes / como validar**
1. `curl -I https://app.stg.arclou.com.br` → `200` e `strict-transport-security` no header.
2. `curl -I http://api.arclou.com.br` → `308` para HTTPS.
3. `docker compose -f edge.yml restart` → os logs do Caddy não mostram nova emissão.

**Dependências:** S0-04, **P3** (domínio delegado; a propagação pode levar até 24 h, então começar cedo).

---

### S0-09 · Pipeline do Terraform (plan no PR, apply no merge)

**Contexto**
Mudança de infra passa pelo mesmo fluxo do código: o PR mostra o `plan`, e o `apply` só acontece depois do merge.

**Escopo** (`.github/workflows/terraform.yml`)
- Gatilho: PR e push que tocam em `infra/terraform/**`.
- Job `validate` (matriz `shared`, `staging`, `production`): `terraform fmt -check`, `init -backend=false`, `validate`, `tflint` (ruleset google) e `trivy config` (misconfig high/critical falha).
- Job `plan` no PR: autentica com `gh-terraform-ro`, roda `terraform plan -lock=false` por pasta e publica **um comentário** no PR (atualizado a cada push) com o resumo `+ ~ -` e o plan completo num `<details>`.
- Job `apply`:
  - push em `develop` → `envs/staging` (Environment `staging`)
  - push em `main` → `envs/shared` e `envs/production` (Environment `production`, **com aprovação**)
  - Sempre `plan -out` seguido de `apply` do mesmo arquivo.
- `concurrency` por ambiente (nunca dois applies juntos) e o state lock do GCS.
- Falha no apply notifica no summary do job e marca o deploy como falho.

**Critérios de aceite**
- [ ] PR que muda um label de recurso recebe o comentário do plan com `~ 1 to change`
- [ ] Código mal formatado ou inválido bloqueia o PR
- [ ] Merge em `develop` aplica só staging; merge em `main` espera aprovação e aplica shared + production
- [ ] Um apply em andamento bloqueia o seguinte (fila)

**Testes / como validar**
1. PR de teste mudando um label → comentário do plan aparece. Novo push → o mesmo comentário é atualizado (não duplica).
2. Merge → o job `apply staging` roda; `terraform plan` local depois mostra "No changes".

**Dependências:** S0-03, S0-06, S0-02 (Environments).

---

### S0-10 · Hello world da API e do web com Dockerfiles de produção

**Contexto**
Antes de construir as funcionalidades, validamos o caminho completo (build → registry → VM → HTTPS) com a aplicação mais simples possível, mas já com as imagens no formato final.

**Escopo**
- `backend/`: projeto `uv` (Python 3.12), FastAPI com `GET /health` → `{"status":"ok","version":"<git sha>","env":"<staging|production>"}`, Uvicorn, `pyproject.toml` com ruff/mypy/pytest configurados e um teste do `/health`.
- `backend/Dockerfile` multi-stage: builder com `uv sync --frozen`; runtime `python:3.12-slim`, usuário não root (uid 10001), `HEALTHCHECK`, `--proxy-headers`, porta 8000.
- `web/`: Next.js (App Router, TypeScript, `output: "standalone"`), página `/` com "Arclou" e o ambiente, rota `/api/health`, ESLint, Prettier, Vitest e um teste da página.
- `web/Dockerfile` multi-stage: `node:22-alpine`, `npm ci`, build standalone, runtime não root, porta 3000.
- Build args `GIT_SHA` e `APP_ENV` gravados na imagem (labels OCI `org.opencontainers.image.revision`).
- `.dockerignore` nos dois.

**Critérios de aceite**
- [ ] `docker build` dos dois funciona localmente
- [ ] Imagem da API < 300 MB e do web < 250 MB
- [ ] Os containers rodam como usuário não root
- [ ] `/health` e `/api/health` respondem 200 com versão e ambiente
- [ ] `pytest` e `vitest` passam

**Testes / como validar**
1. `docker run -p 8000:8000 arclou-api` → `curl localhost:8000/health`.
2. `docker run --rm arclou-api id -u` → `10001`.
3. `docker image ls` confere os tamanhos.

**Dependências:** S0-01.

---

### S0-11 · CI: lint, testes, build, scan e push das imagens

**Contexto**
Todo PR passa pelas mesmas verificações, e só imagens que passaram no CI chegam ao registry.

**Escopo** (`.github/workflows/ci.yml`)
- Gatilho: PR para `develop`/`main` e push nesses branches. Filtro por caminho (`backend/**`, `web/**`, `api/**`), mas com os jobs obrigatórios sempre reportando status (job "skip" quando nada mudou), para não travar o merge.
- Job `backend`: `uv sync`, `ruff check`, `ruff format --check`, `mypy`, `pytest` com cobertura (relatório como artefato).
- Job `web`: `npm ci`, `eslint`, `tsc --noEmit`, `vitest run`, `next build`.
- Job `contract` (entra no S0-14): Spectral no `api/openapi.yaml`.
- Job `images` (depois dos testes): `docker buildx` com cache do GitHub Actions, **Trivy** na imagem (falha em `HIGH`/`CRITICAL` com correção disponível) e, **só em push** para `develop`/`main`, autenticação por WIF e push para `southamerica-east1-docker.pkg.dev/arclou-prd/arclou/{api,web}:<sha>`.
- `gitleaks` no histórico do PR.
- `concurrency` cancelando execuções antigas do mesmo PR.
- Dependabot (`.github/dependabot.yml`) semanal para pip/uv, npm, Docker, GitHub Actions e Terraform.

**Critérios de aceite**
- [ ] PR com erro de lint, tipo ou teste fica vermelho e não pode ser mergeado
- [ ] Imagem com vulnerabilidade crítica corrigível falha o job
- [ ] Merge em `develop` publica `api:<sha>` e `web:<sha>` no Artifact Registry
- [ ] Um PR que só mexe em `docs/` passa sem rodar build (checks como "skipped/success")
- [ ] Tempo total do CI < 8 min com cache

**Testes / como validar**
1. PR com `x: int = "a"` no backend → mypy falha.
2. PR só com mudança em `docs/` → checks verdes em menos de 1 min.
3. Depois do merge, `gcloud artifacts docker images list …/arclou` mostra a tag do commit.

**Dependências:** S0-06, S0-10.

---

### S0-12 · CD: deploy na VM com migrations, health check e rollback

**Contexto**
O deploy precisa ser automático, repetível e seguro: liga a VM se ela estiver desligada, sobe a versão nova e volta para a anterior se algo der errado.

**Escopo**
- `infra/compose/base.yml` + `staging.yml` + `production.yml` (com project names `arclou-stg` e `arclou-prd`): serviços `api` e `web` na rede `edge`, `restart: unless-stopped`, limites de memória do doc 12 §2 e logs com rotação (`max-size 10m`, `max-file 3`). Postgres, Redis e worker entram no Sprint 1.
- `infra/scripts/deploy.sh <env> <tag>` (na VM):
  1. Lê os segredos do Secret Manager do projeto do ambiente e escreve `/opt/arclou/<env>/.env` (permissão 600).
  2. Grava a tag atual em `.previous_tag`.
  3. `docker compose pull` e `up -d` com `TAG=<tag>`.
  4. Health check (`/health` com até 30 tentativas de 2 s) checando se a **versão retornada é a nova**.
  5. Se falhar: `up -d` com a tag anterior, sai com erro e imprime os logs dos containers.
  6. `docker image prune` mantendo as 3 últimas tags.
- `.github/workflows/deploy.yml`: dispara depois do `ci` verde em push em `develop` (→ `staging`) e em `main` (→ `production`, com aprovação):
  - autentica por WIF (`gh-deployer`);
  - **se a VM estiver `TERMINATED`, liga e espera o SSH** (até 3 min);
  - copia `infra/compose` e `infra/scripts` (scp pelo IAP) e roda `deploy.sh`;
  - smoke test externo (`curl https://api.<env>/health` e `https://app.<env>/api/health`);
  - publica no summary a URL, a versão e a duração.
- `concurrency` por ambiente.
- Workflow manual `rollback.yml` (input `env` e `tag`).
- Ensinar o Caddy (S0-08) a apontar para os containers reais.

**Critérios de aceite**
- [ ] Merge em `develop` → `https://api.stg.arclou.com.br/health` mostra o sha novo em < 10 min
- [ ] Merge em `main` → espera aprovação e depois atualiza production
- [ ] Com a VM desligada, o deploy liga a VM e conclui
- [ ] Uma imagem com `/health` quebrado faz **rollback automático** e o job fica vermelho
- [ ] O `rollback.yml` volta para uma tag escolhida
- [ ] O `.env` nunca aparece nos logs do Actions

**Testes / como validar**
1. Deploy normal → conferir `version` no `/health` dos dois hosts.
2. Desligar a VM pelo `vm-power.yml` e fazer merge → o deploy liga a VM e conclui.
3. PR que faz o `/health` responder 500 → deploy em staging faz rollback, e o `/health` continua com o sha anterior.

**Dependências:** S0-04, S0-06, S0-07, S0-08, S0-11.

---

### S0-13 · Runbook inicial de operação

**Contexto**
Qualquer pessoa do time precisa conseguir operar o ambiente sem depender da memória de quem montou.

**Escopo** (`docs/runbook.md`)
- Mapa dos ambientes (hosts, projetos, VM, onde ficam os logs).
- Ligar/desligar a VM (workflow e `gcloud`), horários da agenda e custo por hora.
- Acesso SSH pelo IAP (`gcloud compute ssh arclou-vm --tunnel-through-iap --zone …`) e comandos úteis (`docker compose ps/logs` por ambiente).
- Deploy manual e rollback (workflow e `deploy.sh` direto na VM).
- Adicionar ou rotacionar um segredo (`set-secret.sh` + redeploy).
- Rodar o Terraform localmente (login, `init`, `plan`) e o que nunca fazer (`apply` local em production, mudança no console).
- Checklist de "VM não sobe" e "certificado não emite".

**Critérios de aceite**
- [ ] Cada procedimento tem os comandos exatos, testados
- [ ] Outra pessoa (ou o Claude numa sessão nova) consegue fazer um rollback só lendo o runbook

**Testes / como validar:** executar cada procedimento seguindo apenas o documento.

**Dependências:** S0-05, S0-12.

---

### S0-14 · Contrato de API: lint, mock server e cliente TypeScript

**Contexto**
O front será construído por completo contra o contrato antes de o backend existir (doc 05, "Contrato primeiro"). Por isso, o contrato precisa estar validado, servido como mock e convertido em tipos TypeScript.

**Escopo**
- `api/openapi.yaml` (OpenAPI 3.1, conteúdo do doc 13), dividido em arquivos por domínio se passar de ~2 mil linhas (`api/paths/*.yaml`, `api/schemas/*.yaml`) e empacotado com `redocly bundle`.
- `.spectral.yaml`: `spectral:oas` + regras próprias (todo `operationId` em camelCase, toda operação com `tags`, `summary` e exemplo de resposta 2xx, erros no formato `Problem` (RFC 9457), `security` em toda rota exceto as públicas, paginação por cursor nas listas).
- Mock com **Prism** (`stoplight/prism`) no `compose` de dev, na porta 4010, com exemplos dinâmicos e `--errors`; o header `Prefer: code=404` ou `Prefer: example=vazio` permite simular os estados das telas (vazio, erro, carregando).
- Cliente: `openapi-typescript` gera `web/src/lib/api/schema.d.ts` e `openapi-fetch` dá o cliente tipado. Script `npm run api:gen`.
- CI (job `contract`): Spectral; `api:gen` + `git diff --exit-code` (cliente desatualizado quebra o build); `oasdiff breaking` contra `develop` para avisar quebra de compatibilidade no comentário do PR.
- Documentação navegável com Redoc gerada como artefato do CI.

**Critérios de aceite**
- [ ] `npx spectral lint api/openapi.yaml` sem erros
- [ ] `docker compose up mock` responde a todas as rotas com os exemplos do contrato
- [ ] O `web/` compila usando os tipos gerados; mudar um campo no contrato sem regenerar quebra o CI
- [ ] Uma mudança incompatível (remover campo obrigatório) aparece como "breaking" no PR

**Testes / como validar**
1. `curl localhost:4010/v1/me -H "Authorization: Bearer x"` → exemplo do contrato.
2. `curl … -H "Prefer: code=401"` → `Problem` de erro.
3. Remover um campo do schema sem rodar `api:gen` → o job `contract` falha.

**Dependências:** S0-01, S0-11 e o **doc 13** (contrato), escrito antes do início da sprint.

---

### S0-F01 · Base do front: tokens do Figma, tipografia e componentes primitivos

**Contexto**
O front precisa ficar **pixel perfect** com o Figma (DoD). Tudo parte da biblioteca "Componentes · Painel Web" (node `53:2` do arquivo `PJ7SvIZo5iVL4GqUoT0xAi`), que já usa **variáveis semânticas** com modos Dark e Light. Se os tokens e os primitivos saírem certos aqui, todas as telas das próximas sprints só compõem peças prontas.

**Escopo**
- **Stack de UI:** Tailwind CSS v4 com os tokens como CSS variables; Radix UI para comportamento acessível (Dialog, DropdownMenu, Switch, Checkbox, Toast, Tabs) estilizado com os tokens; `lucide-react` para os ícones (os nomes do Figma `Icon/*` já seguem o Lucide).
- **Tokens** (`web/src/styles/tokens.css`), exportados das variáveis do Figma nos dois modos (`[data-theme="dark"]` e `[data-theme="light"]`):
  - cores: `--bg-canvas`, `--bg-canvas-deep`, `--bg-nav`, `--bg-card`, `--bg-overlay`, `--text-primary|secondary|soft|detail|disabled|link|nav|on-action|hero-label`, `--icon-*`, `--border-field|focus|subtle|item|selected`, `--action-primary|disabled`, `--status-{success,error,warning,info}-{fg,bg}`, `--finance-committed`;
  - espaçamento `--space-2…32`, raios `--radius-sm|md|lg|pill`, tamanhos `--size-control-sm|md`, `--size-avatar`, `--stroke-width`;
  - elevação `Elevation/2` (sombra 0 16 40 #00000066);
  - tipografia Roboto (via `next/font`): Display 45/700, Title 23, Section 20, Body 16, Body Strong 16/600, Action 16/600, Caption 14, Caption Strong 14/600, Micro 12, Micro Strong 12/600.
- Script `npm run tokens:sync` que lê as variáveis do Figma (API REST com token pessoal no `.env.local`, nunca no repo) e regenera o `tokens.css`. O arquivo gerado é commitado.
- **Tema:** `ThemeProvider` (light/dark/system) persistido em `localStorage` e sincronizado com `preferences.theme` (`updateMe`), sem flash ao carregar (script inline no `<head>`). Componentes `Web/ThemeToggle` e `Web/ThemeIconButton`.
- **Primitivos** (`web/src/components/ui/`), cada um com todas as variantes da biblioteca:
  - `Button` (primary, secondary, link, ghost) e `Web/ButtonLoading`;
  - `Web/TextField` (Default, Focus, Error, Disabled; com label, ajuda e erro) e máscara de dinheiro (R$, digita centavos);
  - `Web/Checkbox` (Checked, Unchecked, Error), `Web/Toggle` (On/Off), `SegmentedControl`;
  - `Badge`, `Avatar` (iniciais, 47 px), `Web/Skeleton` (Line, Title, Block, Circle);
  - `Web/Toast` (Success, Error, Info, Loading) e `Web/Banner` (Warning, Error, Info);
  - `Modal` (desktop) e `Sheet` (mobile 430), com scrim; `Menu ⋯` (DropdownMenu) e action sheet no mobile.
- Os componentes de domínio (IntegrationCard, PlanCard, OrderSummary, CheckoutSteps, BankCard, StepItem, SettingRow) entram junto com as telas que os usam.
- **Storybook 8** com uma story por variante, nos dois temas.
- **Teste visual:** Playwright tira screenshot de cada story e compara com o PNG exportado do mesmo componente no Figma (`tests/visual/figma/*.png`, gerados por `npm run figma:export`). Tolerância: **≤ 1% de pixels diferentes**.
- Vitest + Testing Library para comportamento (foco, teclado, estados de erro, `aria-*`).

**Fora do escopo:** telas (S0-F02 em diante), componentes de domínio.

**Critérios de aceite**
- [ ] `tokens.css` gerado das variáveis do Figma, com os modos Dark e Light
- [ ] Todos os primitivos listados existem com todas as variantes da biblioteca, em Dark e Light
- [ ] Teste visual de cada variante passa com diferença ≤ 1% em relação ao Figma
- [ ] Navegação só por teclado funciona (Tab, Enter, Esc no modal/menu) e o foco usa `--border-focus`
- [ ] Trocar o tema não pisca a tela no carregamento
- [ ] Storybook publicado como artefato do CI

**Testes / como validar**
1. `npm run storybook` → comparar cada story com o componente no Figma, nos dois temas.
2. `npm run test:visual` → relatório do Playwright com o diff de cada variante.
3. `npm test` → testes de comportamento verdes.

**Dependências:** S0-10 (Next.js criado), S0-14 (cliente gerado).

---

### S0-F02 · Layout do painel, navegação e estados de tela

**Contexto**
Todas as telas do painel compartilham a mesma moldura: sidebar fixa no desktop e barra superior + tab bar no mobile. Os frames do Figma têm 1920 × 1080 com rolagem vertical (sidebar fixa, conteúdo rola) e 430 de largura no mobile.

**Escopo**
- `Web/Sidebar` (264 px, fixa) com `Web/SidebarItem` (Active/Default) na ordem do Figma: Visão geral, Finanças, Casa, WhatsApp, Integrações, Perfil e preferências, Assinatura, Privacidade e dados, Central de ajuda. No rodapé: card "Fale com a Arclou", `ThemeToggle` e o usuário (avatar, nome, e-mail, sair).
- O item "Casa" aparece conforme `getHousehold` / plano (sem Casa e sem plano Casal → leva para H02).
- Mobile (< 1024 px): `Web/MobileTopBar` + `Web/MobileTabBar` com os destinos das telas M*.
- Rotas do App Router com o layout e páginas-esqueleto para todas as telas do painel (`/visao-geral`, `/financas/*`, `/casa/*`, `/whatsapp`, `/integracoes`, `/perfil`, `/assinatura`, `/privacidade`), cada uma com o cabeçalho (título + subtítulo) do Figma.
- Abas de Finanças (Visão do mês, Limites e receitas, Compromissos, Parcelamentos, Planejamento e metas) como sub-rotas.
- **Estados** (linha "Estados no Dark"): carregando (Skeleton), vazio, erro com "tentar de novo" (Banner) e sem conexão. Um componente `PageState` padroniza isso para todas as telas.
- Camada de dados: TanStack Query sobre o cliente gerado (`openapi-fetch`), com tratamento padrão de `Problem` (401 → login, 403 `plan_required` → upsell, 422 → erros nos campos).
- Breakpoints: desktop ≥ 1280 (referência 1920), tablet 1024–1279, mobile ≤ 430 (referência 430).

**Critérios de aceite**
- [ ] Sidebar e tab bar iguais ao Figma (teste visual ≤ 1%) nos dois temas
- [ ] No desktop, a sidebar fica fixa e só o conteúdo rola
- [ ] Todas as rotas do painel existem e mostram o cabeçalho correto
- [ ] Os 4 estados aparecem ao forçar o mock (`Prefer: code=500`, latência, lista vazia, offline)
- [ ] Item ativo da navegação correto em todas as rotas

**Testes / como validar**
1. Playwright navega por todas as rotas, em 1920 × 1080 e em 430 × 932, e compara com os frames do Figma.
2. Forçar `Prefer: code=500` no mock → Banner de erro com "tentar de novo".

**Dependências:** S0-F01.

---

### S0-F03 · Login, cadastro com Firebase Auth e rotas protegidas

**Contexto**
O painel só abre para quem está logado. O login (tela "01 · Login") e a criação de conta (C02) usam o Firebase Auth (e-mail/senha e Google). A API recebe o ID token no `Authorization`.

**Escopo**
- Telas pixel perfect: "01 · Login" (Entrar, Continuar com Google, Esqueci minha senha, "Conheça os planos") e o formulário de C02 "Crie sua conta" (Criar com Google, nome, e-mail, senha, aceite dos termos).
- Firebase Web SDK configurado por ambiente (`NEXT_PUBLIC_FIREBASE_*` do output do S0-07). Em dev, o **Firebase Auth Emulator** (no compose de dev) para não depender do projeto real.
- Recuperação de senha (e-mail do Firebase) e mensagens de erro em pt-BR (senha fraca, e-mail em uso, credencial inválida, muitas tentativas).
- Middleware/guard: rotas do painel exigem sessão; sem sessão → `/entrar?next=…`. Logado em `/entrar` → painel.
- O cliente da API injeta o ID token e o renova quando expira (`onIdTokenChanged`). Um 401 da API faz logout.
- Depois do login: `getMe`. Se o usuário não tem plano (`plan = null`), vai para a escolha de plano (checkout, Sprint 1).
- Aceite dos termos via `recordConsent`.
- Logout no rodapé da sidebar.

**Critérios de aceite**
- [ ] Login e cadastro por e-mail/senha e por Google funcionam (emulador em dev, Firebase de staging no ambiente)
- [ ] Sem sessão, qualquer rota do painel redireciona para o login e volta para a rota original depois
- [ ] Token expirado é renovado sem o usuário perceber
- [ ] Erros do Firebase aparecem em pt-BR no campo certo
- [ ] Telas iguais ao Figma (teste visual ≤ 1%), Dark e Light, desktop e mobile

**Testes / como validar**
1. Playwright com o emulador: cadastro → login → painel → logout → login de novo.
2. Acessar `/financas` deslogado → redireciona e volta depois do login.
3. Forçar a expiração do token no emulador → a próxima chamada renova o token.

**Dependências:** S0-F02. Em staging, S0-07 (Firebase Auth do ambiente).
