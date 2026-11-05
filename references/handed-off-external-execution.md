## Handed-off External Execution

Consume the router-owned schema-version-6 contract from
`docs/agent-collab/<change-id>/status.md`. Do not re-decide mode, approval,
risk, planned batches, profiles, authorization, or final verification commands.
Missing, stale, duplicated, contradictory, or unparsable canonical state is
`BLOCKED`. Active schema-4/schema-5 contracts drain under their old runtime
before cutover and are never silently migrated or treated as current authority.

The contract binds immutable control-plane, executor, and reviewer assignments,
including Review purpose, reviewer product, reviewer role, capability,
independence, authority, contract-local instance, decision provenance, and a
Confirmation Lease. `codex`, `pi`, `antigravity-cli`, and `grok-cli` are
equally eligible for assigned executor or independent-reviewer roles. Their
results remain governed evidence. Only the bound Codex product plus
`control-plane` role, `control-plane-high` profile, matching instance, and
canonical contract owns decisions. Standard/strict executor and reviewer
instance IDs differ even when products match.

### Artifact Paths

| Artifact | Path |
|---|---|
| Canonical status | `docs/agent-collab/<change-id>/status.md` |
| Brief | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-brief.md` |
| Report | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report.md` |
| Abort Report | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report-abort.md` |
| Review | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-attempt-<AA>-review.md` |
| Timeout Audit | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-attempt-<AA>-timeout-audit.md` |

Attempt-specific paths preserve history. Never overwrite evidence from an
earlier `FAIL`, `BLOCKED`, or timeout attempt.

### State Machine

1. Validate canonical revision, lifecycle, batch, attempt, product/instance/
   role/profile assignments, decision provenance, Confirmation Lease, partial
   state, and owner. Audit existing dirty/partial work before dispatch and list
   what must not be repeated.
2. Transition canonical status to `ready-for-execution`, increment its revision,
   hash the canonical status file, and write the current attempt Brief with that
   execution revision and canonical SHA-256.
3. Run a current-revision **Preflight Review** before dispatch for scope,
   acceptance, exact commands, rollback/stop conditions, Git authority, and
   placeholders. Preflight uses only `PASS`/`BLOCKED`; any finding moves to
   `blocked`, revises the Brief in a new attempt, and must be reviewed again.
   Unchanged revisions do not repeat ceremony. Dispatch only after Preflight
   PASS.
4. Require the attempt Report or Abort Report using the execution revision and
   matching SHA-256;
   then transition status to `ready-for-review` with a new review revision.
5. Audit actual files and the complete diff, scope, evidence, critical commands,
   copy/transform/production wiring, claim-to-mechanism support, and required
   acceptance layers. Consume an assigned independent Review only when its
   product/instance/role/profile match and its instance differs from the executor.
   Rerun critical commands and add at least one independent adversarial or real
   business-chain probe.
6. Write a Review whose first line is exactly `# Review Result: PASS`,
   `# Review Result: FAIL`, or `# Review Result: BLOCKED`.
7. Apply the transition:
   - `FAIL` -> same batch `needs-fix`, increment attempt, create a correction
     Brief, verify, and Review again;
   - `BLOCKED` -> same batch `blocked`, record owner/reason/resume condition,
     then use a fresh attempt and Review after recovery;
   - non-final `PASS` -> increment one batch, reset attempt, next Brief;
   - final `PASS` -> `awaiting-final-verification`, return to
     `openspec-superpower-change` without claiming task completion.

Before applying any transition that introduces an artifact, write the proposed
status outside the project, run the project validator with current canonical
status as `--previous-status`, preserve the PASS output, then atomically replace
the one canonical block. Never persist the proposed/previous snapshot in the
project.

Only Review `PASS` may promote a batch. `FAIL` and `BLOCKED` must be reviewed
again after correction or recovery; a chat acknowledgment is not closure.

## Evidence Profiles

- `compact`: concise Brief/Report/Review and focused commands; omit heavy tables
  unless the contract needs them.
- `standard`: function map, data contract, invariants, error matrix, RED/GREEN,
  production wiring, `step_critical`, and an independent behavior check.
- `strict`: required real security/API/schema/migration/rollback/business-chain
  evidence; mocks and unit tests cannot substitute for required real layers.

The governor runs `step_critical` for each attempt. The router runs
`final_critical` after final batch Review PASS; later implementation changes
invalidate that final evidence.

Every external profile has at least one non-blank `step_critical` and
`final_critical`. Status references the attempt Report and Review by safe
project-relative path plus SHA-256. New artifacts embed a schema-2 manifest
whose `agent_product`, `agent_instance_id`, `agent_role`, and
`capability_profile` match the parent schema-6 assignment and which also binds
result, change, batch, attempt, and source canonical revision/SHA-256.
Historical schema-4/schema-5 contracts and their evidence remain immutable.
Review records
from/to revision and canonical SHA-256 transition evidence; `complete` runtime
validation requires the actual previous status.

## Role-first Review assignment

For schema 6, `codex`, `pi`, `antigravity-cli`, and `grok-cli` are equally
eligible for assigned executor or independent-reviewer roles. Only a bound
`codex` product with role `control-plane`, profile `control-plane-high`, the
matching instance, and canonical contract owns routing, evidence acceptance,
canonical state, archive, or completion. Product names alone grant no authority.

Every Review request states Review purpose, reviewer product, role, capability,
independence, and authority. Apply an existing canonical assignment first;
otherwise preserve a product explicitly selected by the user; otherwise name
one concrete eligible product. If no eligible independent instance is
available, return `BLOCKED`. “another agent”, “independent agent”, and “another
model” are invalid when they are the only destination.

<!-- ROLE_FIRST_REVIEW_CLASSIFICATION_START -->
Use this exact classification before selecting a product:

- A Review that decides whether implementation, execution, runtime planning,
  promotion, archive, or completion may proceed is gate-bearing: use role
  `independent-reviewer`, profile `control-plane-high`, distinct-instance
  independence, and authority `governed-review-evidence`.
- A standalone Review that explicitly does not decide a gate is advisory:
  preserve any eligible user-selected product, use role `advisory-reviewer`,
  profile `control-plane-high`, advisory-not-gate-bearing independence, and
  authority `advisory-input`.
- `cohesive-medium` and `mechanical-low` are executor/evidence-collection
  profiles, not Review profiles.
- For standalone prompt or recommendation wording, a request to open or name a
  new distinct reviewer instance remains actionable after all six assignment
  concepts are resolved; do not infer unavailability merely because a concrete
  instance ID or open window is not yet supplied.
- Return `BLOCKED` only when the request explicitly says no eligible distinct
  instance exists or insists on reusing an implementation instance.
- When a required distinct reviewer instance is unavailable because the user
  must open or provide one, return `BLOCKED` with `blocker_owner: user` and a
  non-blank resume condition.
<!-- ROLE_FIRST_REVIEW_CLASSIFICATION_END -->

Review purpose: inspect the current implementation plan and decide PASS or BLOCKED; reviewer product: codex; role: independent-reviewer; capability: control-plane-high; independence: a user-opened new-window instance distinct from the plan author and executor; authority: governed Review evidence only.
