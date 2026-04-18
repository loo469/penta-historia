# Contributing to Penta Historia

## Workflow

We work through **pull requests**.

- No direct feature work should be merged straight into `main`.
- Create a branch for each change.
- Open a PR for review and discussion.
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
