# 07 — Infraestrutura e custo total por usuário

> Cotação de 13/10/2026. Cálculo reproduzível: `python3 scripts/custos_infra.py`. Ele usa o custo de IA do doc 06.
> Itens marcados **(est.)** vêm de estimativas de mercado e precisam ser confirmados no fornecedor.

> **Atualização de 15/10/2026:** durante o desenvolvimento, staging e production rodam numa VM do GCE desligada fora do horário comercial (~US$ 45/mês, doc 12 §2). Antes do beta, production ganha uma VM própria ligada 24/7 (S14-01). Os cenários abaixo ainda usam a VPS Hostinger e serão recalculados quando a VM de produção for dimensionada.

## 1. A VPS atual

| Item | Valor |
|---|---|
| Provedor | Hostinger (IPv6 `2a02:4780::/32`, hostname `srv…`) |
| Plano provável | **KVM 2: 2 vCPU, 8 GB RAM, 100 GB NVMe** (disco de 95,8 GB). Confirmar com `nproc && free -h` |
| SO | Ubuntu 24.04.4 LTS. Há 101 atualizações pendentes e o servidor pede reboot. Atualizar antes do Sprint 0 |
| Uso hoje | 36% da RAM já ocupada. **Mapear o que está rodando (`docker ps`, `systemctl`)** antes de reservar memória para a Arclou |
| Preço | ~R$ 69,99/mês na renovação **(est.)** |

### Distribuição de memória proposta (8 GB)

| Serviço | RAM |
|---|---|
| Caddy (TLS) | 50 MB |
| API FastAPI | 300 MB |
| Workers (2×) | 600 MB |
| Web Next.js | 300 MB |
| PostgreSQL + pgvector | 1 GB |
| Redis | 150 MB |
| **Whisper (faster-whisper `small`, int8, CPU)** | **1 GB** + 2 vCPU em rajadas |
| Sistema + folga | ~1,5 GB |
| **Total da Arclou** | **~5 GB** |

**Atenção:** com 36% (cerca de 2,9 GB) já em uso, a máquina fica no limite. Se o que roda hoje continuar, considere subir para o KVM 4.

### Capacidade do Whisper na VPS
Premissas: 40% das mensagens chegam por áudio, cada uma com ~8 s, e o modelo `small` int8 processa em cerca de 0,4 s de CPU por segundo de áudio (~3 s por mensagem com os 2 núcleos).

| Usuários ativos | Áudios por dia | CPU no horário de pico |
|---|---|---|
| 300 | ~1.800 | ~25% (tranquilo) |
| ~600 | ~3.600 | ~50%. **Limite confortável da KVM 2** |
| 1.000 | ~6.000 | ~80%: fila e lentidão. Upgrade para KVM 4 (~R$ 140/mês, est.) |

> **Alternativa a avaliar:** mandar o áudio direto para o `gemini-3.1-flash-lite`, que cobra US$ 0,50 por 1M tokens de áudio (25 tokens/s). Um áudio de 8 s custa **US$ 0,0001**. Um usuário Pro típico sairia por cerca de **R$ 0,15/mês**, e 1.000 usuários por cerca de R$ 150/mês. Isso tira o processamento pesado da VPS e adia o upgrade. O ideal é manter o Whisper local como padrão e usar o Gemini quando a fila crescer.

## 2. Custos fixos mensais por cenário

| Item | Beta · 50 | Lançamento · 300 | Crescimento · 1.000 |
|---|---|---|---|
| VPS Hostinger | R$ 69,99 (KVM 2) | R$ 69,99 (KVM 2) | R$ 139,99 (KVM 4, est.) |
| Domínio .com.br (R$ 40/ano) | R$ 3,33 | R$ 3,33 | R$ 3,33 |
| Backup off-site (Google Cloud Storage) | R$ 2,00 | R$ 3,00 | R$ 7,00 |
| Linha/chip dedicado do WhatsApp | R$ 15,00 | R$ 15,00 | R$ 15,00 |
| Google CASA Tier 2 (Gmail para mais de 100 usuários; US$ 540/ano, est.) | — (modo teste) | R$ 247,50 | R$ 247,50 |
| Langfuse (traces do agente) | grátis (Hobby, amostragem) | grátis | R$ 159,50 (Core) ou self-host |
| Firestore | grátis (50 mil leituras e 20 mil gravações/dia) | grátis | ~R$ 10 |
| Firebase Auth, Sentry, WhatsApp Cloud API (hospedagem) | grátis | grátis | grátis |
| **Total** | **R$ 90/mês** | **R$ 339/mês** | **R$ 582/mês** |
| **Por usuário** | R$ 1,81 | R$ 1,13 | R$ 0,58 |

**Itens fora da infraestrutura,** que entram no preço como custo do negócio: contador (~R$ 200–400/mês), CNPJ, marketing e aquisição de clientes, advogado para os termos de uso e a LGPD.

## 3. Custo variável e margem por assinante

Preços definidos em 13/10/2026 (RN-03): **Essencial R$ 19,90 · Pro R$ 34,90**.

| Uso típico | Essencial (R$ 19,90) | Pro (R$ 34,90) |
|---|---|---|
| IA (doc 06, com 25% de margem) | R$ 3,44 | R$ 10,19 |
| WhatsApp: templates fora da janela de 24h (US$ 0,008 cada, est.) | R$ 0,66 (15 msgs) | R$ 1,98 (45 msgs) |
| Gateway Asaas, cartão (2,99% + R$ 0,49) | R$ 1,09 | R$ 1,53 |
| Impostos: Simples Anexo III, 6% (pior caso Anexo V, 15,5%) | R$ 1,19 (R$ 3,08) | R$ 2,09 (R$ 5,41) |
| Estornos (1%) | R$ 0,20 | R$ 0,35 |
| **Margem de contribuição** | **R$ 13,32 (67%)**, pior caso R$ 11,43 | **R$ 18,75 (54%)**, pior caso R$ 15,44 |

**Usuário que esgota o plano** (Essencial: 600 msgs / 30 fotos / 60 lembretes; Pro: 1.200 / 100 / 100):

| Plano | Margem com imposto de 6% | Margem com imposto de 15,5% |
|---|---|---|
| Essencial | R$ 7,43 | R$ 5,54 |
| Pro | R$ 6,97 | R$ 3,66 |

Nenhum perfil dá prejuízo.

**Plano Casal (R$ 49,90, 2 pessoas · decisão de 14/10/2026):**

| Cenário | Margem com imposto de 6% | Margem com imposto de 15,5% |
|---|---|---|
| Uso típico (2× Pro típico) | **R$ 20,08 (40%)** | R$ 15,34 (31%) |
| Os dois esgotando o plano (900 msgs / 60 fotos / 60 lembretes por pessoa) | R$ 11,86 | R$ 7,12 |

Com as quotas do Pro, esgotar daria prejuízo (−R$ 3,48). Por isso o Casal tem quotas próprias por pessoa (RN-03).

**Preço de fundador** (RN-03.4, Pro a R$ 24,90 por 12 meses): margem no uso típico de ~R$ 9,75 (39%).

## 4. Resultado por cenário

Considera 50% de assinaturas no Essencial, 30% no Pro e 20% no Casal, uso típico e imposto de 6% (rode o script para os valores atualizados).

| Cenário | Receita | Custos variáveis | Infra fixa | **Resultado** | Ponto de equilíbrio |
|---|---|---|---|---|---|
| Início · 5 usuários | ~R$ 130 | ~R$ 52 | R$ 90 | **~−R$ 13** (fase de validação) | — |
| Beta · 50 | R$ 1.520 | R$ 705 | R$ 90 | **R$ 725 (48%)** | ~6 assinantes |
| Lançamento · 300 | R$ 9.120 | R$ 4.229 | R$ 339 | **R$ 4.552 (50%)** | ~21 assinantes |
| Crescimento · 1.000 | R$ 30.400 | R$ 14.097 | R$ 582 | **R$ 15.721 (52%)** | ~36 assinantes |

## 5. Gatilhos para evoluir a infraestrutura

Investir só quando o número pedir:

| Gatilho | Ação | Custo adicional |
|---|---|---|
| ~100 usuários com Gmail conectado | Auditoria CASA Tier 2 (sair do modo teste do Google) | ~R$ 250/mês (anual) |
| ~500–600 usuários ativos ou fila de áudio > 10 s | KVM 4 **ou** enviar áudios excedentes ao Gemini Flash-Lite | ~R$ 70/mês ou ~R$ 0,15/usuário Pro |
| ~1.000 usuários | Langfuse pago (ou self-host na KVM 4) | ~R$ 160/mês |

## 6. Pendências
1. **Gateway:** confirmar a taxa do Pix Automático. Para ticket baixo, o cartão (~R$ 1,10–1,53) sai mais barato que o Pix avulso do Asaas (R$ 1,99 fixo).
2. **Impostos:** planejar o Fator R com o contador. A diferença entre os anexos III e V é de R$ 2–3 por assinante.
3. **Antes do Sprint 0:** atualizar e reiniciar a VPS, mapear o que já roda nela e confirmar CPU e RAM.
