# Contributing to ApeSwarm

Thanks for helping make ApeSwarm more savage and more useful.

## Workflow
- Create a feature branch from `main`.
- Keep changes focused and atomic.
- Open a PR with a clear summary and validation steps.
- Prefer squash merge into `main`.

## Branch and Commit Style
- Branch examples:
  - `feat/truth-ape-search`
  - `fix/git-ape-parse`
  - `docs/readme-troubleshooting`
- Commit message examples:
  - `feat: add TruthApe verification pass`
  - `fix: harden GitApe dry-run logic`
  - `docs: add local ollama setup notes`

## Development
- Python: `>=3.11`
- Install:
  - `python3 -m pip install -e .`
- Run:
  - `apeswarm "your goal"`

## Safety Rules
- Git writes are opt-in.
- Default mode is dry-run for GitApe execution.
- Never commit secrets or API keys.

## PR Checklist
- [ ] Code compiles (`python -m compileall src`)
- [ ] Basic CLI smoke test completed
- [ ] Docs updated for behavior changes
- [ ] No secrets in commits
