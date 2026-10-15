# Como contribuir

O fluxo completo está no [doc 12](docs/12-ambientes-e-workflow.md#4-git-prs-e-github-project). Este guia é o resumo do dia a dia.

## 1. Preparar a máquina
Requisitos: Git, [uv](https://docs.astral.sh/uv/), Node 22, Docker e Terraform ≥ 1.9.

```bash
make setup   # instala o pre-commit e os hooks de pre-commit e commit-msg
make lint    # roda tudo em todos os arquivos
```

## 2. Pegar uma task
1. No [Project](https://github.com/orgs/arclou-com/projects/3), escolha uma issue da sprint atual em **Todo** e mova para **In Progress**.
2. Leia a especificação em `docs/sprints/sprint-NN.md` (contexto, escopo, critérios de aceite e testes).

## 3. Branch
Sempre a partir da `develop` atualizada:

```bash
git switch develop && git pull
git switch -c feature/S0-01-monorepo    # feature/ · fix/ · chore/ · docs/  +  ID da task + resumo
```

`main` e `develop` são protegidas: **ninguém faz push direto**. Tudo entra por PR.

## 4. Commits (Conventional Commits)
```
<tipo>(<escopo>): <descrição curta no imperativo>
```
- **Tipos:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `build`, `perf`, `revert`
- **Escopos:** `api`, `web`, `agent`, `infra`, `ci`, `docs`, `scripts`, `deps`
- Exemplos: `feat(api): rota de vínculo do WhatsApp` · `chore(infra): bucket de state` · `fix(web): saldo da Casa no mobile`

O hook `commit-msg` rejeita mensagens fora do padrão (ex.: `ajustes`).

## 5. Pull request
- Base: `develop`. Título: `S0-01 feat: monorepo e pre-commit` (ID da task + tipo + resumo).
- Corpo: `Closes #N`, o que mudou, como testar e o checklist da Definition of Done (o template preenche).
- Front: print lado a lado com o Figma (**pixel perfect**).
- O merge na `develop` é **squash** e dispara o deploy em staging. A issue fecha sozinha e vai para Done.

## 6. Release
PR `develop → main` (merge commit) com as notas da versão. O deploy em production espera a aprovação do owner.

## 7. Segredos
O repositório é **público**. Nenhum segredo entra no código: eles ficam no Secret Manager (`infra/scripts/set-secret.sh`). O gitleaks bloqueia o commit se encontrar algo parecido com uma chave.

## 8. Revisão
Enquanto o time tiver uma pessoa, o PR não exige aprovação, mas exige o CI verde. A partir da segunda pessoa, passa a exigir 1 aprovação.
