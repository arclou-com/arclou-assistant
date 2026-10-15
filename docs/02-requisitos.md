# 02 — Levantamento de requisitos

Convenção: **RF** = requisito funcional, **RNF** = não funcional. Prioridade MoSCoW: **M** (must), **S** (should), **C** (could), **W** (won't, por ora).

## 1. Atores

| Ator | Descrição |
|---|---|
| **Usuário (assinante)** | Pessoa física que assina o plano e conversa com a assistente pelo WhatsApp |
| **Visitante** | Ainda não assinante. Acessa a landing page e o cadastro |
| **Administrador** | Você e o time: gestão de usuários, planos, suporte e métricas |
| **Sistemas externos** | WhatsApp Cloud API, Firebase Auth, Vertex AI, Google Calendar/Gmail, gateway de pagamento |

## 2. Requisitos funcionais

### 2.1 Conta, onboarding e vínculo do WhatsApp
| ID | Requisito | Prio |
|---|---|---|
| RF-01 | Cadastro e login na plataforma web via Firebase Auth (e-mail/senha e Google) | M |
| RF-02 | Vincular o número de WhatsApp à conta: a plataforma gera um código único e um link `wa.me/<numero>?text=VINCULAR-ABC123`. Quando o usuário envia a mensagem, o backend associa o `wa_id` à conta (a posse do número fica provada por ele ter enviado a mensagem) | M |
| RF-03 | Mensagens de números não vinculados recebem uma resposta padrão com o link de cadastro, sem chamar o LLM | M |
| RF-04 | Configurar perfil: nome, fuso horário, moeda, horário do resumo diário, idioma (pt-BR na V1) | M |
| RF-05 | Trocar o número vinculado (desvincula o anterior) | S |
| RF-06 | Opt-in explícito para mensagens proativas (lembretes e resumo), exigido pela política da Meta | M |

### 2.2 Assistente conversacional (núcleo)
| ID | Requisito | Prio |
|---|---|---|
| RF-10 | Receber mensagens de texto e responder em linguagem natural | M |
| RF-11 | Receber **áudio** (voice note), transcrever e processar como texto | M |
| RF-12 | Receber **imagem** (foto de nota fiscal/comprovante) e extrair um gasto | S |
| RF-13 | Manter contexto da conversa (memória de curto prazo) e fatos do usuário (longo prazo: "meu cartão principal é o Nubank") | M |
| RF-14 | Pedir confirmação antes de ações destrutivas ou externas (enviar e-mail, excluir evento, apagar gasto) | M |
| RF-15 | Recusar educadamente pedidos fora do escopo (guardrail, ver doc 01 §3) | M |
| RF-16 | Comandos rápidos: `ajuda`, `resumo`, `desfazer` | S |
| RF-17 | Agrupar mensagens enviadas em sequência rápida (debounce de alguns segundos) antes de processar | S |

### 2.3 Gastos (finanças pessoais)
| ID | Requisito | Prio |
|---|---|---|
| RF-20 | Registrar gasto por linguagem natural ("gastei 45 no ifood ontem no crédito") com valor, data, categoria, descrição e forma de pagamento | M |
| RF-21 | Registrar receitas | S |
| RF-22 | Categorização automática com categorias padrão e personalizadas | M |
| RF-23 | Consultar: "quanto gastei com mercado este mês?", "maiores gastos da semana" | M |
| RF-24 | Editar e excluir lançamentos ("o último foi 54, não 45") | M |
| RF-25 | Orçamento mensal por categoria com alerta ao atingir 80% e 100% | S |
| RF-26 | Gastos recorrentes (aluguel, assinaturas) com lembrete de vencimento | S |
| RF-27 | Parcelamento ("comprei TV em 10x de 300") gerando N lançamentos futuros | S |
| RF-28 | Exportar CSV/planilha pela plataforma web | C |
| RF-29 | Integração bancária (Open Finance) | W |

### 2.3.1 Inteligência financeira (diferencial do produto)
> Tudo que está aqui funciona **no WhatsApp e no painel web**. A assistente precisa saber registrar, consultar, explicar e orientar sobre cada item.

| ID | Requisito | Plano | Prio |
|---|---|---|---|
| RF-80 | **Visão dos gastos:** total do mês, gasto por categoria (ranking e participação %), evolução dos últimos 6 meses, maiores gastos, comparação com o mês anterior e gasto médio por dia | Essencial | M |
| RF-81 | **Receitas recorrentes:** salário e outras rendas fixas com valor e **dia de recebimento**, que pode ser um dia fixo ("todo dia 5") ou um dia útil ("5º dia útil"), com ajuste para fim de semana e feriado. Valor fixo ou variável ("comissão, uns 1.500"). Mais as receitas extras pontuais | Essencial | M |
| RF-82 | **Limite de gastos:** limite mensal geral e por categoria, com alertas em 80% e 100% (RN-05.5) e projeção de estouro ("no ritmo atual, você passa do limite de Delivery no dia 24") | Essencial | M |
| RF-83 | **Disponível para gastar:** receita − contas fixas − reserva para metas − gastos do mês, com valor diário sugerido até o fim do mês | Essencial | M |
| RF-84 | **Planejamento do mês:** orçamento sugerido a partir da renda (modelo 50/30/20 ajustável), contas fixas previstas e projeção de saldo no fim do mês | Pro | M |
| RF-85 | **Metas:** criar objetivos (valor, prazo e para onde vai o dinheiro), acompanhar o progresso, registrar aportes e calcular quanto guardar por mês | Pro | M |
| RF-86 | **"Posso comprar?":** simular uma compra (à vista ou parcelada) e mostrar o impacto no disponível, no limite da categoria e nas metas | Pro | S |
| RF-87 | **Orientações da Arclou:** insights automáticos (gasto fora do padrão, categoria crescendo, assinatura esquecida, meta atrasada) e dicas práticas sob demanda | Pro: semanais e sob demanda · Essencial: só alertas de limite | M |
| RF-88 | **Relatório mensal:** resumo no WhatsApp no dia 1 (onde gastou, o que mudou, metas) e página no painel | Pro | S |
| RF-89 | **Exportar extrato** por período (CSV) | Essencial | C |
| RF-90 | **Gastos recorrentes:** cadastrar contas e assinaturas fixas (aluguel, luz, internet, streaming). Cada uma tem valor fixo ou estimado, dia de vencimento, forma de pagamento (cartão, Pix, boleto, débito automático) e categoria. Elas geram lançamentos previstos todo mês, com lembrete antes do vencimento | Essencial | M |
| RF-91 | **Cartões de crédito:** cadastrar cartões com **banco emissor** (lista: Nubank, Neon, Itaú, Bradesco, Inter, C6, Santander, Banco do Brasil, Caixa, Mercado Pago ou "Outro"), apelido, **dia de fechamento**, **dia de vencimento**, limite (opcional) e os 4 últimos dígitos (opcional, só para identificação). O cartão aparece no **modelo visual Arclou**, com a **cor-padrão do banco**, que o usuário pode trocar (13 cores ou uma personalizada). Sem logos e sem nenhum dado real (doc 09). Mostrar a fatura atual e as próximas | Essencial | M |
| RF-92 | **Compras parceladas** em qualquer forma de pagamento: **cartão de crédito**, **boleto**, **carnê/crediário**, **Pix parcelado** e **financiamento**. No cartão, a parcela cai na fatura certa, conforme a data da compra e o fechamento. Nas outras formas, ela vence todo mês no dia informado. Mostrar parcela atual/total, valor restante, próxima parcela e mês da última. Filtrar por forma de pagamento. Permitir quitar antecipadamente ou cancelar. Há uma aba própria, "Parcelamentos", no painel | Essencial | M |
| RF-93 | **Comprometido nos próximos meses:** visão mês a mês de quanto da renda já está comprometido com recorrentes e parcelas (próximos 6 a 12 meses) | Essencial | M |
| RF-94 | Todo o gerenciamento financeiro (disponível, projeção, limites, orçamento 50/30/20, metas, "Posso comprar?", orientações) **considera recorrentes e parcelas** como valores comprometidos | Essencial / Pro | M |

### 2.3.2 Finanças a dois: plano Casal (no lançamento)
> Cada pessoa tem a própria conta, o próprio WhatsApp vinculado e as próprias finanças. A **Casa** é um espaço compartilhado onde fica **só o que cada um marcar**. Regras na RN-11.

| ID | Requisito | Prio |
|---|---|---|
| RF-100 | **Criar Casa e convidar parceiro(a)** por link ou código (`CASA-XXXX`), compartilhado pelo **WhatsApp do próprio titular** (a Arclou não inicia conversa com quem não deu opt-in, RN-11.2). O convidado cria a própria conta (ou usa a que já tem) e aceita. No máximo 2 membros | M |
| RF-101 | **Visibilidade por lançamento:** Pessoal (padrão), Da casa ou Dividido. Vale para gastos, recorrentes e parcelamentos. Muda pelo painel ou pelo WhatsApp ("esse mercado foi da casa") | M |
| RF-102 | **Regra de divisão da Casa:** 50/50, proporcional à renda (sem revelar a renda ao outro), personalizada (ex.: 60/40) ou por lançamento | M |
| RF-103 | **Quem deve quem:** saldo do mês calculado entre o que cada um pagou e a parte de cada um. O histórico fica visível para os dois | M |
| RF-104 | **Acertar contas:** registrar o pagamento entre os dois (Pix, dinheiro, abatimento), zerando o saldo. Lembrete opcional ao outro pelo WhatsApp | M |
| RF-105 | **Visão da Casa:** gastos da casa por categoria, lançamentos recentes (quem pagou e como foi dividido), contas e parcelas da casa | M |
| RF-106 | **Orçamento e limites da Casa** por categoria (ex.: mercado R$ 1.500 para os dois), com alertas para os dois | S |
| RF-107 | **Metas conjuntas:** valor, prazo e aporte de cada um, com aporte sugerido conforme a regra de divisão | S |
| RF-108 | **Avisos ao parceiro** (opt-in por pessoa): "Marina registrou o aluguel", alerta de limite da Casa, resumo semanal do casal | S |
| RF-109 | **Sair da Casa:** encerra o saldo pendente, congela o histórico compartilhado e cada um mantém os próprios dados. Divisão das metas conjuntas conforme os aportes | M |
| RF-111 | **Modo de dinheiro da Casa:** Dinheiro junto, Separado ou Misto, escolhido e confirmado pelos dois (RN-11.13) | M |
| RF-112 | **Conta conjunta:** saldo inicial, entradas, saídas, cartões da conta, saldo atual, previsão do mês e "Conferir saldo" com ajuste (RN-11.14) | M |
| RF-113 | **Origem do pagamento** em cada lançamento da casa (conta conjunta ou a pessoa) e itens **Privados** na conjunta (RN-11.14, RN-11.15) | M |
| RF-114 | **Modo Misto:** aportes sugeridos pela regra de divisão e reembolsos de quem pagou do próprio bolso (RN-11.16, RN-11.17) | S |
| RF-115 | **Central de Ajuda** (`ajuda.arclou.com.br`): artigos por assunto no estilo Google Cloud, com busca, exemplos de WhatsApp, capturas e feedback por página (`docs/11`) | M |
| RF-116 | **Acesso à Central** pelo menu lateral, pela aba Conta (mobile), por links contextuais "Como funciona?" e pelo WhatsApp ("ajuda" e perguntas livres com o link do artigo) | M |
| RF-117 | **Central sempre atualizada:** toda mudança em regra, preço, quota, fluxo ou tela documentada atualiza o artigo no mesmo PR (check de CI, `docs/11` §5) | M |
| RF-110 | **Plano Casal:** R$ 49,90/mês para os 2 (contas Pro, com as quotas por pessoa da RN-03). Upgrade e downgrade pelo painel | M |

### 2.4 Agenda
| ID | Requisito | Prio |
|---|---|---|
| RF-30 | Conectar Google Calendar via OAuth na plataforma web | M |
| RF-31 | Criar evento ("reunião com João amanhã às 15h por 1h") | M |
| RF-32 | Consultar agenda ("o que tenho hoje?", "estou livre quinta à tarde?") | M |
| RF-33 | Remarcar e cancelar eventos (com confirmação) | M |
| RF-34 | Lembretes proativos antes do evento (antecedência configurável) | M |
| RF-35 | Resumo diário matinal (agenda do dia, contas a vencer, e-mails importantes) | S |
| RF-36 | Lembretes avulsos sem calendário ("me lembra de ligar pro banco às 16h") | M |
| RF-37 | Microsoft Outlook Calendar | W (V2) |

### 2.5 E-mail
| ID | Requisito | Prio |
|---|---|---|
| RF-40 | Conectar Gmail via OAuth | M |
| RF-41 | Resumir e-mails não lidos/importantes ("tenho algo importante?") | M |
| RF-42 | Buscar e-mails ("acha o e-mail da Claro sobre a fatura") | M |
| RF-43 | Redigir resposta/novo e-mail e **enviar só após confirmação explícita** | M |
| RF-44 | Notificação proativa de e-mail importante (por regras/remetentes VIP) | C |
| RF-45 | Outlook/Microsoft 365 | W (V2) |

### 2.6 Assinatura e cobrança
| ID | Requisito | Prio |
|---|---|---|
| RF-50 | Planos mensais com período de teste (trial) | M |
| RF-51 | Pagamento recorrente: cartão e Pix (gateway: Asaas, Stripe ou Mercado Pago, decidir no Sprint 6) | M |
| RF-52 | Webhooks do gateway atualizam o status da assinatura (ativa, inadimplente, cancelada) | M |
| RF-53 | Bloqueio gradual por inadimplência (ver RN) | M |
| RF-54 | Cancelamento self-service | M |
| RF-55 | Cupons de desconto | C |

### 2.7 Plataforma web e Admin
| ID | Requisito | Prio |
|---|---|---|
| RF-60 | Painel do usuário: status do plano, integrações conectadas, configurações, uso | M |
| RF-61 | Admin: listar/buscar usuários, ver status, suspender, reenviar vínculo | M |
| RF-62 | Admin: métricas (MAU, mensagens/dia, custo LLM por usuário, churn) | S |
| RF-63 | LGPD: exportar meus dados e excluir minha conta | M |

## 3. Requisitos não funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF-01 | Desempenho | Webhook do WhatsApp responde `200` em **< 500 ms** (o processamento é assíncrono). Resposta ao usuário: p95 **< 8 s** para texto e < 15 s para áudio/imagem |
| RNF-02 | Confiabilidade | Processamento **idempotente** pelo `message_id` da Meta, que reenvia webhooks |
| RNF-03 | Confiabilidade | Ordem das mensagens preservada por usuário (lock/fila por `user_id`) |
| RNF-04 | Disponibilidade | 99,5% mensal na V1 (VPS única + monitoramento + restart automático) |
| RNF-05 | Segurança | Validar a assinatura `X-Hub-Signature-256` em todo webhook da Meta e a assinatura dos webhooks do gateway |
| RNF-06 | Segurança | Tokens OAuth (Google) **criptografados em repouso** (AES-256-GCM, chave fora do banco: Secret Manager/KMS ou variável protegida) |
| RNF-07 | Segurança | Isolamento multi-tenant: toda query filtrada por `user_id`. Tools do agente recebem `user_id` do contexto, **nunca do LLM** |
| RNF-08 | Segurança | Proteção contra prompt injection vinda de conteúdo de e-mails (conteúdo externo tratado como dado; ações sensíveis sempre exigem confirmação humana) |
| RNF-09 | Privacidade | LGPD: base legal, termos e política de privacidade, retenção configurada, exclusão em até 15 dias, logs sem conteúdo sensível (mascarar) |
| RNF-10 | Custo | Custo de LLM por usuário/mês medido e com teto por plano (rate limit e quota) |
| RNF-11 | Observabilidade | Logs estruturados (JSON) com `trace_id` por mensagem, métricas (Prometheus), tracing do agente (LangSmith ou Langfuse self-hosted), alertas |
| RNF-12 | Qualidade | Cobertura ≥ 80% no domínio. Suíte de avaliação do agente (golden set) rodando no CI |
| RNF-13 | Portabilidade | Tudo em Docker. Ambiente local sobe com `docker compose up` usando emuladores |
| RNF-14 | Manutenibilidade | Arquitetura hexagonal: domínio independente de LangChain, WhatsApp e banco |
| RNF-15 | Backup | Backup diário do Postgres (retenção de 30 dias) fora da VPS. Restore testado mensalmente |
| RNF-16 | Fuso horário | Datas armazenadas em UTC e interpretadas no fuso do usuário |
