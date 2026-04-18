# Contributing to Penta Historia

## Workflow

We work through **pull requests**.

- No direct feature work should be merged straight into `main`.
- Create a branch for each change.
- Open a PR for review and discussion.
- Code reviews and PR validation must be performed by **Main**.
- Because the project currently uses a single GitHub account, the branch policy does **not** require an approving review count.
- Main still performs the review, but merge readiness is based on the review itself plus green required checks.
- Merge only when required checks are green.

## Required checks before merge

Before a PR can be merged, the following must be green:

- GitHub Actions CI
- Sonar checks / quality gate

If Sonar is red, the PR is **not** ready to merge.

## Expected quality bar

- Keep changes focused and small when possible.
- Update tests when behavior changes.
- Keep the project runnable.
- Document important gameplay or architecture decisions in the repo.
- Move the codebase toward a **hexagonal architecture** with clear **ports and adapters**.
- Avoid coupling core game rules directly to Pygame or other external tools.

## Local checks

```bash
python -m compileall src
PYTHONPATH=. python -m unittest discover -s tests -p 'test_*.py' -v
```

## Game collaboration model

- **Alpha**: war, map, fronts, territorial expansion
- **Beta**: cities, economy, logistics
- **Gamma**: culture, research, alternate history
- **Delta**: intrigue, sabotage, espionage
- **Epsilon**: climate, catastrophes, myths
- **Main**: integration, UI, overall game loop
