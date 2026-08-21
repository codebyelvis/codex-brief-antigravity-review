# Review Result: PASS / FAIL / BLOCKED

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

文档类型：Review
日志及版本：YYYY-MM-DD v1
批次及尝试：Step <NN> Attempt <AA>

<!-- COOP_EVIDENCE_MANIFEST_START -->
```yaml
evidence_schema_version: 2
evidence_role: batch-review
evidence_result: pass
change_id: <change-id>
current_batch: <NN>
attempt: <AA>
contract_revision: <reviewed canonical revision>
canonical_sha256: <reviewed canonical SHA-256>
agent_product: <canonical reviewer product>
agent_instance_id: <canonical reviewer instance>
agent_role: independent-reviewer
capability_profile: control-plane-high
```
<!-- COOP_EVIDENCE_MANIFEST_END -->

按实际阶段将 `evidence_role` 设为 `batch-review`、
`preflight-review` 或 `final-review`，并让 `evidence_result` 与
最终 `PASS` / `FAIL` / `BLOCKED`（小写）一致。保存并计算 SHA-256
后不得改写。`contract_revision` 和 `canonical_sha256` 指向本 Review
实际读取的 transition 前 canonical status。

Standard/strict batch Review 的 product/instance/role/profile 必须等于
immutable reviewer assignment，且 reviewer instance 不同于 executor instance；
产品相同也不能 self-review。Compact 把完整 reviewer assignment 绑定到
control-plane identity、保持与 executor instance 不同，并记录顶层非空
not-applicable reason。Preflight 与 final Review 使用各自 immutable assignment。
别名、实例冒充和 executor self-review 均无效。

Preflight 只使用 `PASS`/`BLOCKED`。仅 `BLOCKED` Preflight 以
`preflight-review: blocked` 绑定 canonical `blocked` 状态；Preflight
PASS 只授权 dispatch，不能充当 `batch-review` 或批次完成证据。

## Summary

一句话结论。必须说明是完整通过、执行失败，还是证据/依赖阻塞。

## Review Scope

- Brief：`file:///absolute/path`
- Report：`file:///absolute/path`
- Changed files：`file:///absolute/path`
- Raw artifacts：`file:///absolute/path`
- Summary artifacts：`file:///absolute/path`

## Findings

按严重程度列问题：

任何 actionable finding（无论严重级别）都必须修正、重新验证并再次
Review。非阻塞观察只有在明确记录为 accepted residual risk，并注明 owner
或决策时，才不属于未解决 finding。

### Critical

- <scope violation / missing critical evidence / real regression failure / destructive git operation>

### Major

- <incomplete evidence / weak artifact / unclear acceptance boundary>

### Minor

- <non-blocking issue>

## 1. Brief 遵守情况

| 检查项 | 结果 | 证据 |
|---|---|---|
| 只改允许文件 | PASS/FAIL/BLOCKED | <path/status> |
| 未触碰禁止范围 | PASS/FAIL/BLOCKED | <negative search/status> |
| 生成 report/abort | PASS/FAIL/BLOCKED | <path> |
| 保留 worktree 状态 | PASS/FAIL/BLOCKED | <git status> |
| Handoff Contract 唯一且可解析 | PASS/FAIL/BLOCKED | <marker/schema check> |
| readonly fields 未被外部 Agent 改写 | PASS/FAIL/BLOCKED | `mode` / `approval_status` / `risk_profile` |

## 2. Git 状态检查

```bash
git status --short
```

结果：<pass/fail/blocking reason>

- staged 改动：无 / 有，说明：<details>
- unstaged 改动：无 / 有，说明：<details>
- untracked 文件：无 / 有，说明：<details>
- 范围外改动：无 / 有，说明：<details>

## 3. 验证命令核查

| Brief 要求命令 | Report 是否执行 | Codex 是否复核 | 结果 | 证据 |
|---|---:|---:|---|---|
| `<command>` | 是/否 | 是/否/无法 | PASS/FAIL/BLOCKED | `<path/output>` |

规则：Brief 要求的 critical 命令未执行或无证据时，Final Decision 必须是 `BLOCKED`。

## 4. 业务验收核查

| 验收层级 | Brief 是否要求 | Report 证据 | Codex 复核 | 结论 |
|---|---:|---|---|---|
| 单元测试 | 是/否 | <path/output> | <result> | PASS/FAIL/BLOCKED |
| 管线测试 | 是/否 | <path/output> | <result> | PASS/FAIL/BLOCKED |
| server / API / `/chat` 回归 | 是/否 | <raw/summary/log> | <result> | PASS/FAIL/BLOCKED |
| 真实业务问题 | 是/否 | <assertions> | <result> | PASS/FAIL/BLOCKED |

规则：如果 Brief 要求 server/API/真实业务回归，而 Report 只有 pytest 证据，Final Decision 必须是 `BLOCKED`。
规则：如果真实回归仍复现问题，Final Decision 必须是 `FAIL`。
规则：如果外部依赖不可用导致无法判断业务修复，Final Decision 必须是 `BLOCKED`。

## 4.1 Contract Consensus

| 字段 | Brief | Report/Status | 结论 |
|---|---|---|---|
| `change_id` | `<value>` | `<value>` | PASS/FAIL/BLOCKED |
| `schema_version` | `6` | `6` | PASS/FAIL/BLOCKED |
| Execution revision | Brief `<n>` | Report `<n>` | PASS/FAIL/BLOCKED |
| Execution canonical SHA-256 | Brief `<hash>` | Report/recomputed `<hash>` | PASS/FAIL/BLOCKED |
| Review revision | expected `<n+1>` | canonical status `<n+1>` | PASS/FAIL/BLOCKED |
| `risk_profile` | compact/standard/strict | compact/standard/strict | PASS/FAIL/BLOCKED |
| `current_batch` | `<n>` | `<n>` | PASS/FAIL/BLOCKED |
| `attempt` / `lifecycle_state` | `<AA>` / `<state>` | `<AA>` / `<state>` | PASS/FAIL/BLOCKED |
| `next_owner` | `<owner>` | `<owner>` | PASS/FAIL/BLOCKED |
| `verification_strategy` | `<summary>` | `<summary>` | PASS/FAIL/BLOCKED |
| control plane product / instance / role / profile | `<values>` | `<values>` | PASS/FAIL/BLOCKED |
| executor product / instance / role / profile | `<values>` | `<values>` | PASS/FAIL/BLOCKED |
| reviewer product / instance / role / profile | `<values>` | `<values>` | PASS/FAIL/BLOCKED |
| decision source / Confirmation Lease / status | `<values>` | `<values>` | PASS/FAIL/BLOCKED |

Transition evidence（from/to revision 与 SHA-256）：

| 字段 | 值 |
|---|---|
| from/to revision | `<from>` / `<to>` |
| from/to canonical SHA-256 | `<from hash>` / `<to hash>` |
| transition validator result | PASS / FAIL / BLOCKED |
| `attempt_report_artifact` path / SHA-256 | `<path>` / `<hash>` |
| `last_review_artifact` path / SHA-256 | `<path>` / `<hash after this Review is written>` |

## 4.2 High Review Mechanism Audit

| Required evidence | Result | Artifact / path:line |
|---|---|---|
| actual files and complete diff inspected | PASS/FAIL/BLOCKED | `<diff/path>` |
| copy/transform/production wiring trace | PASS/FAIL/BLOCKED | `<chain>` |
| `step_critical` / `final_critical` rerun | PASS/FAIL/BLOCKED | `<output>` |
| claim-to-mechanism support | PASS/FAIL/BLOCKED | `<runner/runtime mechanism>` |
| independent adversarial or real business-chain probe | PASS/FAIL/BLOCKED | `<bounded probe>` |

A green executor test is insufficient when a copied field is lost, production
wiring is absent, or a behavior claim is only metadata. Any such finding is
`FAIL` or `BLOCKED` and must enter a fresh fix -> verify -> Review loop.

## 5. 子问题覆盖矩阵

| 子问题 | 当前是否覆盖 | 验证方式 | 结果 | 是否允许泛化 |
|---|---:|---|---|---:|
| <子问题 A> | 是/否 | <artifact/assertion> | PASS/FAIL/BLOCKED | 否 |

## Required Fixes

- <必须修复或补充的事项>

## Verification

列出 Codex 已复核命令和结果：

```bash
<command>
```

结果：PASS / FAIL / BLOCKED

## Decision Rules Applied

- 有任何越界修改：`FAIL`
- 有破坏 worktree / 未授权 git 操作：`FAIL`
- 有关键验证缺失：`BLOCKED`
- Brief 要求 server/API/business-chain 回归但未跑完整：`BLOCKED`
- 外部依赖不可用、LLM/API 502、server 无法启动导致无法判断：`BLOCKED`
- 真实回归失败：`FAIL`
- Handoff Contract 缺失、重复、不可解析或 readonly fields 被改写：`BLOCKED`
- 所有 Brief 要求满足且业务验收通过：`PASS`

## Required State Transition

- `FAIL`：保持 same batch，设置 `needs-fix`、`last_review_result: fail`，
  `attempt + 1`，由 governor 生成新的 correction Brief。修正、验证后 must be reviewed again。
- `BLOCKED`：保持 same batch，设置 `blocked`、`last_review_result: blocked`，
  并填写 `blocked_reason`、`blocker_owner`、`resume_condition`。恢复后使用新 attempt、刷新证据，并 must be reviewed again。
- 非最终 `PASS`：`current_batch + 1`、`attempt: 1`、`ready-for-brief`。
- 最终 `PASS`：保持最终 batch，设置 `awaiting-final-verification`、
  `final_verification: pending`、`final_review_result: pending`、
  `next_owner: openspec-superpower-change`；不得声明任务完成。
- Router 必须先以同状态新 revision 持久化 `final_verification: pass` 及
  hashed manifest，再执行最终 Review；不得把两个 final gate 原子化为
  `complete`。
- 每次状态变更：`contract_revision + 1`。

## Final Decision

PASS / FAIL / BLOCKED

## Next Step

- Next-step permission: yes/no
- Next-step owner: openspec-superpower-change / codex-brief-antigravity-review / external-agent / user
- Required next action: <brief/report/fix/user decision>
