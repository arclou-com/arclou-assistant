# 11 — Central de Ajuda

> A documentação para o **cliente final**: um lugar só para tirar dúvidas sobre como a Arclou funciona, no estilo da documentação do Google Cloud.
> Design: página **"Central de Ajuda · Docs"** no Figma (fileKey `PJ7SvIZo5iVL4GqUoT0xAi`). URL de produção prevista: `ajuda.arclou.com.br`.

## ⚠️ Regra de manutenção (obrigatória)
**Toda alteração em algo que está documentado precisa ser refletida na Central de Ajuda no mesmo trabalho:**
- **O que conta como alteração:** regra de negócio, preço, quota, modo da Casa, fluxo ou tela;
- **Como atualizar:**
  1. encontre o artigo afetado nas tabelas da seção 2;
  2. atualize o texto, os exemplos e as capturas;
  3. troque a data de "Última atualização";
  4. adicione o item em "Atualizado recentemente" na página inicial.

Um PR que muda uma RN/RF listada nas tabelas da seção 2 sem tocar no conteúdo da Central **não passa no review**. O check de CI está descrito na seção 5.

---

## 1. Pontos de entrada
| Onde | Como | Tela |
|---|---|---|
| Painel (desktop) | Item **Central de ajuda** no menu lateral | Web/Sidebar (todas as telas do painel) |
| Painel (mobile) | Linha **Central de ajuda** na aba Conta | M05 |
| Contexto | Links "Como funciona…?" que abrem o artigo certo | HJ01, H01, H03, MHJ01 |
| WhatsApp | Mandar **"ajuda"** → menu com "Ver assuntos" e "Abrir Central de Ajuda" | DOCW01 |
| WhatsApp | Pergunta livre ("como funciona a conta conjunta?") → resposta curta com o **link do artigo** | DOCW01 |
| Central | Busca com "Resposta rápida" no topo e resultados por assunto | DOC12 |

## 2. Estrutura e rastreabilidade (todos os artigos)
Cada item do menu lateral tem a sua página. No Figma, a página "Central de Ajuda · Docs" tem **uma linha horizontal por aba**, com os artigos da esquerda para a direita na ordem do menu. **Quando um artigo novo entrar, ele vai para a linha da aba dele, na posição do menu.**

A coluna **Depende de** diz o que revisar quando algo mudar (regra de manutenção).

### Início (4 telas)
| Tela | Conteúdo | Depende de |
|---|---|---|
| DOC01 | Página inicial: busca, 6 assuntos, "Atualizado recentemente", "Perguntar no WhatsApp" | Toda mudança relevante |
| DOC12 | Resultados da busca com "Resposta rápida" | Conteúdo dos artigos |
| MDOC01 | Início (mobile) | — |
| DOCW01 | "ajuda" no WhatsApp, com o link do artigo | RF-116 |

### Primeiros passos (6)
| Tela | Artigo | Slug | Depende de |
|---|---|---|---|
| PP01 | Criar conta e teste grátis | `/primeiros-passos/criar-conta` | RN-02.1 · telas C02, C06 |
| DOC02 | Vincular o WhatsApp | `/primeiros-passos/vincular-whatsapp` | RN-01 · tela D03 |
| PP03 | Conectar agenda e e-mail | `/primeiros-passos/conectar-google` | RN-06.5, RN-07 · telas D04, E09 |
| PP04 | Sua primeira mensagem | `/primeiros-passos/primeira-mensagem` | RN-04.1, RN-04.4 |
| DOC11 | Todos os comandos do WhatsApp | `/referencia/comandos` | RN-04 a RN-11 |
| PP05 | Limites do seu plano | `/primeiros-passos/limites` | RN-03, RN-03.1–03.3 |

### Finanças (9)
| Tela | Artigo | Depende de |
|---|---|---|
| DOC03 | Registrar gastos pelo WhatsApp | RN-03, RN-04.2/04.3, RN-05 · tela F01 |
| FI02 | Receitas e salário | RN-09.2 · tela F02b |
| FI03 | Limites por categoria | RN-05.5, RN-09.3, RN-09.4 · tela F02 |
| FI04 | Contas fixas e cartões | RN-10.1–10.3, RN-10.4c, RN-10.6, RN-10.9 · telas F04, F05c |
| FI05 | Compras parceladas | RN-10.4, RN-10.4b, RN-10.5, RN-10.5b · telas F05, F05b |
| FI06 | Metas | RN-09.5 · tela F03 |
| FI07 | Quanto posso gastar | RN-09.1, RN-09.6, RN-09.7, RN-10.7 |
| FI08 | Comandos de finanças | RN-05, RN-09, RN-10 |
| FI09 | Categorias | RN-05.3 |

### Casa (plano Casal) (13)
| Tela | Artigo | Depende de |
|---|---|---|
| CA01 | Visão geral do plano Casal | RN-03, RN-11.1, RN-11.13 · tela HJ01 |
| DOC04 | Escolher o modo de dinheiro | RN-11.13 · tela H03 |
| DOC05 | Modo Dinheiro junto | RN-11.13–11.15 · telas HJ01, HJ01b |
| DOC06 | Modo Separado e quem deve quem | RN-11.3–11.7 · telas H01, H01c |
| DOC07 | Modo Misto | RN-11.16, RN-11.17 |
| CA06 | O que o parceiro vê | RN-11.3, RN-11.4, RN-11.15 · tela H01d |
| CA07 | Convidar o parceiro | RN-11.2 · telas H02, J02 |
| CA08 | Acertar contas | RN-11.7 · tela H01b |
| CA09 | Conferir o saldo da conjunta | RN-11.14 · tela HJ01c |
| DOC08 | Sair da Casa | RN-11.11, RN-11.12 · telas HS01, HS02, HS04 |
| CA11 | Comandos da Casa no WhatsApp | RN-11 |
| CA12 | Perguntas frequentes | RN-11 |
| MDOC05 | Modo Dinheiro junto (mobile) | igual ao DOC05 · tela MHJ01 |

### Agenda e e-mail (6)
| Tela | Artigo | Depende de |
|---|---|---|
| AG01 | Criar e consultar eventos | RN-04.2, RN-06.1, RN-06.6 |
| AG02 | Lembretes | RN-06.2–06.4, RN-10.9, RN-03 |
| AG03 | Resumo diário | RN-03 (Pro/Casal) |
| AG04 | Resumir e buscar e-mails | RN-07.2–07.4, RN-04.6 |
| AG05 | Responder e enviar e-mails | RN-07.1 |
| AG06 | Comandos de agenda e e-mail | RN-06, RN-07 |

O item "Conectar agenda e e-mail" do menu desta aba abre o PP03.

### Planos e pagamento (6)
| Tela | Artigo | Depende de |
|---|---|---|
| DOC09 | Comparar planos | RN-03 · tela C03 |
| PL02 | Teste grátis de 7 dias | RN-02.1 |
| PL03 | Formas de pagamento | RN-02.1 · tela C04 |
| PL04 | Trocar de plano | RN-11.2 (crédito do convidado), billing · tela D06 |
| PL05 | Cancelar a assinatura | RN-02.5, RN-11.11 |
| PL06 | Pagamento recusado | RN-02.3, RN-02.4 · tela C05 |

### Privacidade e segurança (5)
| Tela | Artigo | Depende de |
|---|---|---|
| DOC10 | O que a Arclou nunca pede | RN-07, RN-09.7, RN-10.4c · tela D07 |
| PV02 | Quais dados guardamos | RN-07.2, RN-08.1, RN-08.4–08.6, RN-09.9 |
| PV03 | Exportar meus dados | RN-08.2 · tela D07 |
| PV04 | Excluir minha conta | RN-08.3, RN-11.12 |
| PV05 | Meta, Google e seus dados | RN-01, RN-06.3, RN-08.5, política da Meta (doc 01) |

**Total: 49 telas** (44 artigos desktop, 2 mobile, busca, início e WhatsApp).

## 3. Guia de estilo (padrão Google Cloud)
- **Título com verbo e tarefa:** "Vincular o seu WhatsApp", não "Vínculo".
- **Abertura:** uma frase que diz o que é e para quem é.
- **Antes de começar:** um aviso de Observação com os pré-requisitos.
- **Passos numerados**, um verbo por passo, com o nome do botão em negrito: "Toque em **Conferir saldo**".
- **Abas Painel | WhatsApp:** o mesmo passo-a-passo nos dois canais.
- **Avisos:** Observação (informação), Dica (atalho) e Importante (risco ou ação irreversível). No máximo 3 por artigo.
- **Exemplo de conversa:** todo artigo tem pelo menos 1, com o botão "Copiar exemplo".
- **Capturas** das telas Light do protótipo, com a legenda "Figura N." e o caminho no painel. Os números precisam bater com os da tela.
- **Tabelas** para comparar e para referência. A primeira coluna é o que o usuário procura.
- **"Nesta página"** à direita (todos os H2), **"Próximas etapas"** no fim, **"Esta página foi útil?"** e a data de atualização.
- **Tom:** você, frases curtas, sem jargão ("conta conjunta", não "household account"). As limitações aparecem com honestidade (ex.: "a Arclou não acessa o banco").

## 4. Implementação (proposta)
- **Conteúdo como código:** os artigos ficam em Markdown com frontmatter em `help/` no repositório:
  - campos do frontmatter: `title`, `slug`, `tab`, `updated`, `depends_on: [RN-11.13, ...]`, `screens: [HJ01]`;
  - as capturas ficam em `help/img/`;
  - o painel (React) renderiza em `ajuda.arclou.com.br`, com SSR para SEO, porque a Central também serve como aquisição.
- **Busca:** os artigos são indexados no **pgvector**, que já está na stack, por trecho. A "Resposta rápida" é gerada **só** a partir dos trechos encontrados, com o artigo citado. Sem trecho relevante, não há resposta rápida.
- **Agente no WhatsApp:** tool `search_help(query) → [{title, slug, snippet}]`.
  - Perguntas sobre "como funciona" respondem em até 3 frases, mais o link do artigo (mensagem interativa com botão de URL, dentro da janela de 24h).
  - "ajuda" devolve uma mensagem de lista com os 6 assuntos.
- **Feedback:** "Esta página foi útil?" grava `help_feedback(slug, vote, comment?)`. Artigos com mais de 30% de "Não" entram na revisão semanal.
- **Deep links:** os links contextuais do painel usam o slug (ex.: `/casa/dinheiro-junto`) e abrem na âncora certa.

## 5. Check de CI (garante a regra de manutenção)
O script `scripts/check_help_sync.py` cruza os IDs de RN/RF alterados no diff de `docs/02` e `docs/03` com o `depends_on` dos artigos em `help/`. Se uma regra listada mudou e nenhum artigo que depende dela foi tocado, o CI falha com a lista dos artigos a revisar.

## 6. Telas no Figma
- **Página:** "Central de Ajuda · Docs", com uma linha por aba (seção 2).
- **Componentes:** Docs/Header, Docs/Tab, Docs/NavItem, Docs/Callout (Observação, Dica, Importante) e Docs/Feedback.
- **Flows do protótipo:** **Central de Ajuda · Desktop**, **· Mobile** e **· pelo WhatsApp**.
  - Todo item do menu lateral, toda aba, todo "Próximas etapas" e todo resultado de busca abre o artigo correspondente.
  - No painel, os pontos de entrada abrem a Central pelo link do protótipo.
