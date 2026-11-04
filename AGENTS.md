# AGENTS.md

## Project positioning

`codex-brief-antigravity-review` is an open-source, reusable Codex skill designed to govern the collaboration between planning-focused orchestrators (like Codex) and execution-focused command-line agents (like Antigravity CLI).

## Required behavior for agents

- Read `SKILL.md` before changing this project.
- Do not modify files in `references/` or `agents/` without updating `SKILL.md` or explaining the changes.
- Test the templates for formatting consistency before completing changes.
- Default tests must run from a standalone checkout without requiring a sibling Router repository. Router-owned rules stay in Router tests; optional cross-repository integration must use an explicit source path and a separate integration command.
- This repository (`/Users/elvis/file/develop/opensource/codex-brief-antigravity-review`) is the canonical Git source of truth for `codex-brief-antigravity-review` (`origin/main`: `https://github.com/codebyelvis/codex-brief-antigravity-review`). Never edit only installed runtime copies (`~/.codex/skills/codex-brief-antigravity-review`, `~/.pi/agent/skills/codex-brief-antigravity-review`, `~/.gemini/antigravity-cli/skills/codex-brief-antigravity-review`, `~/.grok/skills/codex-brief-antigravity-review`) without updating this repository first.
- When user push authorization or a companion sync-push closure applies, commit and `git push origin main` in this repository after validation and four-target runtime sync so GitHub never lags behind local runtime changes.
- Do not execute `git add`, `git commit`, or `git push` unless the user explicitly requests it in the current task or authorizes companion sync-push closure.
- Ensure any self-evolution changes to this skill do not bypass or weaken the quality control loop (Brief -> Dispatch -> Report -> Review).
- Route trigger, lifecycle, required artifact, evidence, or completion-rule changes through `openspec-superpower-change` as Major Self-Evolution before implementation.

## Validation

Run before completion with a Python interpreter that provides PyYAML for `quick_validate.py`:

```bash
"${PYTHON_BIN:-python3}" "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" .
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_templates.py .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Also confirm `agents/openai.yaml` matches the standalone/handed-off routes in `SKILL.md`.
