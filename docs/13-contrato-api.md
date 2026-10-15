# 13 — Contrato da API (painel web)

> Fonte da verdade: [`api/openapi.yaml`](../api/openapi.yaml) (OpenAPI 3.1, 98 rotas, 126 operações). Este documento explica as decisões e mapeia **cada tela do Figma** para as rotas que ela usa. Escrito em 15/10/2026 a partir da página "IA Assistente Painel · Light" (fileKey `PJ7SvIZo5iVL4GqUoT0xAi`).

## 1. Para que serve
- O **front é construído por completo contra o mock** (Prism) gerado do contrato, antes do backend existir (doc 05, "Contrato primeiro").
- O **backend implementa exatamente o contrato**: o teste de contrato (S1-13) quebra o CI se uma rota divergir.
- Mudar o contrato é um **PR próprio**, revisado, que regenera o cliente TypeScript (S0-14).

## 2. Convenções

| Tema | Regra |
|---|---|
| Base | `https://api.arclou.com.br` (prod), `https://api.stg.arclou.com.br` (staging), `http://localhost:4010` (mock). Tudo sob `/v1` |
| Auth | `Authorization: Bearer <ID token do Firebase>`. Rotas públicas (`security: []`): planos, emissores de cartão, convite público, Central de Ajuda |
| Nomes | JSON em `snake_case`, em inglês. Textos para o usuário em pt-BR |
| Dinheiro | **Sempre inteiro em centavos** (`*_cents`), BRL. Saídas na conjunta são negativas |
| Datas | `date` = `AAAA-MM-DD` no fuso do usuário; `date-time` ISO 8601 com fuso; mês de referência `?month=AAAA-MM` |
| IDs | UUID v7 |
| Listas | Cursor: `?cursor=&limit=` → `{ items, next_cursor }` |
| Erros | `application/problem+json` (RFC 9457) com `code` estável (`not_found`, `plan_required`, `not_author`, `validation_error`…) e `errors[]` por campo |
| Idempotência | `Idempotency-Key` (UUID) em checkout, pagamento de parcela, quitação e acerto de contas |
| **O front não calcula dinheiro** | Totais, percentuais, projeções, divisões e simulações vêm prontos. Antes de salvar, o front chama o `…/preview` correspondente |
| Textos prontos | Frases que dependem de regra de negócio vêm da API (`messages[]`, `label`, `headline`) para o front não duplicar regra |
| Polling | Telas que "atualizam sozinhas" consultam o GET a cada 3 s até o `status` mudar |
| Plano | Recurso fora do plano → `403 plan_required` com `required_plan`; o front mostra o upsell |

## 3. Mapa tela → endpoints

Desktop e mobile usam as mesmas rotas (MF*, MH*, M* espelham as telas desktop).

### Página de vendas, login e checkout
| Tela | Endpoints |
|---|---|
| LP · Página de vendas | `listPlans` (preços, "R$ 0,66 por dia", oferta de fundador) |
| 01 · Login | Firebase Auth no cliente (e-mail/senha e Google) → `getMe` |
| C02 / CC02 · Criar conta | Firebase Auth (cadastro) → `recordConsent` (termos) → `createCheckoutSession` |
| C03 / CC03 · Cartão | `validateCoupon` ("Tenho um cupom") → tokenização no SDK do gateway → `payCheckoutWithCard` |
| C04 · Pix Automático | `payCheckoutWithPixAutomatic` → polling `getCheckoutSession` até `completed` |
| C05 · Cartão recusado | `payCheckoutWithCard` devolve `status = declined` com `decline.message` |
| C06 / CC06 · Confirmada | `getCheckoutSession` (`trial_ends_on`, `receipt_email`); no Casal, `createHouseholdInvite` |

### Painel
| Tela | Endpoints |
|---|---|
| Sidebar (todas) | `getMe` (nome, iniciais, e-mail, tema), `getHousehold` (mostra "Casa") |
| 02 · Visão geral | `getOverview` |
| 03 · Vincular número | `createWhatsAppLinkCode` → polling `getWhatsApp` até `linked` |
| 03b · Conectado | `getWhatsApp`, `updateWhatsAppSettings`, `createWhatsAppLinkCode` ("Trocar número"), `unlinkWhatsApp` |
| 04 · Integrações | `listIntegrations`, `selectGoogleCalendars`, `revokeIntegration` |
| E09 · Aguardando Google | `startGoogleAuthorization` (popup) → polling `listIntegrations`; "Cancelar" = `revokeIntegration` |
| 05 · Perfil e preferências | `getMe`, `updateMe`, `listCategories`, `createCategory`, `updateCategory`, `deleteCategory` |
| 06 · Assinatura | `getSubscription`, `getUsage`, `listInvoices`, `changePaymentMethod`, `cancelSubscription`, `resumeSubscription` |
| D06 · Trocar plano | `listPlans`, `previewPlanChange`, `changePlan` |
| 07 · Privacidade e dados | `listMemoryFacts`, `deleteMemoryFact`, `clearMemoryFacts`, `getDataExport`, `requestDataExport`, `requestAccountDeletion` |

### Finanças
| Tela | Endpoints |
|---|---|
| F01 · Visão do mês | `getFinanceOverview` (cards, ranking, orientações, evolução, maiores gastos), `dismissInsight`, `exportTransactionsCsv` |
| F02 · Limites e receitas | `listIncomes`, `getLimits`, `setGeneralLimit`, `createCategoryLimit`, `updateCategoryLimit`, `deleteCategoryLimit` |
| F02b · Nova receita recorrente | `previewIncome` (a cada mudança no formulário) → `createIncome`; `confirmIncomeOccurrence` |
| F03 · Planejamento e metas | `getMonthPlan`, `setBudgetModel`, `listGoals`, `createGoal`, `updateGoal`, `addGoalContribution`, `simulatePurchase` |
| F04 · Compromissos | `getCommitments`, `listCards`, `listRecurringExpenses`, `createRecurringExpense`, `updateRecurringExpense`, `confirmRecurringPayment` |
| F05 · Parcelamentos | `listCards`, `listInstallmentPlans?payment_method=` (filtros e contagens) |
| F05b · Nova compra parcelada | `listCards` → `previewInstallmentPlan` (quadro amarelo) → `createInstallmentPlan` |
| F05c · Novo cartão | `listCardIssuers` (13 cores e cor-padrão) → `createCard` |
| F05 · Ver parcelas | `getInstallmentPlan` |
| F05 · Editar | `updateInstallmentPlan` |
| F05 · Quitar | `previewInstallmentPayoff` → `payoffInstallmentPlan` |
| F05 · Cancelar | `previewInstallmentCancel` → `cancelInstallmentPlan` |
| F05 · Registrar pagamento | `registerInstallmentPayment` (só fora do cartão; o item traz `allowed_actions`) |

### Casa
| Tela | Endpoints |
|---|---|
| H02 · Convidar | `getHousehold` (404 → H02), `previewPlanChange`/`changePlan` ("Mudar para o Casal"), `createHousehold`, `createHouseholdInvite` |
| H02b · Convite enviado | `getHouseholdInvite`, `cancelHouseholdInvite`, `confirmInvitedMember` |
| H01 · Visão (Separado) | `getHousehold`, `getHouseholdOverview`, `listHouseholdTransactions`, `remindPartner` |
| H01 · menu ⋯ / Detalhes | `getTransaction` |
| H01 · Editar | `updateTransaction` |
| H01 · Remover da Casa | `previewTransactionVisibility` → `setTransactionVisibility` (`personal`) |
| H01 · Mover da minha conta | `listTransactions?visibility=personal` → `setTransactionVisibility` |
| H01b · Acertar contas | `createSettlement`, `remindPartner` |
| H01c · Regra de divisão | `setSplitRule`; o parceiro usa `confirmSplitRule` |
| H01d · Visibilidade | `previewTransactionVisibility` → `setTransactionVisibility` |
| H03 · Modo do dinheiro | `setMoneyMode` → pendente até `confirmMoneyMode` do parceiro |
| HJ01 · Dinheiro junto | `getJointAccount`, `listJointAccountMovements`, `createJointEntry`, `upsertJointAccount` |
| HJ01b · Lançamento e origem | `previewTransaction` (saldo da conjunta depois) → `createTransaction`; `revealPrivateTransaction` |
| HJ01c · Conferir saldo | `previewReconciliation` (a cada marcação) → `reconcileJointAccount` |
| HS01 · Sair: o que acontece | `previewLeaveHousehold` |
| HS02 + HS03 · Dividir e confirmar | `leaveHousehold` (digitando SAIR) |
| HS04 · Somente leitura | `getHousehold` (`status = read_only`), `exportHouseholdCsv`, `undoLeaveHousehold` (até 24 h) |
| Orçamento / meta da casa | `createHouseholdLimit`, `updateHouseholdLimit`, `deleteHouseholdLimit`, `createHouseholdGoal`, `addHouseholdGoalContribution` |

### Lado do convidado (João)
| Tela | Endpoints |
|---|---|
| J01 · Convite no WhatsApp da Marina | — (mensagem enviada pelo WhatsApp da titular) |
| J02 / JD02 · Aceitar convite | `getPublicInvite` (público) → Firebase Auth (cadastro) → `acceptInvite` |
| J03 / JD03 · Como vocês dividem | `getInviteProgress` (proposta) → `respondSplitProposal` |
| J04 / JD04 · Entrar pelo WhatsApp | `getInviteProgress` com polling até `joined` |

### Central de Ajuda
| Tela | Endpoints |
|---|---|
| Artigos (SSR) | Markdown em `help/` renderizado pelo Next.js (sem API) |
| Busca | `searchHelp` (resposta rápida só com trechos encontrados) |
| "Este artigo ajudou?" | `sendHelpFeedback` |

## 4. Fluxos que merecem atenção
- **Vínculo do WhatsApp (03):** o código expira em 30 min. A tela mostra o contador a partir de `pending.expires_at` e faz polling em `getWhatsApp`.
- **Google (E09):** o popup volta para `/v1/integrations/google/callback` (backend), que fecha a janela. A tela não lê o callback, só faz polling.
- **Cartão no checkout:** o número do cartão nunca passa pela nossa API (PCI). O gateway (S12-01) tokeniza no navegador. No mock, `card_token = tok_declined` simula a recusa.
- **Prévias:** F02b, F05b, Quitar, Cancelar, Remover da Casa, HJ01b, HJ01c e "Posso comprar?" chamam um `…/preview` sem gravar nada. Faça debounce de 300 ms nas mudanças do formulário.
- **Confirmações do parceiro:** regra de divisão e modo de dinheiro ficam em `pending`/`money_mode_change` até o outro confirmar. A tela mostra "O João confirma pelo WhatsApp".
- **Privacidade da Casa:** a API nunca devolve item pessoal do parceiro. Itens Privados vêm como `title = Privado`, sem descrição nem categoria. A renda informada (`my_monthly_income_cents`) é só de escrita.

## 5. Mock (Prism)
```bash
npx @stoplight/prism-cli@5 mock api/openapi.yaml -p 4010      # ou: docker compose up mock (S0-14)
curl localhost:4010/v1/finance/overview -H "Authorization: Bearer x"
```
| Para ver… | Use |
|---|---|
| Um exemplo nomeado (ex.: WhatsApp aguardando) | `Prefer: example=aguardando` |
| Um erro | `Prefer: code=404` (ou 401, 403, 409, 422) |
| Dados gerados a partir do schema | `Prefer: dynamic=true` |

Os exemplos usam os dados do protótipo (Marina, João, TV 55", Nubank 4821…) para as telas do mock ficarem iguais às do Figma.

Exemplos nomeados disponíveis: `getCheckoutSession` (`pendente_pix`, `confirmada`, `recusada`), `getWhatsApp` (`conectado`, `aguardando`) e `getHousehold` (`separado`, `dinheiro_junto`).

## 6. Fora deste contrato (por enquanto)
- **Admin (RF-61, RF-62):** não há telas no Figma. As rotas entram junto com o S13-02.
- **Webhooks** (Meta, gateway, callback do Google): são da API, mas não são consumidos pelo front. Entram no contrato quando forem implementados (S2, S10, S12).
- **Agenda e e-mail no painel:** o Figma não tem telas de eventos nem de e-mails (isso acontece no WhatsApp). O painel só conecta as contas.

## 7. Validação
- `spectral lint api/openapi.yaml` (regras `spectral:oas`): **0 erros** (o próprio Spectral valida cada exemplo contra o schema).
- `redocly lint api/openapi.yaml`: válido. Os avisos restantes são de operações sem resposta 4xx declarada.
- Prism testado com planos, visão do mês, exemplos nomeados, 404, 401 sem token, 422 e a prévia de parcelas.
