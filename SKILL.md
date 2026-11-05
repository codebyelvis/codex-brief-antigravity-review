---
name: codex-brief-antigravity-review
description: "Use for explicitly requested standalone non-state-changing Antigravity/Codex prompt or brief wording, and read-only diff/report/evidence review that does not request fixes or decide final completion; also use for dispatch/review/resume of an external-agent batch with an existing valid Handoff Contract. Do not use for file edits, review-and-fix, final completion, or workflow/template changes. 可按用户要求用 caveman 风格压缩表达。"
---

# Codex Brief & Antigravity Review

Focused prompt and review skill with two mutually exclusive paths. It stays
lightweight for standalone wording/read-only review and becomes an external
execution governor only when a valid Handoff Contract already exists.

## Route Selection

1. Use **Standalone Lightweight** when the request only writes/refines a
   prompt, Brief, checklist, or performs read-only diff/Report/evidence review.
2. Use **Handed-off External Execution** when canonical `status.md` contains a
   valid Handoff Contract and the task is dispatch, Report audit, retry,
   recovery, or batch promotion. A manually copied state-changing standard or
   strict Brief uses this same route; copy/paste does not make it standalone.
3. Load `openspec-superpower-change` only for explicit OpenSpec, change-gate
   or routing requests, 「迭代优化skill」, or explicit archive/distillation requests.
   Existing valid Handoff governance retains its Router-owned decisions and
   final return. Ordinary file edits and same-scope continuation do not
   automatically load the Router.

“Review and fix” is not standalone review. Do not silently switch from review
to implementation.

When the router has already authorized safe, reversible, same-scope work, this
Companion continues the next approved step without asking for redundant
confirmation. A status report is a status update and is non-confirmation
progress, not a confirmation request. It consumes the Router-owned continuation
rule and does not re-decide scope, risk, acceptance, or authority.

Standalone compact work remains lightweight: continuation wording alone does not
create a Handoff or an OpenSpec change.

## Token-lean / Caveman output mode

`caveman` 在本 skill 里仅用于**输出压缩**，不参与治理决策。

- 触发：用户明确要求“少 token/更短/像 caveman 说”。
- 允许：`Standalone Lightweight` 的提示词、brief/review 结论、可执行项清单。
- 禁止：篡改 `SKILL.md`、`references/handoff-contract.md`、`reports`/`reviews`
  的结构化必填字段；不能代替证据复核。
- 生成 `Handoff Contract`、`Brief/Report/Review` 证明链时，使用标准模板内容；
  用户侧可读解释可再压缩，不得省略状态、文件、证据命名和哈希约束。

## Standalone Lightweight

This route is request-scoped. Do not auto-chain it after producing an OpenSpec
change or another artifact; use it only for the current explicit wording or
read-only Review request.

For OpenSpec artifacts, inspect proposal scope, spec scenarios,
design decisions and risks, task traceability, and cross-artifact consistency.
Output only scope/evidence, actionable findings, PASS/FAIL/BLOCKED, and next
action. Do not load role assignment or ROLE_FIRST classification for this route.
The verdict is advisory; it does not authorize implementation, batch promotion,
or final completion.

This path does not require an OpenSpec proposal, Handoff Contract, Superpowers
plan, or collaboration artifact. Produce the requested prompt/Brief/checklist
or a findings-first read-only review directly in chat unless the user requests
another output location.

- State the reviewed scope and evidence actually inspected.
- For a diff review, list actionable findings by severity and location.
- Do not write batch `PASS`, advance shared status, or imply implementation was
  verified when no governed batch exists.
- A request to save files, apply fixes, dispatch implementation, or change
  workflow behavior leaves standalone Review. Apply Route Selection without
  automatically loading the Router merely because files may change.

## Handed-off External Execution

When Handed-off External Execution is selected, read
`references/handed-off-external-execution.md` completely before any batch
action. Do not read it for Standalone Lightweight work.

The referenced governor preserves the complete Handoff lifecycle, evidence,
identity, correction-loop, and final-return contract. Batch `PASS` returns to
`openspec-superpower-change`; it never authorizes final task completion here.

## Non-Negotiables

- Codex does not edit implementation files while this skill is active; leave
  standalone Review and apply Route Selection if implementation is requested.
- Do not substitute an unassigned product or instance for a canonical executor or reviewer.
- Every governed Brief lists allowed/forbidden files, abort conditions, attempt
  Report path, critical evidence, and canonical status fingerprint.
- External agents must not edit canonical status or readonly fields.
- External executor and independent reviewer product/instance/role/profile must
  match the canonical assignment; standard/strict work forbids same-instance
  self-review even when the product is equal.
- Platform permission does not grant workflow scope or business/production
  approval. An invalidated or revoked Confirmation Lease is `BLOCKED`.
- Executor DONE/PASS is factual Report evidence only and cannot promote canonical
  state or authorize final completion.
- Executor or reviewer `PASS` is governed evidence only. Only the bound Codex
  control-plane contract may record an authoritative batch or final decision.
- Missing Report/evidence/required real acceptance is `BLOCKED`.
- Scope violation, destructive git operation, or reproduced regression is
  `FAIL`.
- Unit tests alone never prove API/server/real business success unless those
  layers are `not-applicable`.
- Never advance a batch or claim completion from `FAIL`, `BLOCKED`, or stale
  evidence.
- Every actionable Review finding must be fixed and reviewed again. Record a
  non-actionable observation only as an accepted residual risk with an owner or
  decision; do not leave it as an unresolved finding under PASS.
- Never run `git add`, `git commit`, `git reset`, or `git clean` unless the user
  explicitly commands it; never push without explicit approval.

## Templates

- `references/brief-template.md`
- `references/report-template.md`
- `references/review-template.md`
- `references/agy-dispatch-template.md`
- `references/timeout-audit-template.md`
- `references/handoff-contract.md`

## Maintenance

Create a temporary structured backup before editing. Editorial changes that do
not alter triggers, required fields, lifecycle, evidence, or PASS conditions may
use compact Direct Change. Semantic workflow changes are Major Self-Evolution
and must return to `openspec-superpower-change` for an approved contract,
RED/GREEN forward-test, validation, Review, rollback, runtime/source sync, and
final reporting. Remove temporary backups only after all checks pass.
