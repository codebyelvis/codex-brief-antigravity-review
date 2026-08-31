# Handoff Contract

The Handoff Contract is the single machine-readable state shared by
`openspec-superpower-change` and `codex-brief-antigravity-review`. Schema version
6 is the only current Handoff API for newly created external execution;
standalone and inline work do not create this contract. Completed schema-4/5
contracts remain immutable history and are available only to the read-only
legacy audit path.

## Canonical Location

Keep exactly one mutable marker block in
`docs/agent-collab/<change-id>/status.md`. Brief, Report, Review, Gate, and chat
output must not embed another mutable block; they reference the canonical path,
revision, batch, attempt, and SHA-256 fingerprint.

## Marker Block

````markdown
<!-- COOP_HANDOFF_CONTRACT_START -->
```yaml
schema_version: 6
change_id: add-example-change
mode: approved-implementation
approval_status: approved
risk_profile: standard
batch_profile: cohesive
current_batch: 1
planned_batches: 2
attempt: 1
contract_revision: 1
lifecycle_state: ready-for-brief
attempt_report_artifact: null
last_review_result: not-run
last_review_artifact: null
blocked_reason: null
blocker_owner: none
resume_condition: null
final_verification: pending
final_verification_artifact: null
final_review_result: pending
final_review_artifact: null
executor: external-agent
governor: codex-brief-antigravity-review
control_plane_owner:
  agent_product: codex
  agent_instance_id: codex-control-01
  agent_role: control-plane
  capability_profile: control-plane-high
executor_assignment:
  agent_product: antigravity-cli
  agent_instance_id: antigravity-executor-01
  agent_role: executor
  capability_profile: cohesive-medium
reviewer_assignment:
  review_purpose:
    object: current batch implementation, Report, contract, and evidence
    decision: decide pass, fail, or blocked for this governed Review gate
  agent_product: grok-cli
  agent_instance_id: grok-reviewer-01
  agent_role: independent-reviewer
  capability_profile: control-plane-high
  independence_requirement:
    kind: distinct-contract-instance
    distinct_from:
      - control_plane_owner
      - executor_assignment
  result_authority: governed-review-evidence
independent_review_not_applicable_reason: null
decision_source: ai-proposed/user-approved
confirmation_lease:
  decision_id: decision-001
  path: docs/agent-collab/add-example-change/confirmation-lease.md
  sha256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
confirmation_lease_status: valid
next_owner: codex-brief-antigravity-review
step_critical:
  - focused test command
final_critical:
  - full test matrix
business_acceptance:
  unit: required
  pipeline: optional
  api: required
  real_business: required
stop_conditions:
  - scope expansion
  - contract ambiguity
verification_strategy:
  step: run step_critical per attempt; Review reruns critical plus an independent check
  final: persist final_critical evidence before final Review
readonly_fields:
  - schema_version
  - change_id
  - mode
  - approval_status
  - risk_profile
  - batch_profile
  - planned_batches
  - executor
  - governor
  - control_plane_owner
  - executor_assignment
  - reviewer_assignment
  - independent_review_not_applicable_reason
  - decision_source
  - confirmation_lease
  - final_critical
  - step_critical
  - business_acceptance
  - stop_conditions
  - verification_strategy
  - readonly_fields
```
<!-- COOP_HANDOFF_CONTRACT_END -->
````

## Optional Runtime Environment Advice

An actual approved model or reasoning switch may carry the following optional,
human-readable block in this reference guidance or in a Brief/dispatch surface.
Omit the entire block when the current runtime is sufficient. If an upstream
control-plane response already contains it, downstream surfaces copy it
verbatim and do not regenerate it or ask for a second notice.

```text
运行环境建议：
- 目标 Session：
- 推荐模型：
- 推理强度：
- 切换原因：
- 可复制任务提示词：
- 完成后切回：
```

The block is outside the machine-readable marker above and is never written to
canonical `docs/agent-collab/<change-id>/status.md`. It does not participate in
schema parsing, canonical status SHA-256, immutable assignment, evidence
identity, lifecycle validation, permission checks, or PASS/FAIL/BLOCKED
decisions. An old schema-6 Handoff without this optional block remains valid.

## Required Fields And Values

Required fields include every field in the example.

- `lifecycle_state`: `ready-for-brief`, `ready-for-execution`,
  `ready-for-review`, `needs-fix`, `blocked`,
  `awaiting-final-verification`, or `complete`.
- `last_review_result`: `not-run`, `pass`, `fail`, or `blocked`.
- `final_verification` and `final_review_result`: `pending`, `pass`, `fail`,
  or `blocked`.
- `attempt` and `contract_revision`: positive integers; booleans are invalid.
- `next_owner`: `openspec-superpower-change`,
  `codex-brief-antigravity-review`, `external-agent`, or `user`.
- `step_critical`, `final_critical`, and `stop_conditions`: non-empty lists of
  non-blank strings for every evidence profile.
- `readonly_fields`: exactly the immutable field set shown above, without
  duplicates or additional mutable fields.
- `control_plane_owner` and `executor_assignment` contain exactly
  `agent_product`, `agent_instance_id`, `agent_role`, and
  `capability_profile`.
- `reviewer_assignment` is always present and contains exactly
  `review_purpose`, `agent_product`, `agent_instance_id`, `agent_role`,
  `capability_profile`, `independence_requirement`, and `result_authority`.
  Purpose contains exactly non-blank `object` and `decision`; independence
  uses `distinct-contract-instance`; result authority is exactly
  `governed-review-evidence` and never grants canonical decision authority.
- The control plane is product `codex`, role `control-plane`, profile
  `control-plane-high`. It alone records authoritative transitions and final
  completion.
- The executor role is `executor`; its profile is bounded by the assigned
  capability ceiling. A standard or strict reviewer uses role
  `independent-reviewer` and profile `control-plane-high`.
- Every assigned `agent_instance_id` is a non-sensitive contract-local ID and
  differs from every other assigned instance. Product equality never permits
  self-review.
- For standard/strict work, reviewer role is `independent-reviewer`, profile is
  `control-plane-high`, independence names both owner and executor, all three
  instance IDs differ, and `independent_review_not_applicable_reason` is null.
  For compact work, reviewer product/instance/role/profile equal the control
  plane, independence names only the executor, and the top-level reason is
  non-blank.
- `decision_source` is one of `ai-proposed/user-approved`, `user-originated`,
  `user-corrected`, `evidence-discovered`, `deferred`, or `revoked`.
- `confirmation_lease` is an immutable decision-ID/path/SHA-256 reference to a
  typed lease artifact. Mutable `confirmation_lease_status` starts `valid` and
  may only move to `deferred` or `revoked`, which forces `blocked`; an old Lease
  cannot be reactivated. A platform permission cannot satisfy a workflow or
  business/production gate.

An artifact reference is either `null` or this mapping:

```yaml
path: docs/project-relative/evidence.md
sha256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

Artifact paths must be project-relative, may not contain `..`, and must remain
inside the declared artifact root after symlink resolution. A non-pending result
requires a matching artifact reference; a pending/not-run result requires
`null`. Artifact paths are distinct by evidence role. The only allowed reuse is
one identical `timeout-audit` artifact serving as both the attempt Report and
the blocking Review.

Every referenced file contains exactly one immutable evidence manifest:

````markdown
<!-- COOP_EVIDENCE_MANIFEST_START -->
```yaml
evidence_schema_version: 2
evidence_role: batch-review
evidence_result: pass
change_id: add-example-change
current_batch: 1
attempt: 1
contract_revision: 3
canonical_sha256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
agent_product: grok-cli
agent_instance_id: grok-reviewer-01
agent_role: independent-reviewer
capability_profile: control-plane-high
```
<!-- COOP_EVIDENCE_MANIFEST_END -->
````

Valid roles are `attempt-report`, `batch-review`, `preflight-review`,
`timeout-audit`, `final-verification`, and `final-review`. Results are `pass`,
`fail`, or `blocked`. `current_batch` and `attempt` identify the work evidenced.
`contract_revision` and `canonical_sha256` identify the earlier canonical status
revision that the artifact reports on, reviews, or verifies; this source
fingerprint avoids a hash cycle with the new artifact reference.

For schema-6 evidence, `agent_product`, `agent_instance_id`, `agent_role`, and
`capability_profile` exactly match the canonical assignment. Attempt Reports
bind the executor assignment. Batch Reviews bind `reviewer_assignment`.
Preflight Review,
timeout audit, final verification, and final Review bind the control plane. The
timeout-audit shared-artifact exception keeps that control-plane identity even
when it occupies the Report field. Historical schema-4 contracts retain their
existing schema-1 `agent_identity` evidence and are never rewritten as schema 6.

Runtime status validation checks file existence, non-empty content, SHA-256,
role-to-state binding, result-to-status binding, batch/attempt freshness, source
revision ordering, canonical fingerprint format, and matching `change_id`; a
heading or filename alone is not evidence identity. `preflight-review` and
`timeout-audit` are BLOCKED-only batch evidence and never satisfy batch PASS.
Final completion validation additionally requires `--previous-status` so the
final Review manifest can be checked against the actual prior revision and its
SHA-256.

This is an external execution contract: `executor` is `external-agent`,
`governor` is `codex-brief-antigravity-review`, and mode is
`approved-implementation`, approved `self-evolution`, or `direct-change`.
The immutable product/instance/role/profile assignments determine who executes
and independently Reviews; only the bound Codex `control_plane_owner` records
the authoritative decision.

## Lifecycle And Review Loop

```text
ready-for-brief -> ready-for-execution -> ready-for-review
batch FAIL -> needs-fix -> new attempt on the same batch
batch BLOCKED -> blocked -> new attempt on the same batch
PASS non-final -> next batch ready-for-brief
PASS final -> awaiting-final-verification (pending/pending)
final verification PASS -> awaiting-final-verification (pass/pending)
final Review PASS -> complete
final FAIL -> needs-fix; final BLOCKED -> blocked
```

Valid result tuples by state:

| State | `last_review_result` | `final_verification` | `final_review_result` |
|---|---|---|---|
| active attempt | `not-run` | `pending` | `pending` |
| `needs-fix` after batch Review | `fail` | `pending` | `pending` |
| `needs-fix` after final verification | `pass` | `fail` | `pending` |
| `needs-fix` after final Review | `pass` | `pass` | `fail` |
| `blocked` during batch | `blocked` | `pending` | `pending` |
| `blocked` during final verification | `pass` | `blocked` | `pending` |
| `blocked` during final Review | `pass` | `pass` | `blocked` |
| awaiting final verification | `pass` | `pending` or `pass` | `pending` |
| `complete` | `pass` | `pass` | `pass` |

Rules:

- Every state change increments `contract_revision` by one.
- `FAIL` and `BLOCKED` never advance `current_batch`.
- A batch retry increments `attempt`; attempt-specific artifacts never overwrite
  earlier evidence. Batch recovery may return to Brief or execution, never
  directly to Review without a fresh Report.
- Every `ready-for-review` decision preserves the exact Report reference it
  reviewed. Non-final promotion requires Review PASS plus a Review artifact;
  clearing or replacing either reference in that decision is invalid.
- `ready-for-review` requires `attempt_report_artifact`. A pre-dispatch
  `blocked` state may have no Report yet; its Preflight Review still supplies
  `last_review_artifact`. Any completed batch Review, timeout audit, or blocking
  Review requires `last_review_artifact`.
- Final batch PASS keeps `current_batch == planned_batches`, sets
  `awaiting-final-verification`, and returns ownership to the router.
- Final verification PASS is persisted in a new revision before final Review.
  Direct `pending/pending -> complete` is invalid.
- Final verification FAIL/BLOCKED may only start from `pass/pending/pending`;
  final Review PASS/FAIL/BLOCKED may only start from the separately persisted
  `pass/pass/pending` revision.
- A `blocked -> blocked` metadata update preserves batch, attempt, the complete
  result tuple, and every evidence reference. It cannot change gate stage.
- Recovery from a final-gate BLOCKED state also preserves the accepted attempt
  Report and batch Review references.
- Any implementation change after final verification invalidates that PASS and
  clears its artifact before the next execution attempt.
- `complete` requires attempt Report, batch Review, final verification, and final
  Review evidence; it is terminal.
- Missing, stale, duplicated, contradictory, unsafe, or unparsable state is
  `BLOCKED` and returns to the router or user.

## Ownership And Integrity

The router creates the contract, owns readonly routing fields and final gates,
and may mark `complete`. The brief governor updates batch lifecycle fields
according to valid transitions. External agents never edit canonical status.

After the governor writes `ready-for-execution`, it hashes the complete canonical
status file. Brief and Report record that same execution revision and SHA-256.
Before moving to `ready-for-review`, the governor recomputes the hash; mismatch is
`BLOCKED`. Review records from/to revision, from/to SHA-256, and transition
validation evidence.

Validate an already persisted non-complete snapshot structurally with:

```bash
python3 scripts/validate_core_gates.py . \
  --status docs/agent-collab/<change-id>/status.md \
  --artifact-root .
```

Without `--previous-status`, `canonical_sha256` is format-checked but cannot be
matched to a prior file. Before applying any transition that introduces a new
artifact, write the proposed status to `${TMPDIR:-/tmp}`, keep the current
canonical status unchanged, and add:

```bash
--previous-status docs/agent-collab/<change-id>/status.md
```

This validates the transition and matches the new artifact's source revision
and SHA-256 to the actual prior canonical file. After PASS, atomically replace
the canonical status with the proposed file and preserve the command result as
evidence. Never persist the proposed or previous marker snapshot inside the
project; the project must still contain exactly one Handoff marker block.

`complete` mechanically requires this previous-status check. The validator
rejects a complete single snapshot because it cannot prove the sequential final
transition. Keep any temporary previous/proposed snapshot outside the project
only until closure validation finishes, then delete it.

### Trust Boundary

`--previous-status` proves one transition against the current canonical file; it
does not independently reconstruct or cryptographically authenticate every
earlier revision. This workflow trusts that the governor has not rewritten the
current canonical prior state and that each earlier transition PASS output is
retained in repository evidence/history. A hostile actor able to forge the
prior state and all artifacts is outside this lightweight validator's threat
model; append-only journals or signatures would be a separate, heavier design.

## Upgrade From Schemas 4 And 5

Schema 6 is a hard switch for contracts created after deployment. Before the
switch, inventory every known active schema-4/schema-5 canonical status and
require it to reach `complete` under the matching old workflow. Do not rewrite,
silently migrate, resume after cutover, ignore, or abandon an active old
contract. Retain the no-active-legacy inventory result as upgrade evidence.
Historical complete schema-4/schema-5 contracts and their evidence remain
byte-immutable history; they cannot produce current PASS, transition, resume,
or completion authority.
