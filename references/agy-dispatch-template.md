# Antigravity CLI Dispatch Template

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

```bash
agy --print-timeout 30m --print "$(cat <<'EOF'
项目路径：<project-path>

请按以下 Brief 执行 <change-id> Step <NN>：
docs/agent-collab/<change-id>/<NN>-attempt-<AA>-brief.md

Canonical status（只读，不得修改）：
docs/agent-collab/<change-id>/status.md
Execution revision / canonical SHA-256：<revision> / <64 lowercase hex>
Executor product / instance / role / profile：antigravity-cli / <id> / executor / <profile>
Reviewer product / instance / role / profile：<values; different instance>
Control plane product / instance / role / profile：codex / <id> / control-plane / control-plane-high
Decision source / Confirmation Lease：<provenance> / <decision-id/path/hash>

执行完成后，请生成报告：
docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report.md

如果遇到越界、阻塞或需要 Codex 判断的问题，请停止并生成：
docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report-abort.md

硬性要求：
- 只允许修改 Brief 指定文件
- 禁止修改 Brief 禁止范围
- 禁止 git add / git commit / git reset / git clean
- 必须运行 Brief 中列出的验证命令
- 不得修改 canonical status 或复制 Handoff Contract marker block
- 报告必须记录 schema_version 6 / contract_revision / batch / attempt 指纹和
  与 Brief 相同的 canonical SHA-256
- 报告必须内嵌完整 schema-2 `attempt-report` evidence manifest；result、
  change、batch、attempt、execution revision/SHA-256、agent product/instance/
  role/profile 缺一不可；禁止别名、实例冒充或 profile 越权
- 平台命令权限不是业务/生产批准；Lease 失效、scope/risk/approval 变化必须 BLOCKED
- 报告需包含修改文件、验证命令与结果、Evidence 表、raw/summary 产物路径、是否偏离 Brief、剩余风险
- 如果 Brief 要求 server/API/business-chain 回归，pytest 通过不能替代真实链路验证
- 缺少关键证据时必须写 BLOCKED，不得写 PASS
- FAIL/BLOCKED 后不得推进 batch；修正或恢复必须由 Codex 分配新 attempt
EOF
)"
```

## Optional Runtime Environment Advice

Append the following block only when this dispatch crosses one actual approved
model/reasoning execution boundary. If the current runtime is sufficient, omit
the entire block. If an upstream control-plane response already contains it,
copy it verbatim; do not regenerate it from chat history or ask for another
notice. The block is human-readable and outside all machine-readable Handoff
marker material.

```text
运行环境建议：
- 目标 Session：
- 推荐模型：
- 推理强度：
- 切换原因：
- 可复制任务提示词：
- 完成后切回：
```
