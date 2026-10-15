# 06 — Custo de IA por usuário

> Preços consultados em **13/10/2026** no [Vertex AI pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing) e na [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing). Câmbio usado: **US$ 1 = R$ 5,50** (Focus ~R$ 5,20 + IOF de cartão internacional + folga).
> Cálculo reproduzível: `python3 scripts/custos_ia.py`. Todos os parâmetros ficam no topo do script.

## 1. Modelos escolhidos

| Uso | Modelo | Input | Input em cache | Output | Por quê |
|---|---|---|---|---|---|
| **Texto** (conversa, tools, resumos, e-mail) | `gemini-3.1-flash-lite` | US$ 0,25 | US$ 0,025 | US$ 1,50 | O mais barato da geração atual, com tool calling. Disponível até pelo menos 07/05/2027 |
| **Imagem** (comprovante/nota fiscal) | `gemini-3.8-flash` | US$ 0,75 → **1,50** a partir de 01/01/2027 | 0,075 → 0,15 | US$ 3,75 → **7,50** | Mais preciso para extrair texto de foto. O cálculo usa o **preço cheio de 2027** |
| **Áudio** | Whisper rodando no nosso servidor | — | — | — | Sem custo de API. O custo de CPU entra na conta de infraestrutura |

*Preços em US$ por 1M de tokens, endpoint global.*

**Pontos que pesaram na escolha:**
- ⚠️ **Gemini 2.5 Flash e 2.5 Flash-Lite serão descontinuados em 20/10/2026.** Não use, mesmo sendo mais baratos.
- **Endpoint global, não regional.** Endpoints regionais (ex.: `southamerica-east1`) custam **+10%** na família Gemini 3. A LGPD não exige que os dados fiquem no Brasil; ela exige salvaguardas para a transferência internacional (cláusulas do contrato com o Google e menção na política de privacidade).
- **Alternativa testada:** `gemini-3.5-flash-lite` como modelo de texto ficou 35–40% mais caro sem ganho claro para o nosso caso.

## 2. Premissas de tokens

Elas precisam ser validadas no Sprint 2, medindo no Langfuse.

| Evento | Chamadas | Prefixo cacheável (system + tools) | Contexto variável | Output (resposta + raciocínio) |
|---|---|---|---|---|
| Mensagem comum (texto ou áudio transcrito) | 1,6 por turno (pedido de tool + resposta) | 2.500 / chamada | 1.590 / chamada (histórico, perfil, mensagem, resultado da tool) + 350 do classificador de escopo | 250 / chamada |
| Resumo diário (Pro) | 1 | 2.500 | 4.000 | 350 |
| Operação de e-mail (Pro) | 1,5 | 2.500 | 7.000 (corpo dos e-mails) | 500 |
| Foto de comprovante | 1 (modelo de imagem) | — | 1.820 (1.120 da imagem + prompt) | 550 |

**Custo unitário com cache:**

| Evento | Custo |
|---|---|
| Mensagem | **US$ 0,0014** (R$ 0,008) |
| Resumo diário | US$ 0,0016 |
| Operação de e-mail | US$ 0,0038 |
| Imagem | **US$ 0,0069** (R$ 0,038) |

## 3. Custo por usuário/mês

| Perfil | Uso no mês | Sem cache | Com cache | **Com cache + 25% de margem** |
|---|---|---|---|---|
| Essencial · típico | 300 msgs, 10 fotos | R$ 4,24 | R$ 2,75 | **R$ 3,44** |
| Essencial · teto do plano | 600 msgs, 30 fotos | R$ 8,85 | R$ 5,88 | **R$ 7,35** |
| Pro · típico | 700 msgs, 40 fotos, 30 resumos, 40 e-mails | R$ 11,90 | R$ 8,15 | **R$ 10,19** |
| Pro · teto do plano (RN-03 atual) | 1.200 msgs, 100 fotos, 30 resumos, 100 e-mails | R$ 22,14 | R$ 15,64 | **R$ 19,55** |
| Pro · teto antigo (descartado) | 2.000 msgs, 200 fotos, 30 resumos, 120 e-mails | R$ 36,71 | R$ 26,16 | R$ 32,70 🔴 |

O cache do prefixo é compartilhado entre todos os usuários, porque o system prompt e as tools são iguais para todo mundo. O armazenamento custa cerca de US$ 1,80 por mês para o produto inteiro, então é obrigatório ativar.

## 4. Conclusões

1. **O uso típico cabe com folga.** A IA custa cerca de 17% do preço no Essencial (R$ 3,44 de R$ 19,90) e 29% no Pro (R$ 10,19 de R$ 34,90).
2. **✅ Resolvido em 13/10/2026.** O Pro passou para **R$ 34,90**, com teto de 1.200 mensagens e 100 fotos. Com isso, nem quem esgota o plano dá prejuízo (doc 07, seção 3). O teto antigo (2.000/200) custava R$ 32,70 de IA, mais que os R$ 24,90 que o plano cobrava.
3. **A foto é o evento mais caro**: custa 5× uma mensagem. Duas otimizações:
   - mandar a foto primeiro para o `gemini-3.1-flash-lite` e só usar o `gemini-3.8-flash` quando a confiança da leitura for baixa;
   - reduzir a resolução da imagem (`media_resolution` média, cerca de 560 tokens) quando a foto for nítida.
4. **Custo de WhatsApp (será detalhado na etapa de infraestrutura).** Lembretes e resumos enviados fora da janela de 24h são templates pagos, cerca de US$ 0,008 cada. Por isso o teto do Pro caiu de 300 para 100 lembretes (cerca de R$ 4,40 no pior caso).

## 5. Como manter o custo sob controle (para implementação)
- Cache explícito do prefixo (system + tools) e histórico curto: as últimas 10 mensagens mais um resumo do que veio antes.
- `thinking` mínimo no Flash-Lite. O raciocínio é cobrado como output.
- O classificador de escopo barra pedidos fora do domínio antes da chamada principal.
- Contador de tokens por usuário (`usage_counters`) e alerta quando um usuário passar de 2× a média.
- Recalcular este documento sempre que o preço, o prompt ou o comportamento de uso mudar: basta rodar o script.
