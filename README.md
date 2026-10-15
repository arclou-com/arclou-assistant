# Personal Assistant (SaaS via WhatsApp)

Assistente pessoal por assinatura que controla **gastos, agenda e e-mails** do usuário, com interação pelo WhatsApp.

## Documentação de planejamento
| Doc | Conteúdo |
|---|---|
| [01 — Análise de mercado WhatsApp](docs/01-analise-mercado-whatsapp.md) | Número único × número do usuário, custos, **política de IA da Meta**, restrições do Gmail |
| [02 — Requisitos](docs/02-requisitos.md) | Atores, RF e RNF priorizados |
| [03 — Regras de negócio](docs/03-regras-de-negocio.md) | Vínculo, assinatura, quotas, agente, gastos, agenda, e-mail, LGPD |
| [04 — Arquitetura](docs/04-arquitetura.md) | Stack, componentes, fluxo, agente LangGraph, modelo de dados, estrutura do repo |
| [05 — Backlog e sprints](docs/05-backlog-sprints.md) | Pré-requisitos, calendário, Sprints 0–15 com critérios de aceite, estratégia de testes |
| [06 — Custo de IA](docs/06-custos-ia.md) | Modelos escolhidos, premissas de tokens e custo de IA por usuário/mês (`scripts/custos_ia.py`) |
| [07 — Infra e custo total](docs/07-custos-infra.md) | VPS atual, capacidade do Whisper, custos fixos por escala, margem por plano (`scripts/custos_infra.py`) |
| [08 — Finanças: conversas de referência](docs/08-financas-conversas.md) | Comportamento esperado da assistente em gastos, limites, receitas, metas e orientações (base dos evals) |
| [09 — Cartões visuais](docs/09-cartoes-visual.md) | Modelo Arclou de cartão: 13 cores, cor-padrão por banco, personalização e regras (sem logos) |
| [10 — Plano Casal e a Casa](docs/10-plano-casal.md) | Guia completo de finanças a dois: 3 modos (Dinheiro junto com conta conjunta, Separado, Misto), gavetas, divisão, quem deve quem, privacidade, convite e saída |
| [11 — Central de Ajuda](docs/11-central-de-ajuda.md) | Documentação para o cliente (estilo Google Cloud): pontos de entrada, estrutura, mapa artigo × regra, guia de estilo e **regra de manutenção** |
| [12 — Ambientes e workflow](docs/12-ambientes-e-workflow.md) | Staging e production numa VM do GCE com agenda de liga/desliga, Terraform, branches protegidas, GitHub Project e pipelines |
| [13 — Contrato da API](docs/13-contrato-api.md) | Convenções, mapa tela → endpoint, fluxos e mock do `api/openapi.yaml` (OpenAPI 3.1) |
| [Sprints](docs/sprints/) | Especificação detalhada de cada sprint (contexto, escopo, critérios de aceite e testes por task). É a fonte do corpo das issues (`scripts/github_backlog.py --sprint N`) |

## Estrutura do monorepo
```
api/            contrato OpenAPI 3.1 (doc 13): fonte do mock e do cliente TS
backend/        FastAPI + worker arq (Python 3.12, hexagonal)
web/            Next.js: página de vendas, checkout, painel e Central de Ajuda
infra/
  terraform/    toda a GCP (bootstrap, modules, envs)
  compose/      Docker Compose de dev, staging, production e edge (Caddy)
  caddy/        Caddyfile
  scripts/      deploy, segredos e backup
docs/           planejamento (01–13) e especificação de cada sprint
scripts/        utilitários (custos, sync do backlog com o GitHub)
```

Para começar: `make setup` e leia o [CONTRIBUTING](CONTRIBUTING.md).

## Stack
Python 3.12 · FastAPI · LangGraph/LangChain · Vertex AI (Gemini) · PostgreSQL + pgvector · Firestore · Redis + arq · Firebase Auth · WhatsApp Cloud API · Next.js · Docker · Caddy · VM no GCE · Terraform · GitHub Actions

## Regra de documentação
Toda alteração em algo documentado (regra, preço, quota, fluxo ou tela) atualiza também a **Central de Ajuda** no mesmo trabalho: o artigo na página "Central de Ajuda · Docs" do Figma e o mapa em `docs/11-central-de-ajuda.md` §2.
