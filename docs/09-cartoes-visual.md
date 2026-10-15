# 09 — Cartões visuais

> Decisão (13/10/2026): **não vamos usar arte nem logos dos bancos.** Todo cartão usa o **modelo Arclou** (componente `Web/BankCard` no Figma), com a **cor-padrão do banco** e o **nome do banco em texto**. O usuário pode trocar a cor, por exemplo para diferenciar dois cartões do mesmo banco. Isso dá o visual que a gente quer e reduz o risco com marcas registradas.

## Componente
- **Propriedades:**
  - `Cor` (variante): uma das 13 cores abaixo;
  - `Banco` (texto): nome que aparece no topo do cartão;
  - `Last digits` (texto): `•••• •••• •••• 1234`, com os 4 últimos dígitos opcionais;
  - `Holder` (texto): nome do usuário.
- **Camadas:**
  - `Art`: gradiente da cor;
  - `Pattern` / `Accent`: textura opcional de algumas cores;
  - `Sheen`: brilho;
  - chip, contactless, número, titular e "CRÉDITO".
- **Cor do texto automática:** clara sobre cores escuras e escura sobre **Amarelo** e **Prata**.

## Cores e padrão por banco

As cores foram amostradas das imagens de referência (zip "Sem título", 10 cartões).

| Cor (variante) | Gradiente | Texto | Detalhe | Banco que usa como padrão |
|---|---|---|---|---|
| Roxo | `#A855D3` → `#7804A4` | branco | — | Nubank |
| Ciano | `#1FBDEA` → `#0BCED0` | branco | — | Neon |
| Laranja | `#EE661A` → `#F2691A` | branco | curva `#E4500E` no canto | Itaú |
| Vermelho e azul | `#CD1646` → `#94326B` → `#323C90` | branco | linhas diagonais | Bradesco |
| Preto | `#1A1A1A` → `#0B0B0B` | `#D4D4D4` | textura de traços | Inter |
| Pink | `#EF60B0` → `#D31C69` | branco | — | C6 Bank |
| Vermelho | `#FF3A2E` → `#E8170C` | branco | — | Santander |
| Amarelo | `#F3DF34` → `#F2E43B` | `#0B4C9C` | linhas sutis | Banco do Brasil |
| Petróleo | `#00607F` → `#005574` | branco | faixa superior | Caixa |
| Grafite | `#3A3B3A` → `#1E1C1A` | branco | — | Mercado Pago |
| Azul Arclou | `#2549AB` → `#0B1026` | branco | — | Outro banco (padrão) |
| Verde | `#10B981` → `#047857` | branco | — | (só escolha do usuário) |
| Prata | `#EEF0F3` → `#AEB4BD` | `#1F2937` | — | (só escolha do usuário) |

O usuário também pode escolher **Personalizada** (seletor de cor livre). Nesse caso o app calcula a cor do texto pelo contraste WCAG: branco se o contraste for ≥ 4,5:1, senão `#0B1026`.

## Regras
- Ao escolher o banco, a cor-padrão é aplicada e a interface mostra "Ciano · padrão do Neon". Trocar a cor não muda o banco.
- **Nunca** usar logotipo, bandeira (Visa/Mastercard/Elo) nem arte oficial dos bancos.
- Dados do cartão: só apelido, banco, cor, fechamento, vencimento, limite (opcional) e os 4 últimos dígitos (opcional). **Nunca** número completo, CVV, validade ou senha (RN-10.4c).

## Implementação (front-end)
- **Tokens:** `card.skin.<nome>.{from,via?,to,text,pattern}` em JSON, gerados a partir desta tabela.
- **Componente React:** `<BankCard skin="ciano" bank="Neon" last4="7310" holder="Marina Costa" />`. Para cor personalizada, usar `skin="custom"` com `color="#hex"`.
- **Banco de dados:** `credit_cards.color_skin` (enum das 13 cores + `custom`) e `credit_cards.custom_color` (`#RRGGBB`, nulo quando não é personalizada).
