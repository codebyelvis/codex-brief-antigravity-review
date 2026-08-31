# <change-id> Step <NN> Attempt <AA> Brief

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

文档类型：Implementation Brief
日志及版本：YYYY-MM-DD v1
执行角色：<codex/pi/antigravity-cli/grok-cli> / <step role>
预计耗时：<例如 30m；超过后 Codex 可写 timeout audit>

## 1. 项目路径

`<absolute project path>`

## 2. 任务目标

<只描述本步骤要完成的目标，禁止扩展范围。明确本步骤是修复、验证、调查还是只产出报告。>

## 2.1 Canonical Handoff Contract

唯一可变 marker block 必须位于：

```text
docs/agent-collab/<change-id>/status.md
```

本 Brief 只引用 canonical status，不得嵌入第二份 marker block。记录指纹：

| 字段 | 值 |
|---|---|
| `schema_version` | `6` |
| `contract_revision` | `<n>` |
| `current_batch` / `planned_batches` | `<NN>/<total>` |
| `attempt` | `<AA>` |
| `lifecycle_state` | `ready-for-execution` |
| control plane product / instance / role / profile | `codex` / `<id>` / `control-plane` / `control-plane-high` |
| executor product / instance / role / profile | `<product>` / `<id>` / `executor` / `<profile>` |
| reviewer product / instance / role / profile | `<product>` / `<different id>` / `independent-reviewer` / `control-plane-high` |
| `decision_source` | `<allowed provenance>` |
| Confirmation Lease decision ID / path / SHA-256 / status | `<id>` / `<path>` / `<hash>` / `valid` |
| canonical SHA-256 | `<64 lowercase hex>` |

若 Contract 缺失、重复、过期、矛盾或不可解析，本 Brief 不得继续，必须交回 `openspec-superpower-change` 或用户。

不可覆写字段：canonical `readonly_fields` 中的完整集合，而不只是
`mode`、`approval_status`、`risk_profile`。

Report 必须回显同一 execution revision 和 canonical SHA-256。Codex 在进入
`ready-for-review` 前重新计算 canonical 文件哈希；不一致时必须 BLOCKED。
Report 的 schema-2 manifest 将 `agent_product` / `agent_instance_id` /
`agent_role` / `capability_profile` 绑定为 canonical executor assignment。
Standard/strict Review 必须使用不同 reviewer instance；产品相同也不能
self-review。Compact 必须把完整 `reviewer_assignment` 绑定到 control-plane
identity、保持与 executor instance 不同，并记录顶层非空 not-applicable reason。

手工复制本 Brief 不会降级治理。任何 state-changing standard/strict 工作
仍须引用相同 canonical status、Report path、allow-list 与 evidence chain。

## 2.2 Evidence Profile

Profile：compact / standard / strict

- compact：仅保留必要目标、allow-list、验证命令、报告路径和阻塞条件。
- standard：必须包含函数级地图、数据合同、不变量、错误矩阵、TDD RED/GREEN、生产 wiring、业务验收层和 step-critical。
- strict：必须保留安全/API/schema/迁移/回滚/真实业务链证据；mock 或单测不得替代明确要求的真实验收。

所有 profile 的 `step_critical`、`final_critical` 和 `stop_conditions` 都必须
至少包含一个非空白条目。

## 2.3 Preflight Review

Dispatch 前必须对本 Brief 当前 revision 执行 **Preflight Review**：

- 合同/计划覆盖、占位符和范围；
- allow-list、生产 wiring 与验收层；
- 精确验证命令、证据等级、回滚和停止条件；
- worktree/branch 决定及 Git 授权。

结果：PASS / BLOCKED

- `BLOCKED`：任何 actionable finding 都不得 dispatch；canonical 转为
  `blocked`，新 attempt 修订 Brief 后重新 Preflight Review。Preflight
  不使用 `FAIL`；`FAIL` 保留给已执行行为的实施 Review。写入独立
  `preflight-review: blocked` manifest，并在替换 canonical 前使用
  `--previous-status` 验证 proposed transition。
- `PASS`：仅授权 dispatch，不是实施 Review 或完成证据。
- Brief revision 未变化时不重复；发生任何语义修改后必须重跑。

## 2.4 Authorization, Lease, Partial State, And Escalation

- Tool/platform authorization：<已有权限；只表示平台可执行>
- Scope/workflow authorization：<批准 Change/Plan/Brief revision 与 allow-list>
- Business/production authorization：<required / not-required；证据或用户决定>
- Confirmation Lease reuse：yes / no；失效原因：<scope/risk/revision/production/user decision>
- Existing partial/dirty state：<已检查文件与未完成片段>
- Do-not-repeat scope：<已完成且不得重做的步骤/文件>
- `mechanical-low` / `cohesive-medium` 遇到歧义、意外失败、安全字段、
  禁止文件、生产凭据、scope/risk/approval 变化时立即 `BLOCKED`，不得设计或扩展范围。

## 2.5 Optional Runtime Environment Advice

仅当本步骤实际发生模型或推理强度切换时，才附带控制面为该切换生成的一次完整块；当前运行环境足够时省略整段。若上游已有该块，逐字复制，不从 chat history 重生成，也不再次询问。该人类可读块必须位于所有机器可读 schema-6 Handoff marker 之外，且不得写入 canonical `docs/agent-collab/<change-id>/status.md` 或参与其哈希、权限、生命周期和 PASS/FAIL/BLOCKED 校验。

```text
运行环境建议：
- 目标 Session：
- 推荐模型：
- 推理强度：
- 切换原因：
- 可复制任务提示词：
- 完成后切回：
```

## 3. 允许修改的文件

只允许修改：
- `<path>`

## 4. 禁止修改的范围

禁止修改：
- `<path>`
- qflow / prompt / 文档工具 / 配置 / 其他未授权范围：<按任务列出>
- 任何 git 操作（不要 `git add` / `git commit` / `git reset` / `git clean`）

## 5. Git / 工作区硬约束

- 执行前必须记录 `git status --short`。
- 禁止 `git add`。
- 禁止 `git commit`。
- 禁止 `git reset`。
- 禁止 `git clean`。
- 禁止丢弃用户已有 staged / unstaged / untracked 改动。
- 若存在 staged 改动且 Brief 未明确授权处理，必须停止并写 `<NN>-attempt-<AA>-report-abort.md`。
- 若 Brief 明确允许处理 staged 状态，只能执行被授权的命令，并必须保留工作区改动和记录前后状态。

## 6. 允许副作用

默认不允许文件修改以外的副作用。若本步骤需要命令、网络、数据库、环境变量、缓存、后台服务、server 启停或外部 API 调用，必须在此列明：

- `<side effect>`：<目的、边界、回滚方式>

### 备份要求（若允许修改 skill / 模板，必须创建结构化备份）

- 临时备份目录：`${TMPDIR:-/tmp}/<backup-dir-name>/`（或 Brief 明确授权的位置）。
- 结构规范：备份必须保留相对路径结构（例如 `codex-brief-antigravity-review/SKILL.md`），禁止使用扁平列表备份，以防回滚歧义。
- 备份仅用于失败回滚，不作为历史版本。
- 完成测试、验证和归档同步后必须删除临时备份、`.bak.*` 文件和 `${CODEX_HOME:-$HOME/.codex}/skills/` 下可被发现的 `*.backup*` skill 目录。
- 历史版本通过配置的 `openspec-superpower-change` 和 `codex-brief-antigravity-review` source repository git history 管理。
- 若验证失败或需要回滚，临时备份只保留到回滚/用户决策完成。

## 7. 需求来源

- Plan：`docs/superpowers/plans/YYYY-MM-DD-<change-id>.md`
- OpenSpec delta：`openspec/changes/<change-id>/specs/.../spec.md`
- Previous Review：`docs/review/...`
- User issue / bug evidence：`<path or pasted summary>`

## 8. 子问题列表与覆盖边界

| 子问题 | 本步骤是否覆盖 | 验证方式 | 不覆盖时的说明 |
|---|---|---|---|
| <子问题 A> | 是/否 | <command/artifact/assertion> | <reason> |
| <子问题 B> | 是/否 | <command/artifact/assertion> | <reason> |

> 不得把某个子问题的局部修复泛化为整个业务问题已修复。

## 8.1 Standard / Strict 实现细节

### 函数级变更地图

| 文件 | 函数/类型 | 当前行为 | 目标行为 | 调用方/消费者 |
|---|---|---|---|---|
| `<path>` | `<symbol>` | <fact> | <target> | `<caller>` |

### 数据合同

| 字段 | 类型 | 可选性 | 默认值 | 生产者 | 消费者 |
|---|---|---:|---|---|---|
| `<field>` | `<type>` | 是/否 | `<value>` | `<producer>` | `<consumer>` |

### 不变量与错误矩阵

| 不变量 / 失败点 | 预期 | 是否阻断 | 必须证据 |
|---|---|---:|---|
| <invariant or failure> | <expected> | 是/否 | `<artifact>` |

### TDD 与生产 wiring

- RED 测试名称：
- 当前实现为什么必须失败：
- GREEN 最小实现路径：
- 生产数据入口到最终消费者路径：
- 不允许测试通过但生产 wiring 未接入。

## 9. 必须执行的验证命令

Critical commands（Codex Review 必须重跑或给出阻塞说明）：

```bash
<critical command>
```

Supporting commands（执行者必须运行；Codex Review 至少抽查一项或检查对应行为）：

```bash
<supporting command>
```

## 10. 业务验收标准

明确区分以下层级，并标明哪些层级是本步骤 `PASS` 的必要条件：

| 验收层级 | 是否必须 | 验证方式 | PASS 条件 |
|---|---:|---|---|
| 单元测试 | 是/否 | `<pytest ...>` | <expected> |
| 管线测试 | 是/否 | `<command>` | <expected> |
| server / API / `/chat` 回归 | 是/否 | `<curl/script/raw SSE>` | <expected> |
| 真实业务问题 | 是/否 | <artifact/assertion> | <expected> |

如果本 Brief 要求 server / API / `/chat` 回归，则 pytest 通过不能替代业务链路通过，单元测试通过也不能替代业务链路通过。

## 11. Key Assertions（关键断言）

| 断言 | 期望 | 证据产物 |
|---|---|---|
| <例如 answer 中 forbidden string 次数> | 0 | `<raw/summary path>` |
| <例如 是否进入文档工具> | 是 | `<raw/summary path>` |
| <例如 server /chat 是否跑完整> | 是 | `<raw/summary path>` |

## 12. 阻塞处理

如果遇到依赖、LLM 502、server 无法启动、外部服务不可用、未进入目标工具、权限不足或验证命令无法完成：

- 不得声称 `PASS`。
- 必须生成 `<NN>-attempt-<AA>-report-abort.md` 或在 report 结论写 `BLOCKED`。
- 必须写清楚阻塞命令、错误、已完成操作、raw 输出路径、下一步需要 Codex / 用户 / 外部服务做什么。
- 缺少 Handoff Contract、只读字段被改写、`current_batch > planned_batches`、或 `step_critical` / `final_critical` 混用时，必须 BLOCKED。
- `FAIL` 修正或 `BLOCKED` 恢复必须使用新的 `<AA>`，保留同一批次且不得复用旧证据。
- 外部 Agent 不得修改 canonical `status.md`；只在 Report 中提供证据与建议结果。

## 13. 质量门禁

```bash
git diff --check -- <allowed files>
```

## 14. 执行报告

执行完成后生成：
- `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report.md`

报告必须包含：
- 修改文件列表
- `git status --short` 前后状态
- 验证命令与结果，区分 critical / supporting
- Evidence：Commands / Artifacts / Key Assertions
- canonical execution revision / SHA-256 与 Report artifact path / SHA-256
- raw / summary 产物路径
- 子问题覆盖矩阵
- 业务验收结论，区分单元测试、管线测试、server/API、真实业务问题
- Diff Summary：`git diff --stat` 与关键 hunk 摘要
- 是否偏离 Brief
- BLOCKED / FAIL 时的阻塞项或必修项
- 剩余风险
