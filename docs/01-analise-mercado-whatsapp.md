# 01 — Análise de mercado: integração com WhatsApp

> Pesquisa feita em 13/10/2026. Preços e políticas da Meta mudam com frequência: **revalidar antes de cada release**.

## 1. A pergunta central

Há dois modelos possíveis para o usuário falar com a assistente:

| | **A) Número único do produto** (oficial) | **B) Número do próprio usuário** ("conversa comigo mesmo") |
|---|---|---|
| Como funciona | O SaaS tem 1 número WhatsApp Business (Cloud API). Todo usuário salva o contato "Assistente X" e conversa com ele. O backend identifica o usuário pelo `wa_id` (telefone) que chega no webhook. | O usuário escaneia um QR Code e o nosso servidor vira um "aparelho conectado" (linked device) da conta dele. A assistente lê e responde no chat "Você" (self-chat). |
| API | WhatsApp Cloud API (Meta) | Bibliotecas não oficiais: Baileys, Evolution API, WPPConnect, WAHA |
| Termos de uso | Permitido (com restrições de IA, ver §3) | **Viola os Termos do WhatsApp**: automação de conta pessoal |
| Risco de banimento | Baixo, se respeitar as políticas | **Alto**, e o ban cai na conta **pessoal do cliente**, o que é um desastre comercial e jurídico |
| Privacidade/LGPD | Só recebemos as mensagens enviadas para a assistente | Temos sessão com acesso a **todas as conversas pessoais** do cliente. Superfície de risco enorme |
| Escala | 1 webhook HTTP, stateless, horizontal | 1 sessão WebSocket com estado **por cliente**. 1.000 clientes = 1.000 sessões para manter vivas, reconectar e re-parear |
| Estabilidade | SLA da Meta | Quebra sempre que o WhatsApp muda o protocolo. Sessões caem e o cliente precisa reescanear o QR |
| Custo direto | Mensagens de serviço gratuitas (detalhes na §2) | "Grátis", mas o custo operacional cresce com o número de clientes |
| Recursos | Templates, botões, listas, mídia, status de leitura | Tudo, inclusive o que não deveria |

### Como o mercado faz hoje

Os produtos sérios de assistente pessoal/financeiro no WhatsApp (Brasil e exterior) usam **número único + API oficial**. O usuário se cadastra na web, vincula o telefone e conversa com o contato da marca. O self-chat via QR aparece em projetos hobby, automações "growth hacking" e ferramentas self-hosted, nunca em SaaS pago que precisa de previsibilidade.

### Decisão recomendada

**Modelo A, número único com a WhatsApp Cloud API oficial.** O usuário cadastra o próprio número **apenas como identidade** (para sabermos quem está falando), não como canal.

A integração fica atrás de uma interface (`MessagingProvider`). Em desenvolvimento local podemos usar o **número de teste gratuito da Meta**. Se um dia for preciso, dá para plugar a Evolution API para um protótipo interno sem reescrever o domínio.

## 2. Custos da Cloud API (modelo vigente)

- Desde 01/07/2025 a Meta cobra **por mensagem de template entregue**, não mais por conversa.
- **Mensagens livres (não template) dentro da janela de 24h** após a última mensagem do usuário: **gratuitas** para empresas comuns.
- **Templates de utilidade enviados dentro da janela aberta: gratuitos.**
- **Fora da janela** (ex.: lembrete de compromisso às 8h quando o usuário não falou nada nas últimas 24h), é obrigatório usar **template aprovado**. Referência Brasil: utilidade ≈ US$ 0,008/msg, marketing ≈ US$ 0,0625/msg. Conferir na rate card oficial; contas BRL faturadas pelo Facebook Brasil desde 07/2026.
- Hospedagem da Cloud API: gratuita (a Meta hospeda). Não precisamos de BSP (Twilio, Gupshup, Z-API etc.) na V1, o que elimina markup.

**Implicação de produto:** a interação iniciada pelo usuário tem custo ~zero de WhatsApp. O custo variável real está em **templates proativos** (lembretes, resumo diário) e no **LLM**. Isso vira regra de negócio: limite de lembretes proativos por plano (ver `03-regras-de-negocio.md`).

> Alguns fornecedores (ex.: Wati) afirmam que mensagens de serviço passariam a ser cobradas a partir de 01/10/2026. A documentação oficial consultada **não confirma** isso para empresas comuns. Monitorar.

## 3. ⚠️ Risco crítico: política da Meta para "AI Providers"

- Desde **15/01/2026**, os termos do WhatsApp Business **proíbem provedores cujo produto principal é um assistente de IA de propósito geral** (por isso ChatGPT, Perplexity e Copilot saíram do WhatsApp).
- Em mercados onde a Meta é legalmente obrigada a permitir esses provedores (**Brasil incluído, desde 11/03/2026**), eles podem operar, mas pagam **por cada mensagem não-template** (~US$ 0,069 por resposta segundo terceiros). Isso inviabilizaria a margem de uma assinatura barata.
- **Continuam permitidas** as automações de tarefas estruturadas: agendamentos, lembretes, confirmações, atendimento.

### Mitigação (requisito de arquitetura e de produto)

1. **Posicionar o produto como assistente de tarefas** (finanças pessoais, agenda e e-mail), não como "ChatGPT no WhatsApp". Isso vale para landing page, nome, descrição do WABA e templates.
2. **Guardrail de escopo no agente:** perguntas fora do domínio ("escreva um poema", "quem ganhou a copa") recebem recusa educada e um redirecionamento. Isso é RN, não detalhe.
3. **Respostas consolidadas:** 1 resposta por turno em vez de várias mensagens picadas. Reduz custo caso sejamos enquadrados.
4. Modelar no financeiro o **cenário pessimista** (enquadramento como AI Provider) antes de definir o preço da assinatura.
5. Ler os termos oficiais com um advogado antes do lançamento público.

## 4. Outras restrições importantes (fora do WhatsApp)

### Gmail: escopos restritos
Ler e-mails (`gmail.readonly`, `gmail.modify`, `gmail.metadata`) são **escopos restritos** do Google. Para um app público isso exige:
- verificação OAuth do app (semanas), e
- **avaliação de segurança CASA** anual por laboratório credenciado (custo na casa de centenas a milhares de US$/ano).

Em **modo de teste** o app aceita até **100 usuários**, o que basta para o beta fechado. Google Calendar usa escopos *sensíveis*: exige verificação, mas não CASA.
**Plano:** beta com até 100 usuários em modo teste. Iniciar a verificação e o CASA em paralelo ao Sprint 5.

### Microsoft (Outlook/Graph)
Fica para a V2. O processo de *publisher verification* é mais leve.

## 5. Fontes
- [Meta — Pricing on the WhatsApp Business Platform](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing)
- [Meta — Pricing policy for AI Providers](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/ai-providers/)
- [respond.io — WhatsApp general-purpose chatbots ban](https://respond.io/blog/whatsapp-general-purpose-chatbots-ban)
- [Business Standard — Meta bans AI chatbots from WhatsApp Business API](https://www.business-standard.com/technology/tech-news/meta-bans-ai-chatbots-from-whatsapp-business-api-chatgpt-to-shut-down-jan-2026-125102200335_1.html)
- [Wati — WhatsApp API pricing guide](https://www.wati.io/blog/whatsapp-api-pricing-guide)
- [Wati — 2026 pricing changes](https://www.wati.io/en/blog/whatsapp-business-api-pricing-changes-2026-what-meta-s-two-new-fees-actually-cost-you/)
