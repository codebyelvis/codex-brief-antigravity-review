# CHANGELOG

All notable changes to this project will be documented in this file.

## Unreleased

### Changed
- Adopt current schema-6 immutable Reviewer Assignments, concrete role-first
  standalone Review wording, four-product executor/reviewer eligibility, and
  bound-Codex control-plane authority while keeping schema 4/5 audit-only.
- Add Pi to the required portable runtime closure and document its Skill and
  managed global-rule roots; all four targets must pass before completion.
- Keep route selection, standalone behavior, and shared authority/Git boundaries
  in `SKILL.md`, while loading the complete external-batch governor on demand
  from `references/handed-off-external-execution.md` only for valid Handoffs.
- Preserve the migrated governor contract with a normalized content hash and
  structural validation; no token reduction is claimed because Antigravity
  reference-loading remains `UNKNOWN`.

## [1.4.0] - 2026-07-15

### Changed
- Make Standalone Lightweight Review explicit and request-scoped, with concise
  findings-first checks for OpenSpec scope, scenarios, design risks, task
  traceability, and cross-artifact consistency.
- Do not auto-chain this skill after another workflow produces OpenSpec
  artifacts; preserve the complete valid-Handoff lifecycle when it applies.
- Detail both legal README routes: request-scoped non-state-changing Standalone
  work and the complete canonical Handoff lifecycle, including final handback.
- Participate in phase-aware cross-CLI routing through managed invariant
  `CCG-014` and manifest version 3 without weakening any HARD-GATE, evidence,
  Review, verification, or completion boundary.
- Verify 72 companion tests alongside the router's 117-test source suite,
  durable 5/5/25 forward evidence, and three-target runtime parity/discovery.
- Treat the first shared-workspace S2 result as invalid harness contamination,
  not a product bug. After reset, fix the real delegated authentication/
  compatibility brainstorming bypass, add regression coverage, then pass Review.
- Replace the earlier non-durable five-scenario behavior summaries with fresh
  per-scenario resets and 25 persisted evidence files.
- Record completed OpenSpec archival, post-archive strict validation, final High
  Review, and verified temporary-resource cleanup; keep Git commit/push pending.

## [1.3.0] - 2026-07-11

### Changed
- Upgrade new Handoffs and templates to schema 5/schema-2 evidence with bound
  product, instance, role, capability profile, provenance, and Lease references.
- Govern manually copied state-changing Briefs through the same canonical route.
- Require High Review of actual diffs, copy/transform/production wiring,
  claim-to-mechanism support, critical reruns, and an independent probe.
- Keep executor PASS advisory and reject same-instance self-review even when the
  executor and reviewer use the same product.

## [1.2.0] - 2026-07-11

### Changed
- Upgrade Handoff collaboration to schema 4 with bound executor, independent
  reviewer, and Codex decision-owner identities.
- Bind Report, Review, timeout, and dispatch evidence to the producing agent
  identity/role and reject same-agent independent self-review.
- Participate in the allowlisted Codex, Antigravity CLI, and Grok CLI runtime
  synchronization and managed-governance completion gate.

## [1.1.0] - 2026-07-10

### Changed
- Narrow implicit routing to non-state-changing review or an existing valid Handoff.
- Add Brief Preflight Review and canonical execution SHA-256 consensus.
- Upgrade Handoff governance to schema 3 with hashed Report/Review evidence.
- Reject empty critical checks, blank blockers, unsafe evidence paths, and atomic final completion.
- Expand adversarial lifecycle tests and bind runtime evidence to
  role/result/batch/attempt/source fingerprints plus previous-status transitions.
- Add caveman as a presentation-compression mode and explicitly exclude
  governance routing and evidence artifacts from compression.

## [1.0.0] - 2026-06-23

### Added
- Initial release of `codex-brief-antigravity-review` skill.
- Core `SKILL.md` orchestrating the "Brief -> Dispatch -> Report -> Review" flow.
- Configured metadata in `agents/openai.yaml`.
- Reusable templates in `references/`:
  - `brief-template.md` (Step Brief specification)
  - `report-template.md` (Step Report feedback)
  - `review-template.md` (Step Review gatekeep)
  - `agy-dispatch-template.md` (External agent dispatch command syntax)
- Added default `AGENTS.md`, `.gitignore`, `CONTRIBUTING.md`, and `LICENSE`.
