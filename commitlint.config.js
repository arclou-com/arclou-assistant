// Conventional Commits: <tipo>(<escopo>): <descrição>  — ver CONTRIBUTING.md
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', ['feat', 'fix', 'chore', 'docs', 'refactor', 'test', 'ci', 'build', 'perf', 'revert']],
    'scope-enum': [2, 'always', ['api', 'web', 'agent', 'infra', 'ci', 'docs', 'scripts', 'deps']],
    'subject-case': [0],
    'header-max-length': [2, 'always', 100],
    'body-max-line-length': [0],
  },
};
