# 12 — Ambientes, infraestrutura e workflow

> Decisão de 15/10/2026. Substitui a VPS Hostinger da V1 (docs 04 e 07). Tudo o que existe na GCP é criado por **Terraform**: nada é criado à mão no console.

## 1. Ambientes

| | Staging | Production |
|---|---|---|
| Branch | `develop` | `main` |
| Deploy | Automático no merge | No merge, **com aprovação** no GitHub Environment `production` |
| Projeto GCP (serviços gerenciados) | `arclou-stg` | `arclou-prd` |
| Web | `app.stg.arclou.com.br` | `app.arclou.com.br` |
| API | `api.stg.arclou.com.br` | `api.arclou.com.br` |
| WhatsApp | Número de teste da Meta | Número dedicado (P1) |
| Firebase Auth, Firestore, Secret Manager, Vertex AI | Do projeto de staging | Do projeto de production |
| Postgres + Redis | Containers próprios na VM | Containers próprios na VM |

Cada ambiente tem seu projeto GCP, então usuários, dados e segredos nunca se misturam.

## 2. A VM (fase de desenvolvimento)

Uma única VM do Compute Engine roda os **dois ambientes em Docker Compose**.

| Item | Valor |
|---|---|
| Projeto / região | `arclou-prd` · `southamerica-east1` (São Paulo) |
| Máquina | `e2-standard-2` (2 vCPU, 8 GB) · Ubuntu 24.04 LTS |
| Discos | Boot de 30 GB + **disco de dados de 50 GB** (`/mnt/data`) com snapshot diário. Recriar a VM não apaga os dados |
| Rede | IP estático. Firewall: 80/443 abertas; 22 **só pelo IAP** (sem SSH público) |
| Identidade | Service account própria, com acesso só ao que os dois ambientes usam |
| Agenda | **Liga 08h e desliga 20h, de segunda a sexta** (`America/Sao_Paulo`), via *instance schedule* do Terraform. Fim de semana fica desligada |
| Fora do horário | Workflow manual "VM: ligar/desligar" no Actions. O deploy liga a VM sozinho se ela estiver desligada |

### Layout dentro da VM
```
/opt/arclou/
├── edge/compose.yml            # Caddy (TLS automático) — roteia os 4 hosts
├── staging/compose.yml + .env  # api, worker, web, postgres, redis  (projeto compose "arclou-stg")
└── production/compose.yml + .env  # idem                             (projeto compose "arclou-prd")
/mnt/data/{staging,production}/{postgres,redis}   # volumes no disco de dados
```

| Serviço por ambiente | RAM (limite) staging | RAM (limite) production |
|---|---|---|
| API (FastAPI) | 300 MB | 400 MB |
| Worker (arq) | 300 MB | 500 MB |
| Web (Next.js standalone) | 250 MB | 300 MB |
| Postgres 16 + pgvector | 512 MB | 1 GB |
| Redis 7 | 100 MB | 150 MB |
| **Subtotal** | **~1,5 GB** | **~2,4 GB** |

Somando Caddy e o sistema, sobram ~3 GB de folga.

### Custo estimado (confirmar na calculadora da GCP)
| Item | Por mês |
|---|---|
| `e2-standard-2` em SP, ~240 h (11 h × 22 dias úteis) | ~US$ 25 |
| Discos (80 GB pd-balanced) + snapshots | ~US$ 12 |
| IP estático (cobrado também com a VM parada) | ~US$ 3 |
| Cloud DNS, Artifact Registry, Secret Manager, backups no GCS | ~US$ 2 |
| Firestore, Firebase Auth, Vertex (dev) | ~US$ 0–5 |
| **Total** | **~US$ 45/mês (~R$ 250)** |

> A agenda corta ~67% do custo da máquina, que custaria ~US$ 75/mês ligada 24/7.

### Limites desta fase (aceitos)
- **Fora do horário nada responde:** webhooks da Meta (a Meta tenta de novo por até 7 dias), crons e lembretes. Em desenvolvimento, isso é aceitável.
- Staging e production dividem a máquina e a service account. Isso fica resolvido no **S14-01**: antes do beta, production ganha uma VM própria, ligada 24/7, e só staging continua desligando à noite.
- Backups e evals noturnos rodam **dentro do horário** (backup às 19h30, evals às 19h).

## 3. Terraform

```
infra/terraform/
├── bootstrap/          # projetos, billing, APIs, bucket de state, budgets, WIF do GitHub (apply manual, 1x)
├── modules/
│   ├── env-services/   # Firestore + TTL, Firebase Auth, Secret Manager, SA, Vertex
│   ├── vm-host/        # VPC, firewall, IP, VM, disco de dados, snapshot e instance schedule
│   ├── dns/            # zona e registros
│   └── registry/       # Artifact Registry + política de limpeza (mantém 10 imagens)
└── envs/
    ├── shared/         # VM, DNS, registry (vivem em arclou-prd)
    ├── staging/        # env-services de arclou-stg
    └── production/     # env-services de arclou-prd
```

- **State** remoto no GCS (`gs://arclou-prd-tfstate`, versionado), um prefixo por pasta (`bootstrap`, `shared`, `staging`, `production`).
- **Primeiro apply:** você faz o login no terminal (`gcloud auth login` e `gcloud auth application-default login`) e eu rodo o `bootstrap/`. Depois disso, o GitHub Actions faz os applies via **Workload Identity Federation**, sem chave JSON.
- Segredos (token da Meta, chaves) entram no Secret Manager por `gcloud secrets versions add`, nunca no código nem no state.

## 4. Git, PRs e GitHub Project

### Repositório
O repositório `arclou-com/arclou-assistant` é **público**: no plano Free, é o que libera rulesets e Environments com aprovação. Por isso, nenhum segredo entra no código, e o gitleaks roda no pre-commit e no CI.

### Branches
```
feature/S2-07-vinculo-whatsapp ─┐
fix/...                          ├─ PR → develop ── deploy staging (auto)
chore/...                       ─┘
develop ── PR de release → main ── deploy production (aprovação)
hotfix/... ── PR → main, depois merge de volta em develop
```
- **Proteção de `main` e `develop`:** merge só por PR, checks do CI obrigatórios, branch atualizada antes do merge, histórico linear (squash na `develop`, merge commit no release), sem force push e sem exclusão. Se o time tiver uma pessoa só, o PR fica obrigatório com 0 aprovações; a partir de duas pessoas, passa a exigir 1 aprovação.
- **Branch padrão:** `develop`. Assim, `Closes #123` fecha a issue quando ela chega em staging.
- **Commits:** Conventional Commits (`feat(api): …`, `fix(web): …`, `chore(infra): …`). Título do PR = `S2-07 feat: vínculo do WhatsApp`.
- **Release:** a cada sprint (ou antes), PR `develop → main` com tag `vAAAA.MM.DD` e notas geradas.

### GitHub Project "Arclou Assistant"
| Campo | Tipo | Valores |
|---|---|---|
| Status | Seleção | Backlog · Todo · In Progress · In Review · Done |
| Sprint | Iteração (2 semanas, início 19/10/2026) | Sprint 0 … Sprint 15 |
| Pontos | Número | 1, 2, 3, 5, 8 |
| Área | Seleção | infra · devops · backend · agent · frontend · docs |
| Prioridade | Seleção | P0 · P1 · P2 |

- **Issues:** uma por linha do doc 05 (título `S2-07 · Vínculo do WhatsApp`) com o critério de aceite como checklist. Cada sprint tem uma **issue-épico** com as tasks como sub-issues.
- **Uma sprint por vez:** as issues de uma sprint só são criadas no planejamento dela, com `python3 scripts/github_backlog.py --sprint N`. Até lá, o backlog futuro fica no doc 05, onde é barato de ajustar.
- **Views:** *View 1* (tabela) e *View 3* (board por Status). No board, use o filtro `sprint:@current` para ver a sprint atual.
- **Automação:** issue entra como Backlog. Quando o PR é aberto, vai para In Review. Com o merge, vai para Done.

## 5. Pipelines (GitHub Actions)

| Workflow | Gatilho | O que faz |
|---|---|---|
| `ci.yml` | PR e push | Lint, type-check e testes do back e do front, Spectral no contrato, build das imagens, Trivy |
| `terraform.yml` | PR com mudança em `infra/` | fmt, validate, tflint e `plan` comentado no PR. `apply` no merge (production com aprovação) |
| `deploy.yml` | Push em `develop`/`main` | Push no Artifact Registry → liga a VM se estiver parada → SSH pelo IAP → `deploy.sh <env> <tag>` (segredos → `.env`, pull, `alembic upgrade`, `up -d`, health check, rollback automático) → smoke Playwright |
| `vm-power.yml` | Manual | Liga ou desliga a VM |
| `evals.yml` | Agendado 19h, seg–sex | Evals com modelo real em staging |
