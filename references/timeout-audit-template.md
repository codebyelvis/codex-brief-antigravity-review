# <change-id> Step <NN> Attempt <AA> Timeout Audit

## Schema 6 Reviewer Assignment

| Field | Bound value |
|---|---|
| Review purpose object | `<reviewed object>` |
| Review purpose decision | `<PASS/FAIL/BLOCKED decision boundary>` |
| reviewer product | `<codex/pi/antigravity-cli/grok-cli>` |
| reviewer instance | `<contract-local instance>` |
| reviewer role | `<independent-reviewer or compact control-plane>` |
| capability profile | `<control-plane-high>` |
| `distinct_from` | `<control_plane_owner, executor_assignment or executor_assignment>` |
| result authority | `governed Review evidence only` |

These fields reproduce the immutable schema 6 `reviewer_assignment`; schema-2
evidence identity must match this parent assignment and never promotes
canonical state by itself.

文档类型：Timeout Audit
日志及版本：YYYY-MM-DD v1

<!-- COOP_EVIDENCE_MANIFEST_START -->
```yaml
evidence_schema_version: 2
evidence_role: timeout-audit
evidence_result: blocked
change_id: <change-id>
current_batch: <NN>
attempt: <AA>
contract_revision: <audited canonical revision>
canonical_sha256: <audited canonical SHA-256>
agent_product: codex
agent_instance_id: <canonical control-plane instance>
agent_role: control-plane
capability_profile: control-plane-high
```
<!-- COOP_EVIDENCE_MANIFEST_END -->

`timeout-audit` 只能是 `blocked`，不得用于 PASS/FAIL promotion。保存并
计算 SHA-256 后不得改写 manifest 或正文。
它是 Codex 治理审计而非 executor evidence，因此即使同一 artifact 同时
占用 Report 与 Review 字段，身份/角色/profile 仍绑定 canonical control-plane assignment。

## 结论

需修改

> timeout audit 的结论固定为 `需修改`，因为外部 Agent 未在约定时间内交付 Report 或 Abort Report，Codex 必须在审计后决定下一步行动。

## Review 范围

- Brief：`docs/agent-collab/<change-id>/<NN>-attempt-<AA>-brief.md`
- 预期但未收到的 Report：`docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report.md`
- 预期但未收到的 Abort Report：`docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report-abort.md`

## 超时情况

- 预计耗时：<Brief 中约定的时间限制>
- 实际等待时间：<从 dispatch 到 audit 的实际时长>
- 超时判定依据：<说明如何确认外部 Agent 未按时交付>

## Worktree 检查

- 工作树状态：`git status` 输出摘要
- 是否有部分改动：<是/否，说明发现的未完成改动>
- 改动是否在 Brief allow-list 范围内：<是/否>

## 验证记录

已运行的验证命令（如有）：

```bash
<command>
```

结果：<pass/fail/not applicable>

## 后续门禁

- Redispatch permission: yes/no
- 若 yes：<说明 redispatch 条件，例如是否需要修改 Brief、是否需要清理部分改动>
- 若 no：<说明阻塞原因和需要用户或 Codex 做的决策>
- Timeout audit required before redispatch: yes
- Handoff Contract status: present / missing / duplicated / unparsable
- Lifecycle: `blocked`; current batch unchanged; record `blocked_reason`, `blocker_owner`, and `resume_condition`
- Timeout Audit may satisfy `attempt_report_artifact` and
  `last_review_artifact` only after Codex records its project-relative path and
  SHA-256 in canonical status.
- Batch recovery must use a new attempt, return to Brief/execution rather than
  jumping directly to Review, and produce a fresh Report and fresh Review.
- Next owner: Codex / external agent / user
