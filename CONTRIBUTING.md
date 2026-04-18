# Contributing to Penta Historia

## Workflow

We work through **pull requests**.

- No direct feature work should be merged straight into `main`.
- Create a branch for each change.
- Open a PR for review and discussion.
- Each agent should develop its own part of the game in its own branch or PR when practical.
- On GitHub, every agent-written message must start with the agent name followed by a colon, for example `Alpha:` or `Zeta:`.
- Code reviews and PR validation must be performed by **Zeta**.
- When an agent has a PR ready, that agent must ask **Zeta** for validation.
- Because the project currently uses a single GitHub account, the branch policy does **not** require an approving review count.
- Zeta performs the review, and merge readiness is based on that review plus green required checks.
- If Zeta does not validate a PR, Zeta must leave a comment on the PR and tell the agent to rework the code.
- Merge only when required checks are green.

## Required checks before merge

Before a PR can be merged, the following must be green:

- GitHub Actions CI

Sonar is planned, but it is **not blocking for merge right now** while the integration is being set up.

Once Sonar is reliably connected to pull requests, the quality gate can be made mandatory again.

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
- **Main**: development coordination, integration, UI, overall game loop
- **Zeta**: PR review, validation, and cross-cutting quality control
