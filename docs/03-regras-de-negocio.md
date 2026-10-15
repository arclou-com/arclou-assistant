# 03 — Regras de negócio

> Valores numéricos (limites, preços, prazos) são **propostas iniciais** e devem ficar configuráveis (tabela `plans` / env), nunca hardcoded.

## RN-01 Identidade e vínculo
- **RN-01.1** Um número de WhatsApp (`wa_id`) pertence a **no máximo uma** conta ativa. Uma conta tem **um** número vinculado.
- **RN-01.2** O código de vínculo é de uso único, expira em **30 minutos** e fica limitado a 5 tentativas inválidas por número por hora.
- **RN-01.3** Mensagem de número não vinculado → resposta fixa com link de cadastro, **sem chamar o LLM** (custo zero). No máximo 1 resposta por número a cada 24h, para evitar spam.
- **RN-01.4** Ao trocar o número, o anterior é desvinculado e o histórico de conversa permanece na conta (não no número).

## RN-02 Assinatura e acesso
- **RN-02.1 (decisão de 14/10/2026)** Trial de **7 dias** com todas as funcionalidades do plano escolhido, **com meio de pagamento cadastrado**: cartão de crédito ou autorização de Pix Automático. Nada é cobrado no início.
  - 1 trial por CPF, telefone, e-mail **e cartão** (fingerprint do gateway). Quem já usou não ganha outro.
  - Aviso por e-mail e WhatsApp **2 dias antes** da primeira cobrança, com o link para cancelar.
  - Cancelou durante o trial: nada é cobrado, e o acesso termina no fim dos 7 dias.
  - A primeira cobrança falhou no fim do trial: segue o fluxo de `past_due` (RN-02.3).
  - Preços mantidos (decisão de 14/10/2026): Pro a R$ 34,90 no lançamento, sem teste a R$ 39,90.
- **RN-02.2** Status possíveis: `trialing → active → past_due → suspended → canceled`.
- **RN-02.3** `past_due`: o pagamento falhou. A assistente segue funcionando por **3 dias de carência** e avisa o usuário uma vez por dia.
- **RN-02.4** `suspended`: a assistente só responde com o link de regularização. **Dados preservados por 90 dias.**
- **RN-02.5** `canceled`: o acesso vai até o fim do período já pago. Depois de 90 dias sem reativação, os dados são anonimizados/excluídos (avisar com 7 dias de antecedência por e-mail).
- **RN-02.6** O status da assinatura é a fonte de verdade para o gate de acesso, checado **antes** de qualquer chamada ao LLM.

## RN-03 Planos e quotas
> Definidos em 13/10/2026 a partir de `docs/06-custos-ia.md` e `docs/07-custos-infra.md`. Nenhum perfil de uso, nem quem esgota o plano, gera margem negativa.

| | Essencial | Pro | Casal (2 pessoas) |
|---|---|---|---|
| **Preço mensal** | **R$ 19,90** | **R$ 34,90** | **R$ 49,90** |
| **Preço anual** (2 meses grátis) | R$ 199/ano | R$ 349/ano | R$ 499/ano |
| Mensagens processadas/mês | 600 | 1.200 | 900 por pessoa |
| Gastos | ✓ | ✓ | ✓ |
| Agenda + lembretes | ✓ | ✓ | ✓ |
| E-mail (Gmail) | — | ✓ | ✓ (cada um o seu) |
| Lembretes proativos fora da janela 24h/mês | 60 | 100 | 60 por pessoa |
| Leitura de imagem (comprovantes)/mês | 30 | 100 | 60 por pessoa |
| Resumo diário | — | ✓ | ✓ |
| Casa compartilhada (RN-11) | — | — | ✓ |

- **RN-03.4 Preço de fundador:** os 50 primeiros assinantes do Pro pagam **R$ 24,90/mês travados por 12 meses** (cupom `FUNDADOR`, um por CPF). Depois disso, o valor passa para a tabela vigente, com aviso 30 dias antes.

- **RN-03.1** Ao atingir 80% da quota, avisar o usuário. A 100%, responder com oferta de upgrade e só aceitar comandos sem LLM (`ajuda`, `resumo` simples).
- **RN-03.2** Rate limit anti-abuso: no máximo **20 mensagens/minuto** por usuário. O excedente é ignorado com um aviso único.
- **RN-03.3** Quotas resetam no aniversário da assinatura.

## RN-04 Comportamento do agente
- **RN-04.1 Escopo:** a assistente atua **apenas** em finanças pessoais, agenda/lembretes, e-mail e uso da própria conta. Fora disso: recusa curta + exemplos do que ela faz (ver doc 01 §3).
- **RN-04.2 Confirmação obrigatória** (pergunta + resposta "sim" explícita) para: enviar e-mail, excluir ou alterar evento com convidados, excluir gasto, excluir mais de 1 item, alterar orçamento.
- **RN-04.3** Ações de criação simples (registrar gasto, criar lembrete, criar evento sem convidados) são executadas direto, e a resposta mostra o que foi feito e oferece "desfazer".
- **RN-04.4 Desfazer:** a última ação reversível pode ser desfeita em até **10 minutos**.
- **RN-04.5 Ambiguidade:** se faltar dado essencial (valor, data/hora), perguntar. Se faltar dado secundário, usar o padrão (data = hoje, categoria = inferida, pagamento = padrão do usuário).
- **RN-04.6 Conteúdo externo** (corpo de e-mail, texto em imagem) é dado, nunca instrução. Ele nunca dispara ação sem pedido do usuário.
- **RN-04.7** Uma resposta consolidada por turno (no máximo 1 mensagem; 2 só quando houver mídia).
- **RN-04.8** A assistente nunca inventa dados: se a consulta não retornar nada, diz isso.

## RN-05 Gastos
- **RN-05.1** Valores armazenados em **centavos (inteiro)** + moeda (ISO 4217). Nunca `float`.
- **RN-05.2** Data do gasto = data informada pelo usuário no fuso dele. Sem data informada, vale a data de recebimento da mensagem.
- **RN-05.3** Categorias padrão: Alimentação, Mercado, Transporte, Moradia, Saúde, Educação, Lazer, Assinaturas, Compras, Contas, Outros. O usuário pode criar até 30 categorias próprias.
- **RN-05.4** Parcelamento: N lançamentos com `installment_group_id` e valor total/N (resto de centavos na 1ª parcela).
- **RN-05.5** Alertas de orçamento: 80% e 100%, **uma vez** por categoria por mês.
- **RN-05.6** Gasto extraído de imagem sempre pede confirmação ("Registrei R$ 87,40 em Mercado (Carrefour), certo?").
- **RN-05.7** Exclusão é *soft delete* (permite desfazer e auditar). O expurgo físico acontece junto com a exclusão da conta.

## RN-06 Agenda e lembretes
- **RN-06.1** O Google Calendar é a fonte de verdade dos eventos (não duplicamos eventos no nosso banco; guardamos só os IDs relevantes para lembretes).
- **RN-06.2** Lembrete padrão: 30 min antes, configurável (0 = desligado).
- **RN-06.3** Lembrete com janela de 24h aberta → mensagem livre (grátis). Janela fechada → template de utilidade aprovado (consome quota RN-03).
- **RN-06.4** Horário de silêncio: entre 22h e 7h (fuso do usuário) nada proativo é enviado, exceto lembretes que o próprio usuário marcou nesse horário.
- **RN-06.5** Token OAuth revogado/expirado → avisar o usuário uma vez com link de reconexão e desativar as tools de agenda até lá.
- **RN-06.6** Horários relativos ("amanhã", "sexta") são resolvidos no fuso do usuário, e a resposta sempre confirma a data absoluta ("sexta, 17/10 às 15h").

## RN-07 E-mail
- **RN-07.1** **Nunca enviar e-mail sem confirmação explícita** mostrando destinatário, assunto e corpo.
- **RN-07.2** Não armazenamos o corpo de e-mails. Só metadados mínimos (ID, remetente, assunto) com retenção de 7 dias, para referências como "responde aquele e-mail".
- **RN-07.3** Anexos: fora da V1 (somente menciona que existem).
- **RN-07.4** Na V1 só lemos; o envio usa a conta do usuário. Nenhuma exclusão de e-mail.

## RN-08 Privacidade e dados (LGPD)
- **RN-08.1** Histórico de conversa: retenção de **12 meses** (configurável). Memória de longo prazo (fatos) até ser excluída pelo usuário ("esquece que…").
- **RN-08.2** Exportar dados: JSON/CSV gerado em até 48h, com link temporário.
- **RN-08.3** Excluir conta: revoga os tokens OAuth, apaga Postgres, Firestore e mídias em até 15 dias, e mantém só o mínimo fiscal (faturas).
- **RN-08.4** Mídias recebidas (áudio/imagem) são processadas e **descartadas em até 24h**.
- **RN-08.5** Prompts e respostas enviados ao Vertex AI: configurar a região (`southamerica-east1` quando o modelo estiver disponível) e garantir que os dados não sejam usados para treino (padrão do Vertex).
- **RN-08.6** Admin não lê conversas dos usuários, salvo com consentimento em ticket de suporte (acesso auditado).

## RN-09 Inteligência financeira
- **RN-09.1 Disponível para gastar** (mês corrente) = receitas previstas do mês − **compromissos ainda não pagos no mês** (recorrentes a vencer + faturas de cartão que vencem no mês, incluindo as parcelas; ver RN-10) − reserva mensal das metas − gastos variáveis já registrados. Uma compra no cartão entra no disponível **no momento da compra** (o dinheiro já está comprometido), mas só é paga na fatura. **Valor diário sugerido** = disponível ÷ dias restantes no mês. Se o disponível ficar negativo, a assistente avisa e sugere onde cortar (as categorias variáveis que mais cresceram).
- **RN-09.2 Receitas recorrentes:** a renda fixa gera um lançamento **previsto** todo mês. Formas de definir o dia:
  - **dia fixo** (1–31; em meses curtos, usa o último dia);
  - **N-ésimo dia útil** (seg–sex, descontando feriados nacionais).

  Se o dia fixo cair em fim de semana ou feriado, a regra padrão é **antecipar para o dia útil anterior** (configurável: antecipar ou adiar). Uma renda de valor variável usa a média dos últimos 3 recebimentos como previsão. No dia previsto, a assistente pergunta "o salário caiu?". O usuário confirma ou ajusta o valor ("veio 4.850"), e o lançamento passa de previsto para recebido. Receita extra só entra quando é registrada.
- **RN-09.3 Limites:** limite geral ≥ soma dos limites por categoria. Categoria sem limite não gera alerta. Projeção de estouro = gasto médio diário da categoria no mês × dias restantes + gasto atual. Só alerta quando a projeção passar de 110% do limite e faltarem pelo menos 5 dias para o fim do mês.
- **RN-09.4 Orçamento sugerido (Pro):** com base na renda, propõe 50% necessidades, 30% desejos e 20% metas/reserva. As categorias são mapeadas para esses grupos e o usuário pode ajustar os percentuais e o mapeamento.
- **RN-09.5 Metas (Pro):** aporte mensal sugerido = (valor da meta − valor guardado) ÷ meses restantes. A meta fica "Atrasada" quando o guardado está mais de 10% abaixo do esperado para a data. No máximo 10 metas ativas.
- **RN-09.6 "Posso comprar?" (Pro):** a resposta sempre mostra os números (disponível depois da compra, % do limite da categoria, efeito nas metas). Se a compra for parcelada, considera as parcelas nos meses seguintes. A resposta é **informativa**, nunca uma ordem ("cabe no seu orçamento" / "deixaria o mês negativo em R$ X").
- **RN-09.7 Orientações:** são educativas e baseadas nos dados do próprio usuário. **A Arclou não recomenda investimentos, produtos financeiros, crédito nem instituições específicas** (atividade regulada pela CVM e pelo Bacen). Pedidos desse tipo recebem uma resposta neutra e a sugestão de procurar um profissional certificado. No máximo 1 insight proativo por semana no Pro, dentro do horário permitido (RN-06.4) e com opt-in (RF-06).
- **RN-09.8 Insights automáticos** (gatilhos, todos com um valor mínimo de relevância):
  - categoria pelo menos 25% acima da média dos 3 meses anteriores **e** pelo menos R$ 50 de diferença;
  - nova cobrança recorrente detectada (mesmo valor e descrição em 2 meses seguidos);
  - gasto único maior que 3× o ticket médio da categoria;
  - meta atrasada (RN-09.5).
- **RN-09.9 Privacidade:** dados financeiros nunca são usados para publicidade nem compartilhados. Agregados anônimos só com consentimento explícito.

## RN-10 Recorrentes, cartões e parcelamentos
- **RN-10.1 Gasto recorrente:** gera um lançamento **previsto** por mês no dia de vencimento (mesma regra de dia útil da RN-09.2). Quando o pagamento é registrado (ou confirmado: "paguei a luz"), o previsto vira realizado. Previsto e realizado nunca são somados duas vezes. Recorrentes de **valor variável** (luz, água) usam a média dos últimos 3 meses como previsão e mostram "estimado".
- **RN-10.2 Recorrente no cartão:** quem paga é a fatura. O recorrente entra na fatura do ciclo da data de cobrança e não gera um compromisso separado (evita contar duas vezes).
- **RN-10.3 Ciclo da fatura:** uma compra feita **até o dia de fechamento** (inclusive) entra na fatura que vence no próximo vencimento. Compra feita **depois do fechamento** entra na fatura seguinte. A fatura pertence ao mês do seu **vencimento** (regime de caixa).
- **RN-10.4 Parcelamento:** valor da parcela = total ÷ N, com o resto dos centavos na 1ª parcela (RN-05.4). A parcela 1 segue a RN-10.3, e as seguintes caem uma por fatura. Juros informados pelo usuário entram no total (ex.: "10x de 330 com juros"). Para orçamento, limites e relatórios, cada parcela conta na categoria da compra **no mês da fatura**. Para o disponível, a compra inteira já comprometida aparece em "Comprometido nos próximos meses".
- **RN-10.4b Parcelamento fora do cartão** (boleto, carnê, Pix parcelado, financiamento): cada parcela vence no **dia de vencimento** informado (mesma regra de dia útil da RN-09.2), a partir do mês da 1ª parcela informada pelo usuário (padrão: mês seguinte à compra). Lembrete 1 dia antes (RN-10.9). No financiamento, o usuário informa o valor da parcela e quantas faltam, sem exigir o valor original.
- **RN-10.4c Dados do cartão:** a Arclou **nunca** pede nem armazena número completo, CVV, validade ou senha. O usuário pode informar só os 4 últimos dígitos, para diferenciar dois cartões do mesmo banco. A arte do cartão é ilustrativa.
- **RN-10.5 Quitação e cancelamento:** quitar antecipadamente remove as parcelas futuras e registra um lançamento único no valor informado. Cancelar (estorno) remove as parcelas futuras e lança um crédito na fatura.
- **RN-10.5b Ações de uma compra parcelada** (menu "⋯" no desktop; toque no item no mobile):
  - **Ver parcelas:** cronograma com nº/total, data (fatura ou vencimento), valor e status (próxima, prevista, paga).
  - **Editar:** descrição, categoria, valor total, nº de parcelas, data da compra e (fora do cartão) dia de vencimento. Só as parcelas **ainda não vencidas** são recalculadas. A forma de pagamento não pode ser trocada (cancelar e registrar de novo).
  - **Registrar pagamento** (só boleto, carnê, Pix parcelado e financiamento): marca a parcela como paga com valor e data. No cartão, o pagamento é a fatura.
  - **Quitar antecipadamente** e **Cancelar** seguem a RN-10.5 e mostram antes o impacto no comprometido do mês.
- **RN-10.6 Comprometido do mês M** = recorrentes previstos de M (fora do cartão) + total das faturas que vencem em M (parcelas + recorrentes no cartão + compras à vista no cartão). O indicador **% da renda comprometida** = comprometido ÷ receitas recorrentes previstas. Alertas:
  - **atenção** acima de 50%;
  - **crítico** acima de 70% (o usuário pode ajustar os percentuais).
- **RN-10.7 "Posso comprar?"** (RN-09.6) simula **todas as parcelas** nos meses em que caem, de acordo com o fechamento do cartão escolhido. Se em algum mês o comprometido passar do limite crítico, a resposta avisa qual mês fica apertado.
- **RN-10.8 Limite do cartão (opcional):** limite disponível = limite − (faturas em aberto + parcelas futuras). Avisa quando uma compra simulada ultrapassa o limite disponível.
- **RN-10.9 Lembretes:**
  - recorrente fora do cartão: 1 dia antes do vencimento;
  - fatura: 3 dias antes do vencimento, com o total;
  - os dois respeitam o opt-in e o horário de silêncio (RN-06.4) e consomem a quota de lembretes proativos (RN-03).

## RN-11 Finanças a dois (Casa)
- **RN-11.1 Estrutura:** uma Casa tem **no máximo 2 membros**, e cada pessoa participa de **no máximo 1 Casa**. Cada membro mantém conta, WhatsApp, cartões e dados próprios. Exige plano **Casal**, pago por um dos membros (o "titular").
- **RN-11.2 Convite:** o código ou link vale 7 dias e é de uso único. O convidado aceita depois de ler o resumo de privacidade (RN-11.4). Se o convidado tiver uma assinatura própria, ela é cancelada proporcionalmente (crédito) ao entrar no Casal.
  - **Canal do convite (política do WhatsApp Business):** a Arclou **nunca manda a primeira mensagem para o convidado**, porque ele ainda não deu opt-in. O convite sai do **WhatsApp do próprio titular** (link `wa.me/?text=` com o texto e o link `arclou.com.br/casa/CASA-XXXX` prontos) ou é copiado e compartilhado por ele. O convidado abre o link, aceita no site e confirma mandando `ENTRAR CASA-XXXX` para a Arclou, ou seja, **a conversa é iniciada por ele**, o que vale como opt-in e já vincula o número dele (dispensa o `VINCULAR-XXXX`).
  - O número informado pelo titular serve só para pré-preencher o compartilhamento e conferir que quem entrou é a pessoa certa. Se o número que mandar `ENTRAR` for diferente, a Arclou pede confirmação ao titular antes de liberar a Casa.
  - Enquanto o convite estiver pendente, o titular vê o status ("aguardando o João") e pode reenviar ou cancelar. O trial de 7 dias do Casal começa no pagamento, não no aceite.
- **RN-11.3 Visibilidade (decisão de 14/10/2026):** **todo lançamento nasce Pessoal.** Ele só vai para a Casa quando o autor marca "Da casa" ou "Dividido" (painel ou WhatsApp). A Arclou **pode perguntar** ("esse mercado foi da casa?"), mas **nunca move sozinha**. O parceiro **não vê nada** do que é pessoal: nem lançamentos, nem totais, nem renda, nem metas pessoais.
  - **Da casa:** os dois veem, e o valor entra na divisão pela regra da Casa.
  - **Dividido:** os dois veem, com a divisão definida naquele lançamento (sobrepõe a regra).
  - Só o **autor** pode mudar a visibilidade. Voltar para Pessoal remove o lançamento da Casa e recalcula o saldo.
- **RN-11.4 Privacidade da renda:** na regra "proporcional à renda", **cada um vê só a proporção** (ex.: 58% / 42%), nunca o valor da renda do outro. A proporção usa as receitas recorrentes previstas do mês. Se faltar a renda de alguém, a regra cai para 50/50 com aviso.
  - **Limite honesto da privacidade:** quem sabe a própria renda e a proporção consegue **estimar** a renda do outro (ex.: 4.300 ÷ 0,42 × 0,58 ≈ 5.938). Por isso a regra proporcional só é ativada quando **os dois aceitam** uma tela que diz isso com todas as letras, e a comunicação nunca promete "renda secreta": promete "ninguém vê o valor que o outro informou". Quem não quiser expor nem a proporção usa 50/50 ou personalizada.
  - A proporção é exibida em pontos percentuais inteiros e só é recalculada quando alguém altera a própria renda (não a cada receita lançada), para não revelar variações do mês.
- **RN-11.5 Divisão:** parte de cada um = valor × percentual da regra (ou do lançamento), arredondando os centavos a favor de quem pagou. Recorrentes e parcelamentos marcados como da casa dividem **cada parcela** no mês em que ela cai.
- **RN-11.6 Saldo "quem deve quem"** (por mês, acumulando o que ficou aberto) = Σ(pago por A nos itens da casa) − Σ(parte de A). Saldo positivo significa que o outro deve. Mostrar sempre **um único número** ("João te deve R$ 391,55"), nunca dívidas cruzadas.
- **RN-11.7 Acertar contas:** registra uma transferência entre membros (Pix, dinheiro ou "abater no próximo mês"). Ela **não** é gasto nem receita no pessoal de ninguém. Pode ser parcial. Os dois recebem a confirmação.
- **RN-11.8 Orçamento, limites e metas da Casa:** são separados dos pessoais. O aporte sugerido numa meta conjunta segue a regra de divisão. Os aportes saem do disponível pessoal de cada um.
- **RN-11.9 Disponível pessoal com Casa:** disponível = (fórmula da RN-09.1) considerando **só a sua parte** dos itens da casa e o saldo a pagar ou receber, se o usuário quiser incluir (padrão: não incluir).
- **RN-11.10 Avisos ao parceiro:** são opt-in **por pessoa** e consomem a quota de proativos de quem recebe. Nunca contêm item pessoal.
- **RN-11.11 Saída e separação:** qualquer membro pode sair a qualquer momento.
  - O saldo pendente é mostrado e pode ser acertado ou registrado como pendência.
  - O histórico compartilhado fica **somente leitura** para os dois por 90 dias, e cada um pode exportar.
  - Cada membro leva os próprios aportes das metas conjuntas.
  - O plano do titular vira Pro; o outro volta para trial ou Essencial, conforme escolher.
  - **Conta conjunta:** o registro (saldo e lançamentos) fica somente leitura com o histórico. A Arclou **não divide o dinheiro** da conta: mostra o último saldo registrado e permite anotar como os dois combinaram dividir ("Marina fica com R$ 4.600, João com R$ 4.591,30"). Essa anotação vira uma entrada na conta pessoal de cada um, se a pessoa quiser.
  - Quem sai recebe a confirmação na hora, e o outro é avisado pelo WhatsApp (o aviso não informa o motivo e não oferece "desfazer").
  - A saída é confirmada digitando **SAIR** (ação irreversível, RN-04.2). Há 24 horas para cancelar a saída antes de o histórico congelar.
- **RN-11.13 Modo de dinheiro da Casa (decisão de 14/10/2026):** ao criar a Casa, o casal escolhe **como organiza o dinheiro**. O modo muda o padrão dos lançamentos e o que a tela principal mostra. Os dois precisam confirmar a escolha e qualquer troca.

  | Modo | Para quem | Padrão de um lançamento novo | O que a Casa mostra | "Quem deve quem" |
  |---|---|---|---|---|
  | **Dinheiro junto** | Salários vão para uma conta conjunta e tudo sai dela | **Da casa, pago pela conta conjunta** | Saldo da conta conjunta, entradas, saídas, previsão do mês | **Não existe** |
  | **Separado** (dividindo as contas) | Cada um tem o seu dinheiro e divide as despesas da casa | **Pessoal** (RN-11.3) | Gastos da casa, divisão e saldo entre os dois | Entre as pessoas (RN-11.6) |
  | **Misto** | Cada um tem o seu dinheiro e os dois abastecem uma conta conjunta para a casa | **Pessoal**. Se for marcado como da casa, o pagamento sugerido é a conta conjunta | Saldo da conta conjunta, aportes de cada um, gastos da casa | Só **reembolsos**: quando alguém paga do próprio bolso algo da casa, a conjunta deve a ele (RN-11.16) |

  - Em **Dinheiro junto**, o padrão "Da casa" é uma exceção consciente à RN-11.3. Ela vale só depois que **os dois** confirmam, numa tela que explica que o parceiro passará a ver os lançamentos novos. Cada um ainda pode registrar algo como **Pessoal** ou **Privado** (RN-11.15).
  - Trocar de modo não altera lançamentos antigos, só o padrão dos novos.
- **RN-11.14 Conta conjunta:** a Casa pode ter **1 conta conjunta** (nos modos Dinheiro junto e Misto). Ela é um objeto da Casa, não de uma pessoa.
  - A conta tem um nome, uma cor do modelo de cartão Arclou (cor-padrão do banco, editável, sem logo, RN de `09-cartoes-visual.md`), um **saldo inicial** e a data desse saldo.
  - Os cartões da conta conjunta (débito ou crédito) são da Casa: os dois veem as compras e a fatura. Nunca coletamos número completo, CVV, validade ou senha (RN-10.4c).
  - Todo lançamento da casa tem uma **origem do pagamento**: `conta conjunta`, `Marina` ou `João`. Pelo WhatsApp, a Arclou usa o padrão do modo ("gastei 412 no mercado" no modo Dinheiro junto → conta conjunta) e aceita correção ("foi no meu cartão").
  - **Entradas:** salário ou outra receita pode cair na conjunta. Nesse caso, quem registrou aceita que o parceiro veja o valor (a receita deixa de ser privada). No modo Misto, a entrada típica é o **aporte** ("coloquei 2.900 na conjunta"), que não é receita nem gasto de ninguém.
  - **Saldo da conta conjunta** = saldo inicial + entradas + aportes − saídas pagas por ela − transferências para metas. A Arclou não acessa o banco: o saldo é o que foi registrado. Por isso existe **"Conferir saldo"**: a pessoa informa o saldo real do app do banco, e a diferença vira um lançamento de **ajuste** visível para os dois (ou uma lista dos lançamentos que provavelmente faltam).
  - **Previsão do mês** = saldo hoje − contas recorrentes da casa a vencer até o fim do mês + receitas previstas.
- **RN-11.15 Privado na conta conjunta:** um gasto pago pela conjunta que a pessoa não quer detalhar (ex.: presente surpresa) é registrado como **Privado**. O parceiro vê **"Privado · João · R$ 180,00"**, sem descrição nem categoria. O valor precisa aparecer porque o dinheiro saiu de uma conta dos dois e, sem ele, o saldo não fecha. Gastos pagos com dinheiro **próprio** e marcados como Pessoal continuam invisíveis. Um item Privado pode ser revelado depois pelo autor ("pode mostrar o presente").
- **RN-11.16 Reembolso (modo Misto):** se alguém paga **do próprio bolso** um lançamento da casa, a conta conjunta passa a dever esse valor a ele. A tela mostra **"Reembolsar a Marina: R$ 412,30"**, e o reembolso é registrado como transferência da conjunta para a pessoa (não é gasto). No modo Dinheiro junto, pagar do próprio bolso algo da casa só mostra a pergunta "reembolsar pela conjunta?". Se ninguém responder, nada é cobrado.
- **RN-11.17 Aportes sugeridos (modo Misto):** a regra de divisão (RN-11.4 e RN-11.5) passa a valer para **quanto cada um coloca na conjunta**, não para cada gasto. Exemplo: para R$ 5.000 no mês com a regra 58/42, a sugestão é Marina R$ 2.900 e João R$ 2.100. A Arclou mostra quanto cada um já aportou no mês e quanto falta.
- **RN-11.12 LGPD:** consentimento explícito de cada membro ao entrar. A exclusão de conta de um membro remove os dados pessoais dele e **anonimiza** a autoria dele no histórico compartilhado do outro ("Ex-membro").
