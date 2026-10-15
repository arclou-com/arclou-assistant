# 05 — Backlog, sprints e estratégia de testes

> Revisão de 15/10/2026: a infra sai da VPS Hostinger e vai para **uma VM no GCE** que roda staging e production em Docker, provisionada com **Terraform** e desligada fora do horário comercial (doc 12). As telas do Figma estão prontas, então o front entra junto com cada funcionalidade. As antigas sprints 3b e 3c viraram sprints de 2 semanas.

Sprints de **2 semanas**, de segunda a sexta, começando em **19/10/2026**. Estimativa em pontos (1, 2, 3, 5, 8). Duas trilhas em paralelo: **back/infra (~30 pontos por sprint)** e **front (~15 pontos por sprint)**, recalibradas no fim do Sprint 1. A trilha de front constrói **todas as telas nas Sprints 1–6 contra o mock do contrato**. Depois disso, cada sprint de backend tem uma task de integração que troca o mock pela API real daquelas telas. O quadro fica no **GitHub Project** (doc 12 §4). Cada linha das tabelas abaixo vira uma issue.

**Contrato primeiro:** o contrato da API (`api/openapi.yaml`, doc 13) cobre **todas as telas** antes do desenvolvimento. O front consome o mock gerado a partir dele e pode ser construído por completo sem esperar o backend. Cada task de backend implementa rotas que já estão no contrato; mudar o contrato é um PR próprio, revisado.

**Áreas** (label `area:*`): `infra` (Terraform/GCP) · `devops` (CI/CD, repo, VM) · `backend` · `agent` (LangGraph, prompts, evals) · `frontend` · `docs`.

## Definition of Done (vale para toda task)
- PR revisado e aprovado para `develop`, com CI verde (lint, type-check, testes, Trivy)
- Testes unitários do domínio e de integração dos adapters tocados
- Migrations Alembic reversíveis (`upgrade` + `downgrade` testados)
- Logs estruturados, sem dados sensíveis
- Deploy automático em **staging** funcionando, com smoke test verde
- Infra só muda por Terraform (nada criado à mão no console)
- Documentação atualizada (README/ADR/OpenAPI e Central de Ajuda, quando a mudança afeta o cliente)
- Front: igual ao Figma no desktop (1920) e no mobile (430), nos temas Dark e Light

## Pré-requisitos externos (começar JÁ, eles têm lead time)
| # | Item | Lead time |
|---|---|---|
| P1 | Conta Meta Business verificada + app no Meta for Developers + WABA + **número dedicado** (chip novo, nunca usado no WhatsApp comum). Staging usa o número de teste da Meta | 1–3 semanas |
| P2 | Conta de billing GCP e **login do `gcloud` no terminal** (o Terraform cria projetos, APIs e o resto) | 1 dia · antes do S0-03 |
| P3 | Domínio `arclou.com.br` com DNS delegado para o Cloud DNS | 1 dia · antes do S0-08 |
| P4 | OAuth consent screen do Google (modo teste, até 100 usuários) | 1 dia. A verificação + CASA leva semanas, iniciar no Sprint 11 |
| P5 | Termos de uso + Política de privacidade (advogado), exigidos pela Meta e pelo Google | 2–4 semanas |
| P6 | Templates de WhatsApp (lembrete, resumo diário, vínculo, cobrança) submetidos para aprovação | dias |

## Calendário
| Sprint | Datas | Tema | Back/infra | Front |
|---|---|---|---|---|
| 0 | 19/10 – 30/10/2026 | Infra, Terraform, workflow e contrato de API | 40 | — |
| 1 | 02/11 – 13/11 | Esqueleto da aplicação · feriado 02/11 | 23 | 13 |
| 2 | 16/11 – 27/11 | Gateway WhatsApp e vínculo · feriado 20/11 | 32 | 16 |
| 3 | 30/11 – 11/12 | Núcleo do agente | 37 | 16 |
| 4 | 14/12 – 25/12 | Gastos · feriado 25/12 | 34 | 13 |
| 5 | 28/12 – 08/01/2027 | Finanças I: receitas, limites e disponível · feriado 01/01 | 29 | 16 |
| 6 | 11/01 – 22/01 | Finanças II: recorrentes, cartões e parcelas | 30 | 8 |
| 7 | 25/01 – 05/02 | Finanças III: metas, simulação e insights | 25 | — |
| 8 | 08/02 – 19/02 | Casa I: modelo, convite e divisão · Carnaval 08–09/02 | 28 | — |
| 9 | 22/02 – 05/03 | Casa II: conta conjunta, privacidade e saída | 29 | — |
| 10 | 08/03 – 19/03 | Agenda e lembretes | 34 | — |
| 11 | 22/03 – 02/04 | E-mail · Sexta-feira Santa 26/03 | 33 | — |
| 12 | 05/04 – 16/04 | Assinatura e cobrança | 24 | — |
| 13 | 19/04 – 30/04 | Plataforma, LGPD e Central de Ajuda · feriado 21/04 | 25 | — |
| 14 | 03/05 – 14/05 | Hardening e produção 24/7 | 25 | — |
| 15 | 17/05 – 28/05 | **Beta fechado** (20–50 usuários) | — | — |

> O plano anterior previa o beta nas semanas 21–22. Com a fundação de infra e uma capacidade realista por trilha, o beta vai para **maio de 2027**. Se a velocidade medida for maior, puxamos tasks da sprint seguinte.

---

## Sprint 0 — Infra, Terraform e workflow (19/10 – 30/10)
**Objetivo:** repositório protegido, toda a infra criada por Terraform e um "hello world" da API e do web publicado em **staging e production** na VM pelo pipeline.

| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S0-01 | Monorepo `arclou-com/arclou-assistant` (`backend/`, `web/`, `infra/`, `docs/`), pre-commit (ruff, mypy, eslint, prettier, `terraform fmt`, gitleaks), Conventional Commits | devops | 2 | `pre-commit run --all` passa |
| S0-02 | GitHub: `main` e `develop` protegidas (só PR, checks obrigatórios, histórico linear, sem force push), `develop` como padrão, Environments `staging` e `production` (este com aprovação), templates de PR/issue, labels, CODEOWNERS | devops | 2 | Push direto na `main` é rejeitado |
| S0-03 | Terraform bootstrap: projetos `arclou-stg` e `arclou-prd`, billing, APIs, bucket de state versionado, alertas de orçamento (50/90/100%) | infra | 3 | `terraform apply` do zero. State remoto com lock |
| S0-04 | Terraform da VM: VPC, firewall (80/443 público; 22 só pelo IAP), IP estático, `e2-standard-2` Ubuntu 24.04, **disco de dados separado** com snapshot diário, startup script instala Docker | infra | 5 | Recriar a VM não perde dados. Porta 22 fechada para a internet |
| S0-05 | Agenda de liga/desliga (instance schedule: seg–sex, 08h–20h, `America/Sao_Paulo`) + workflow manual "VM: ligar/desligar" | infra | 2 | A VM desliga às 20h e liga às 08h. O workflow liga fora do horário |
| S0-06 | Artifact Registry, service accounts com papel mínimo e **Workload Identity Federation** para o GitHub Actions (sem chave JSON) | infra | 3 | Actions autentica sem segredo de longa duração |
| S0-07 | Serviços por ambiente: Firestore Native (`southamerica-east1`, TTL em `expires_at`), Firebase Auth, Vertex AI e Secret Manager | infra | 3 | Os dois ambientes isolados (projetos diferentes) |
| S0-08 | Cloud DNS + subdomínios (`app.`, `api.`, `app.stg.`, `api.stg.`) + Caddy com TLS automático roteando para cada ambiente | infra | 3 | Os 4 hosts respondem em HTTPS |
| S0-09 | Pipeline do Terraform: fmt, validate, tflint e `plan` comentado no PR; `apply` em staging no merge em `develop` e em production no merge em `main`, com aprovação | devops | 3 | PR com mudança de infra mostra o plan |
| S0-10 | Hello world: FastAPI com `/health` e Next.js com página inicial, Dockerfiles multi-stage (usuário não root) | backend | 2 | Imagens < 300 MB |
| S0-11 | CI: lint, type-check e testes do back e do front, build das imagens, Trivy, push no Artifact Registry com tag do commit | devops | 3 | PR bloqueado se falhar |
| S0-12 | CD: `deploy.sh` na VM (Secret Manager → `.env`, pull, migrate, `up -d`, health check, rollback para a tag anterior). O job **liga a VM se ela estiver desligada** | devops | 5 | Merge em `develop` → staging no ar. Merge em `main` + aprovação → production no ar. Health quebrado faz rollback |
| S0-13 | Runbook inicial: ligar a VM, deploy e rollback manuais, SSH pelo IAP, custos | docs | 1 | Documento em `docs/runbook.md` |
| S0-14 | Contrato de API no repo (`api/openapi.yaml`, doc 13): lint com Spectral no CI, mock server (Prism) no compose de dev e cliente TS gerado (`openapi-typescript`) para o `web/` | devops | 3 | Mudança no contrato sem regenerar o cliente quebra o CI. O front roda 100% contra o mock |

## Sprint 1 — Esqueleto da aplicação (02/11 – 13/11)
**Objetivo:** backend com banco, fila, logs e auth em staging. O front começa a trilha dele contra o mock.

| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S1-01 | Backend com uv, `config.py` (pydantic-settings), estrutura hexagonal, `/ready` checando as dependências | backend | 2 | Config inválida falha no boot com mensagem clara |
| S1-02 | `compose.yml` de dev (api, worker, postgres+pgvector, redis, firestore-emulator) e base comum com os compose de staging/production | devops | 3 | `docker compose up` sobe tudo do zero |
| S1-03 | SQLAlchemy async + Alembic + 1ª migration (`users`) | backend | 3 | Testcontainers: upgrade/downgrade |
| S1-04 | structlog + `trace_id` por request/job + mascaramento de PII | backend | 2 | Unit do masker (telefone, e-mail, CPF) |
| S1-05 | Worker arq com job de exemplo + cron | backend | 2 | Job enfileirado é executado |
| S1-06 | Middleware Firebase Auth (valida ID token, cria `users` no 1º acesso) + claim `admin` | backend | 3 | Token válido, expirado e sem claim admin → 403 |
| S1-07 | Sentry no back e no front, separado por ambiente | devops | 1 | Erro de teste aparece no projeto certo |
| S1-08 | Backup diário do Postgres de cada ambiente para o GCS (às 19h30, antes de a VM desligar; retenção de 30 dias) | infra | 3 | Restore testado num ambiente limpo |
| S1-12 | E2E de fumaça com Playwright em staging depois de cada deploy (login → painel vazio) | devops | 2 | Falha marca o deploy como quebrado |
| S1-13 | Teste de contrato do backend contra o `openapi.yaml` (schemathesis): rota implementada que diverge do contrato quebra o CI | backend | 2 | Rota com campo a mais/a menos falha |


**Trilha de front (base: tokens, layout e login, contra o mock):**

| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S1-F01 | Next.js (App Router, TS), tokens do Figma (Dark/Light), fontes e componentes base (botão, input, card, modal, drawer, toast, menu ⋯). Vitest + Testing Library. Cliente gerado do contrato apontando para o mock | frontend | 5 | Componentes iguais ao Figma nos dois temas |
| S1-F02 | Layout do painel (sidebar fixa, cabeçalho, desktop 1920 com rolagem, mobile 430) e estados de carregamento, vazio e erro (linha "Estados no Dark") | frontend | 5 | Testes de componente |
| S1-F03 | Login com Firebase Auth (linha "Página de vendas e login"), rotas protegidas e envio do ID token | frontend | 3 | Sem login → redireciona. Token vencido → renova |
## Sprint 2 — Gateway WhatsApp e vínculo (16/11 – 27/11)
**Objetivo:** usuário cadastrado vincula o número e recebe um eco da mensagem.

| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S2-01 | Port `MessagingProvider` (send_text, send_template, send_interactive, mark_read, download_media) | backend | 2 | Interface + fake in-memory |
| S2-02 | Adapter Meta Cloud API (httpx, retry com backoff em 429/5xx, timeouts) | backend | 5 | `respx` simulando respostas e erros |
| S2-03 | `GET /webhooks/whatsapp` (verify token) e `POST` com validação `X-Hub-Signature-256`. Webhook por ambiente | backend | 3 | Assinatura inválida → 401 |
| S2-04 | Parser dos payloads (text, audio, image, interactive, status) para um DTO interno | backend | 3 | Fixtures de cada tipo |
| S2-05 | Idempotência (`SETNX` Redis + `processed_webhooks`) e enqueue rápido | backend | 3 | Mesmo `message_id` 2x → processado 1x. Webhook < 500 ms |
| S2-06 | Lock por usuário + debounce de 3 s agrupando mensagens | backend | 5 | 3 mensagens em 1 s → 1 job com as 3, em ordem |
| S2-07 | Vínculo: `POST /v1/whatsapp/link-code` → link `wa.me` → worker reconhece `VINCULAR-XXXX` | backend | 5 | RN-01.1 a RN-01.3. Código expirado/reutilizado rejeitado |
| S2-08 | Resposta para número não vinculado (sem LLM, 1x/24h) | backend | 2 | Teste de throttle |
| S2-10 | Eco end-to-end no número de teste da Meta, em staging | backend | 2 | Demo: mando "oi", recebo "oi" |
| S2-12 | Integração: login e vínculo do WhatsApp na API real (mock → staging) | frontend | 2 | E2E em staging sem o mock |


**Trilha de front (entrada do cliente, contra o mock):**

| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S2-F01 | Página de vendas (SSR, SEO, desktop e mobile) | frontend | 5 | Lighthouse ≥ 90 |
| S2-F02 | Cadastro e checkout (C02–C06): escolha de plano, dados, pagamento, trial e pagamento recusado | frontend | 8 | Fluxo completo contra o mock, incluindo erros |
| S2-F03 | Vincular WhatsApp (D03): código, link/QR e status do vínculo | frontend | 3 | Testes de componente |
## Sprint 3 — Núcleo do agente (30/11 – 11/12)
**Objetivo:** conversa útil com guardrails e observabilidade. Ainda sem integrações.

| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S3-01 | Adapter Vertex AI (`ChatVertexAI`), região, timeouts, retry, contagem de tokens | agent | 3 | Contrato com modelo fake. Smoke real atrás de flag |
| S3-02 | `ConversationStore` em Firestore (append, últimas N, TTL) | backend | 3 | Integração no emulator |
| S3-03 | Grafo LangGraph: guard_input → load_context → agent ⇄ tools → respond. Checkpointer Postgres | agent | 8 | Testes com `FakeMessagesListChatModel` |
| S3-04 | System prompt v1 (persona, escopo, data/hora local, formato WhatsApp) versionado | agent | 3 | Revisão + evals |
| S3-05 | Guardrail de escopo (Flash-Lite) e recusa padrão (RN-04.1) | agent | 3 | ≥ 95% de acerto em 100 frases |
| S3-06 | Áudio: download da mídia → Gemini multimodal → texto | agent | 3 | Fixture .ogg contém as palavras-chave |
| S3-07 | Confirmação (interrupt/resume, expiração de 10 min) | agent | 5 | Sim, não, ambígua, expirada |
| S3-08 | Gate de assinatura/quota + contador de uso (msgs, tokens) | backend | 3 | Usuário sem plano não chega ao LLM |
| S3-09 | Langfuse Cloud (Hobby) + tracing de cada execução, projeto por ambiente | agent | 1 | Trace com tokens e latência |
| S3-10 | **Harness de evals** (`tests/evals`): golden conversations com asserts de tool e argumentos | agent | 5 | Roda no CI (nightly, modelo real, durante o horário da VM) e gera relatório |


**Trilha de front (finanças, contra o mock):**

| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S3-F01 | Gastos e lançamentos (F01): lista, filtros, editar, excluir, desfazer | frontend | 5 | Testes de componente |
| S3-F02 | Finanças: visão, limites e receitas (F02, F02b) | frontend | 5 | Testes de componente |
| S3-F03 | Planejamento e metas (F03) | frontend | 3 | Testes de componente |
| S3-F04 | Integrações: conectar Google Agenda (D04) e e-mail (E09), com status e desconectar | frontend | 3 | Testes de componente |
## Sprint 4 — Gastos (14/12 – 25/12)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S4-01 | Domínio: `Transaction`, `Category`, `Money` (centavos), regras RN-05 | backend | 3 | Parcelamento com resto de centavos, soft delete |
| S4-02 | Migrations + repositórios Postgres | backend | 3 | Testcontainers |
| S4-03 | Tools `add/update/delete_expense` (com confirmação), `list/summarize_expenses` | agent | 5 | Evals: 50 frases reais → argumentos ≥ 90% |
| S4-04 | `action_log` + `undo_last_action` (10 min) | backend | 3 | Registra → desfaz → some das consultas |
| S4-05 | Foto de comprovante → extração → confirmação (RN-05.6) | agent | 5 | 20 fotos. Valor correto ≥ 90% |
| S4-06 | Orçamentos + alertas 80/100% (1x por mês) | backend | 3 | Unit + integração |
| S4-07 | Recorrentes e lembrete de vencimento (`scheduled_notifications`) | backend | 3 | Clock fake |
| S4-08 | Formatação das respostas (R$ 1.234,56, listas curtas, totais) | agent | 2 | Snapshot tests |
| S4-09 | API de lançamentos (listar, filtrar, editar, excluir) | backend | 5 | Contrato OpenAPI |
| S4-10 | Integração: telas de gastos na API real | frontend | 2 | E2E em staging sem o mock |


**Trilha de front (compromissos, plano e conta, contra o mock):**

| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S4-F01 | Compromissos (F04), Parcelamentos com cartões visuais (F05, F05c, doc 09), modais de receita recorrente e compra parcelada, menu ⋯ / action sheet (F05b) | frontend | 8 | Testes de componente |
| S4-F02 | Trocar de plano (D06) e uso/quotas | frontend | 2 | Testes de componente |
| S4-F03 | Perfil, preferências, privacidade, exportar dados e excluir conta (D07) | frontend | 3 | Testes de componente |
## Sprint 5 — Finanças I: receitas, limites e disponível (28/12 – 08/01)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S5-01 | Calendário de dias úteis (feriados) + dia fixo/útil/ajuste de fim de semana (RN-09.2, RN-10.1) | backend | 3 | 5º dia útil com feriado; dia 31 em fevereiro |
| S5-02 | Receitas fixas/extras + recorrência mensal (RN-09.2) | backend | 3 | Clock fake, meses curtos |
| S5-03 | Limites geral/categoria + projeção de estouro (RN-09.3) | backend | 5 | Início/fim de mês, categoria sem histórico |
| S5-04 | Disponível para gastar e valor diário (RN-09.1) | backend | 3 | Hypothesis: coerente com a soma |
| S5-05 | Agregações, view materializada e `/v1/finance/overview` | backend | 5 | < 200 ms com 10 mil lançamentos |
| S5-06 | Orçamento 50/30/20 com mapeamento de categorias (RN-09.4) | backend | 3 | Unit |
| S5-07 | Memória de longo prazo (`remember_fact`/`forget_fact` + pgvector) | agent | 5 | Fato salvo aparece no contexto quando é relevante |
| S5-08 | Integração: Finanças (visão, limites, receitas) na API real | frontend | 2 | E2E em staging sem o mock |


**Trilha de front (Casa, contra o mock):**

| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S5-F01 | Casa: convite, visão, divisão e escolher o modo (H01, H02, H03) + lado do convidado (J02) | frontend | 5 | Testes de componente |
| S5-F02 | Casa · ações ⋯, acertar contas e o que o parceiro vê (H01b, H01c, H01d) | frontend | 3 | Testes de componente |
| S5-F03 | Dinheiro junto (HJ01, HJ01b, HJ01c), lançamento com origem e saída da Casa (HS01–HS04) | frontend | 5 | Testes de componente |
| S5-F04 | Checkout do Plano Casal | frontend | 3 | Fluxo completo contra o mock |
## Sprint 6 — Finanças II: recorrentes, cartões e parcelas (11/01 – 22/01)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S6-01 | Recorrentes: previstos e confirmação previsto → realizado sem contar duas vezes | backend | 5 | Previsto + pagamento = 1 lançamento |
| S6-02 | Cartões, ciclo de fatura e materialização de faturas (RN-10.3) | backend | 5 | Compra no fechamento, no dia seguinte, virada de ano |
| S6-03 | Compras parceladas (cartão, boleto, carnê, Pix parcelado, financiamento): resto de centavos, juros, quitação, cancelamento (RN-10.4, 10.4b, 10.5) | backend | 8 | Hypothesis: soma das parcelas = total |
| S6-04 | Comprometido por mês + % da renda + alertas (RN-10.6) e integração com disponível e "Posso comprar?" (RN-10.7) | backend | 5 | Evals: 30 perguntas com números corretos |
| S6-05 | Ações por compra parcelada: cronograma, editar só parcelas futuras, registrar pagamento, quitar, cancelar (RN-10.5b) | backend | 5 | Editar não altera parcelas pagas |
| S6-06 | Integração: Compromissos e Parcelamentos na API real | frontend | 2 | E2E em staging sem o mock |


**Trilha de front (Central de Ajuda e fechamento, contra o mock):**

| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S6-F01 | Central de Ajuda (SSR em `ajuda.arclou.com.br`): início, abas, artigo, busca e feedback | frontend | 5 | Navegação igual ao Figma |
| S6-F02 | E2E Playwright navegando todas as telas contra o mock + revisão de acessibilidade (WCAG AA) e responsivo | frontend | 3 | Todas as rotas do contrato usadas por alguma tela |
## Sprint 7 — Finanças III: metas, simulação e insights (25/01 – 05/02)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S7-01 | Metas e aportes, com status de atraso (RN-09.5) | backend | 5 | Unit + integração |
| S7-02 | Simulação "Posso comprar?" à vista e parcelado (RN-09.6) | backend | 5 | Parcelas afetam os meses seguintes |
| S7-03 | Motor de insights + job semanal (RN-09.8) com limite de frequência | backend | 5 | Nunca mais de 1 por semana |
| S7-04 | Tools do agente para finanças + guardrail regulatório (RN-09.7) | agent | 5 | Evals: 60 perguntas corretas, 0 recomendações de investimento no set adversarial (doc 08) |
| S7-05 | Relatório mensal (WhatsApp, dia 1) + página no painel (RF-88) | backend | 3 | Clock fake |
| S7-06 | Integração: Planejamento, metas e relatório na API real | frontend | 2 | E2E em staging sem o mock |

## Sprint 8 — Casa I: modelo, convite e divisão (08/02 – 19/02)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S8-01 | Modelo de dados da Casa + RLS por `household_id`/visibilidade | backend | 5 | O parceiro nunca lê item `personal` (nem em agregados) |
| S8-02 | Criar Casa e convite (link pelo WhatsApp do titular, 7 dias, uso único) + `ENTRAR CASA-XXXX` | backend | 5 | Convite expirado/reutilizado rejeitado |
| S8-03 | Visibilidade por lançamento (pessoal/da casa/dividido); padrão pessoal | backend | 5 | Só o autor muda |
| S8-04 | Regras de divisão (50/50, proporcional sem expor a renda, personalizada, por item) + `household_shares` | backend | 5 | Σ partes = valor; centavos a favor de quem pagou |
| S8-05 | Modo de dinheiro (junto/separado/misto) com confirmação dos dois (RN-11.13) | backend | 3 | Conjunta só após as 2 confirmações |
| S8-06 | Saldo "quem deve quem" + acertar contas (parcial, Pix/dinheiro/abater) | backend | 5 | Saldo zera após o acerto |

## Sprint 9 — Casa II: conta conjunta, privacidade e saída (22/02 – 05/03)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S9-01 | Conta conjunta: entradas, aportes, origem do pagamento, Privado, saldo, previsão, conferir saldo, reembolsos | backend | 8 | Saldo = inicial + entradas − saídas; Privado nunca expõe descrição |
| S9-02 | Orçamento/limites e metas da Casa | backend | 3 | Integração |
| S9-03 | Tools da Casa + guardrail de privacidade | agent | 5 | Evals: 40 casos, 0 vazamentos |
| S9-04 | Avisos ao parceiro (opt-in) e resumo semanal do casal | backend | 3 | Clock fake |
| S9-05 | Sair da Casa (saldo, histórico 90 dias, metas, plano) + exclusão LGPD | backend | 5 | E2E dos dois lados |
| S9-06 | Plano Casal no billing (titular paga, crédito do convidado, downgrade) | backend | 3 | Sandbox do gateway |
| S9-07 | Integração: telas da Casa e Dinheiro junto na API real | frontend | 2 | E2E em staging sem o mock |

## Sprint 10 — Agenda e lembretes (08/03 – 19/03)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S10-01 | OAuth Google: authorization code + PKCE, `state` assinado, tokens criptografados | backend | 5 | Tokens nunca aparecem em log |
| S10-02 | Serviço de crypto (AES-GCM, `key_id`, rotação; chave mestra no Secret Manager) | backend | 3 | Chave errada falha |
| S10-03 | Refresh de token + revogação (RN-06.5) | backend | 3 | `invalid_grant` → `revoked` + aviso único |
| S10-04 | Adapter Google Calendar (list, create, update, delete, freebusy) | backend | 5 | `respx` com fixtures reais |
| S10-05 | Tools de agenda + datas relativas no fuso do usuário (RN-06.6) | agent | 5 | Evals: "amanhã", "sexta que vem", virada de mês/ano |
| S10-06 | Lembretes avulsos (`create_reminder`) | backend | 3 | Clock fake |
| S10-07 | Scheduler: poller de `scheduled_notifications` (`FOR UPDATE SKIP LOCKED`), retries, horário de silêncio | backend | 5 | 2 workers → nenhum envio duplicado |
| S10-08 | Janela de 24h: mensagem livre × template (RN-06.3) + quota | backend | 3 | Janela aberta/fechada |
| S10-09 | Integração: conectar Google Agenda na API real | frontend | 2 | E2E em staging sem o mock |

## Sprint 11 — E-mail (22/03 – 02/04)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S11-01 | Lembrete de eventos do Calendar (sync incremental dos próximos eventos) | backend | 5 | Evento criado no Google → lembrete enviado |
| S11-02 | Escopos Gmail incrementais | backend | 2 | Sem Gmail, sem tools de e-mail |
| S11-03 | Adapter Gmail (list, search, get, draft, send) | backend | 5 | `respx` + fixtures |
| S11-04 | `list_important_emails` com resumo (Flash-Lite) | agent | 5 | Sem alucinar remetente/assunto |
| S11-05 | `search_emails` (linguagem natural → query Gmail) | agent | 3 | Evals |
| S11-06 | `draft_email` + `send_email` com confirmação e preview (RN-07.1) | agent | 5 | Impossível enviar sem o "sim" |
| S11-07 | Defesa contra prompt injection em e-mails | agent | 3 | Set adversarial não gera ação |
| S11-08 | Resumo diário matinal (agenda + vencimentos + e-mails) via template | backend | 3 | Clock fake |
| S11-10 | **Iniciar verificação OAuth + CASA do Google** | docs | — | Processo aberto |
| S11-09 | Integração: conectar e-mail na API real | frontend | 2 | E2E em staging sem o mock |

## Sprint 12 — Assinatura e cobrança (05/04 – 16/04)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S12-01 | Escolha do gateway (spike: Pix Automático, taxas, webhooks) e ADR | backend | 2 | ADR aprovado |
| S12-02 | Tabelas `plans`/`subscriptions` + seed | backend | 2 | Migration |
| S12-03 | Checkout/criação de assinatura via API | backend | 5 | Sandbox do gateway |
| S12-04 | Webhook do gateway → máquina de estados RN-02.2 | backend | 5 | Eventos fora de ordem |
| S12-05 | Trial, carência, suspensão e avisos (RN-02.1/02.3/02.4) | backend | 3 | Clock fake |
| S12-06 | Quotas por plano e mensagens de upgrade (RN-03) | backend | 3 | Unit |
| S12-07 | Cancelamento self-service | backend | 2 | E2E no sandbox |
| S12-08 | Integração: página de vendas, checkout, Plano Casal e trocar de plano no gateway (sandbox) | frontend | 2 | E2E em staging sem o mock |

## Sprint 13 — Plataforma, LGPD e Central de Ajuda (19/04 – 30/04)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S13-01 | APIs `/v1/me` (perfil, integrações, uso, plano) | backend | 3 | Contrato OpenAPI |
| S13-02 | APIs admin (usuários, suspender, métricas) + `admin_audit` | backend | 5 | Testes de autorização |
| S13-03 | Exportação e exclusão de conta (RN-08) | backend | 5 | Nada sobra em Postgres/Firestore; tokens revogados |
| S13-04 | Central de Ajuda (back): artigos em `help/` (Markdown + `depends_on`), indexação pgvector, API de busca com resposta citando o artigo e feedback | backend | 5 | Busca "conta conjunta" → artigo certo; a resposta só usa trechos encontrados |
| S13-05 | `search_help` + "ajuda" no WhatsApp + links no painel + `check_help_sync.py` no CI | agent | 5 | O CI falha quando uma RN muda sem o artigo |
| S13-06 | Integração: perfil, privacidade, exportar/excluir conta e Central de Ajuda na API real | frontend | 2 | E2E em staging sem o mock |

## Sprint 14 — Hardening e produção 24/7 (03/05 – 14/05)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S14-01 | **Produção 24/7**: VM própria para production, sem agenda de desligamento (staging continua desligando). Terraform | infra | 5 | Lembretes das 07h e webhooks à noite funcionam |
| S14-02 | Cutover de produção: número real da Meta, templates aprovados, OAuth em produção | devops | 3 | Checklist do runbook |
| S14-03 | RLS no Postgres como 2ª camada | backend | 3 | Query sem `user_id` não retorna nada |
| S14-04 | Cloud Monitoring: uptime checks, alertas (erro, latência, disco, fila) e dashboard | infra | 3 | Alerta dispara em teste |
| S14-05 | Teste de carga (k6): 50 msgs/s no webhook, 200 usuários simultâneos | devops | 3 | p95 dentro do RNF-01 |
| S14-06 | Revisão de segurança (OWASP API Top 10, `pip-audit`, Trivy, gitleaks) | devops | 3 | Zero high/critical |
| S14-07 | Runbook completo (deploy, rollback, restore, incidente da Meta) | docs | 2 | Documento |
| S14-08 | Ensaio de restore e de recriação da VM pelo Terraform | infra | 3 | Ambiente volta em < 1 h |

## Sprint 15 — Beta fechado (17/05 – 28/05)
| ID | Task | Área | Pts | Critério de aceite / testes |
|---|---|---|---|---|
| S15-01 | **Beta fechado** com 20–50 usuários + coleta de feedback | docs | — | Métricas de uso/erros por 2 semanas |

### Roadmap V2 (pós-beta)
Outlook/Microsoft 365 · Open Finance · relatórios mensais em PDF · app de admin mais completo · migração da API para Cloud Run, se a escala pedir.

---

## Estratégia de testes

| Camada | Ferramenta | O que cobre | Quando roda |
|---|---|---|---|
| **Unit** | pytest · Vitest | Domínio puro (Money, parcelamento, assinatura, datas, janela 24h) com clock fake; componentes do front | Todo PR |
| **Integração** | pytest + testcontainers (Postgres, Redis) + Firestore emulator + respx | Repositórios, adapters, migrations, jobs | Todo PR |
| **Grafo do agente** | LangGraph + LLM fake determinístico | Roteamento, interrupts, `UserContext`, erros de tool | Todo PR |
| **Infra** | `terraform validate`, tflint, `plan` | Toda mudança em `infra/` | Todo PR |
| **Evals (LLM real)** | Harness próprio (pytest + YAML) | Escolha de tool e argumentos, recusa, prompt injection, formatação | Nightly + antes de mudar prompt/modelo |
| **E2E** | Playwright + fake da Meta | Fluxo completo e smoke do painel | Depois de cada deploy em staging |
| **Carga** | k6 | Webhook e worker | Antes do beta |
| **Segurança** | pip-audit, npm audit, Trivy, gitleaks | Dependências, imagens, segredos | CI |

**Regra de ouro:** mudança de prompt ou de modelo é tratada como mudança de código. Ela só entra se os evals não regredirem.
