# backend/

API (FastAPI) e worker (arq) em Python 3.12, com arquitetura hexagonal (doc 04 §6).

- `src/assistant/domain/`: regras de negócio puras, sem dependências externas
- `src/assistant/application/`: casos de uso
- `src/assistant/adapters/`: Postgres, Firestore, Vertex, Meta, Google, gateway
- `src/assistant/api/`: rotas que implementam o contrato `api/openapi.yaml`
- `tests/`: unit, integration, e2e e evals

O código entra a partir do S0-10 (hello world) e do S1-01 (esqueleto).
