# web/

Next.js (App Router, TypeScript): página de vendas, checkout, painel e Central de Ajuda.

- As telas são **pixel perfect** com o Figma (biblioteca de componentes no node `53:2` do arquivo `PJ7SvIZo5iVL4GqUoT0xAi`).
- A API é consumida só pelo cliente gerado do contrato `api/openapi.yaml` (doc 13). Em dev, o front aponta para o mock (Prism).
- O front nunca calcula dinheiro: totais, divisões e simulações vêm da API.

O código entra a partir do S0-10 (hello world) e do S1-F01 (base do front).
