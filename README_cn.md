# codex-brief-antigravity-review

[English](README.md) | [简体中文](README_cn.md)

`codex-brief-antigravity-review` 是一个用于编写 Antigravity/Codex 任务提示并复核 diff、Report 和证据的 Codex Skill。独立提示词/只读 Review 保持轻量；只有 `openspec-superpower-change` 已完成交接后，才进入结构化外部执行治理。

## 亮点

- 独立编写或优化 task prompt、Brief、checklist，无需 OpenSpec/Handoff。
- Standalone Review 必须由用户明确请求、仅作用于当前请求、采用 findings-first 输出，且生成变更后绝不自动串联触发。
- 每次 standalone Review 请求或推荐都必须说明非空 purpose、一个具体 reviewer
  产品、角色、能力 profile、独立性与仅证据性质的结果权限。
- 普通 diff/证据只读 Review 不伪造批次推进。
- 将已批准实施计划转化为带 attempt 的批次 Brief。
- 将编排与评审从具体实现执行中分离。
- 要求外部 Agent 输出结构化 Report 或 Abort Report。
- 在写出 PASS、FAIL 或 BLOCKED 前审计证据。
- 防止关键证明缺失时产生虚假 PASS。
- `FAIL`/`BLOCKED` 保留 attempt 历史，修正/解阻后必须再 Review。
- 只以 canonical `status.md` 保存共享状态，最终批次 PASS 回交总入口验证。
- Dispatch 前对当前 revision 的 Brief 执行 Preflight Review。
- 当前 schema 6 / schema 2 证据绑定完整且不可变的 Reviewer Assignment；冻结的
  schema 4/5 只能通过只读、非授权 legacy audit 使用。
- Codex、Pi、Antigravity CLI 与 Grok CLI 在被指派的 executor/reviewer 角色上
  资格同等。产品名本身不授予权限；只有绑定的 Codex `control-plane` /
  `control-plane-high` 实例及合同可以接受证据或推进 canonical state。
- 手工复制的 state-changing standard/strict Brief 仍走 canonical Handoff；
  High Review 必须检查真实 diff、生产 wiring、机制证据和独立探针。

## 为什么需要它

长时间实施任务如果由同一个 Agent 负责所有环节，风险很高。常见失败模式包括：

- 上下文过载并遗漏约束；
- 规划者与实施者职责不清；
- 成功声明缺少原始证据；
- 文件修改范围超出批次边界；
- 跳过关键命令复跑；
- 上一个批次尚未证明就推进下一批次。

该 Skill 固化了严格的 Brief -> Dispatch -> Report -> Review 循环。

## 角色边界

| 角色 | 职责 |
|---|---|
| Codex standalone | 编写 prompt/Brief/checklist 或只读 Review diff/证据；不维护 Handoff 或推进批次。 |
| 绑定的 Codex control plane | 读取已批准计划、指派角色、编写 attempt Brief、审计 governed evidence，并独占 canonical transition 决策。 |
| 被指派的 executor/reviewer | Codex、Pi、Antigravity CLI 或 Grok CLI 均可承担明确指派的角色，遵守实例/独立性边界，并且只返回证据。 |
| Handoff Contract | 只在 canonical `status.md` 保存 batch、attempt、lifecycle、阻塞恢复和最终回交状态。 |
| openspec-superpower-change | 在本 Skill 接手前，负责请求路由、OpenSpec 审批状态、风险等级和实施授权。 |

Standalone 路径不得修改实现；handed-off 路径不得重新判断 OpenSpec 审批或风险分类。

Handed-off 路径按需完整读取
`references/handed-off-external-execution.md`；standalone 路径不读取该治理流程。

## 工作流

```text
Standalone：编写/优化 prompt 或只读 Review diff/Report -> 返回结论

Handed-off：读取 canonical Handoff Contract
-> 读取当前批次/attempt 的已批准计划
-> 写 <NN>-attempt-<AA>-brief.md
-> 绑定 canonical execution SHA-256 并 Preflight Review Brief
-> 派发外部 Agent
-> 要求 attempt Report 或 Abort Report
-> 根据证据审计 Report 声明
-> 在可行时复跑关键检查
-> 写 step review：PASS / FAIL / BLOCKED
-> FAIL/BLOCKED：同批次新 attempt，再次 Review
-> 非最终 PASS：下一批
-> 最终 PASS：回交 openspec-superpower-change 做最终验证
```

明确请求的 standalone OpenSpec Review 保持简洁，并检查：

- proposal 范围；
- spec 场景；
- design 决策与风险；
- task 可追溯性；
- 跨产物一致性。

## 路由决策详解

只有两条合法路线，一个请求不得在两者之间暗中漂移。

### Standalone Lightweight

仅在用户明确要求编写/优化 prompt、Brief、checklist，或只读 Review
diff、Report、证据集、OpenSpec 产物时使用。它只返回本次请求的文案
或 findings；不修改项目文件，不创建/变更 `status.md`，不派发实施批次，
不推进 lifecycle，不决定最终完成，也不在产出产物后自动串联 Review。一旦
请求包含修复 finding 或改变行为，必须返回 `openspec-superpower-change`。

### Canonical Handoff

仅在有效的 canonical Handoff Contract 已记录路由器审批、风险/证据等级、
batch/attempt、owner 和当前 lifecycle 时使用。本 Skill 随后才可对当前 Brief
执行 Preflight、派发绑定 executor、审计 attempt Report、绑定 Review 证据并
记录 `PASS` / `FAIL` / `BLOCKED`。失败必须留在同一 batch 并使用新 attempt；
非最终 PASS 可推进；最终批次 PASS 将 `awaiting-final-verification` 回交路由器。
它不得冒充路由器审批，也不得把批次 PASS 改写为整个任务完成。

## 产物路径

| 产物 | 路径 |
|---|---|
| Brief | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-brief.md` |
| Report | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report.md` |
| Abort Report | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report-abort.md` |
| Status / Handoff Contract | `docs/agent-collab/<change-id>/status.md` |
| Review | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-attempt-<AA>-review.md` |
| Timeout Audit | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-attempt-<AA>-timeout-audit.md` |

## 证据等级

| 等级 | 典型场景 |
|---|---|
| compact | 低风险批次，使用聚焦命令和简洁报告。 |
| standard | 默认实施批次，需要函数映射、数据合同、不变量、错误矩阵、RED/GREEN 证据和业务验收层。 |
| strict | 安全、认证、权限、公开 API/schema、持久化、迁移、部署、回滚或跨租户变更。 |

## 仓库结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── brief-template.md
│   ├── report-template.md
│   ├── review-template.md
│   ├── agy-dispatch-template.md
│   ├── timeout-audit-template.md
│   └── handoff-contract.md
├── scripts/
│   └── validate_templates.py
└── tests/
    └── test_workflow_rules.py
```

## 关键参考文件

- `references/brief-template.md`：Brief 必填章节和证据要求。
- `references/report-template.md`：外部 Agent 实施报告格式。
- `references/review-template.md`：PASS / FAIL / BLOCKED Review 合同。
- `references/agy-dispatch-template.md`：派发 prompt 和命令结构。
- `references/timeout-audit-template.md`：超时或 Report 缺失审计格式。
- `references/handed-off-external-execution.md`：仅 Handoff 路径读取的完整 governor 流程。
- `references/handoff-contract.md`：Codex 与外部 Agent 的共享状态合同。

## 核心规则

- 每份 Brief 必须列出允许文件、禁止文件、abort 条件、report 路径和关键证据。
- 外部 Agent 不得覆盖由路由器拥有的 Handoff Contract 字段。
- Report 缺失、关键证据缺失、原始 artifact 缺失或依赖不可达，结论为 `BLOCKED`。
- 越界文件修改、破坏性 git 操作或回归仍可复现，结论为 `FAIL`。
- 除非明确声明相关层不适用，否则单元测试不能单独证明 API、服务或真实业务成功。
- 只有 `PASS` 才能推进批次指针或授权下一份 Brief。
- 每个外部 evidence profile 都必须有非空 step/final critical 命令。
- Report/Review 证据必须是项目相对路径、非空文件、SHA-256 匹配，并内嵌
  schema-2 role/result/change/batch/attempt/source fingerprint manifest，以及
  被分配的 product、instance、role 和 capability profile。
- 便携变更只有在 Codex/Pi/Antigravity/Grok 四个必需 runtime 都通过共享同步门后
  才完整；Pi 使用 `${PI_CODING_AGENT_DIR}/skills`，managed global rule 位于
  `${PI_CODING_AGENT_DIR}/APPEND_SYSTEM.md`。

## 安装

复制或链接到 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codex-brief-antigravity-review "${CODEX_HOME:-$HOME/.codex}/skills/codex-brief-antigravity-review"
```

## 验证

修改 Skill 后运行：

```bash
"${PYTHON_BIN:-python3}" "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" /path/to/codex-brief-antigravity-review
PYTHONDONTWRITEBYTECODE=1 python3 /path/to/codex-brief-antigravity-review/scripts/validate_templates.py /path/to/codex-brief-antigravity-review
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s /path/to/codex-brief-antigravity-review/tests -v
```

当前受治理状态使用 schema 6。运行时可使用 `--status <status.md>` 和
`--artifact-root <project-root>` 验证其 schema-2 evidence manifest。引入证据
的 transition 应增加 `--previous-status <canonical-status>`；`complete` 强制
要求。proposed/previous 快照必须留在项目外，确保项目中仍只有一个
canonical Handoff marker block。

冻结的 schema-4/schema-5 记录只能作为 legacy audit/drain 输入。必须通过
`--legacy-inventory-root` 与 `--legacy-inventory-output` 单独盘点，不得交给
当前 `--status` 校验，也不得迁移成 schema 6。

`quick_validate.py` 需要 PyYAML；请通过 `PYTHON_BIN` 选择可用解释器。项目 validator 和测试会覆盖无 PyYAML fallback。

## 示例 Prompt

```text
Use codex-brief-antigravity-review to write the next implementation brief from the approved plan. Do not edit implementation files.
```

```text
Use codex-brief-antigravity-review to audit the latest external-agent report, rerun critical evidence where possible, and write a PASS / FAIL / BLOCKED review.
```

```text
Use codex-brief-antigravity-review to resume shared status and determine whether the next batch may start.
```

```text
Use codex-brief-antigravity-review standalone mode to improve this Antigravity task prompt. Do not create Handoff artifacts or modify project files.
```

## 维护说明

- 本 Skill 可独立处理 prompt/只读 Review；只有 handed-off 路径消费 `openspec-superpower-change` 的路由和审批决策。
- 当用户要求外部 Agent 实施时，不得用 Codex subagent 替代指定外部 Agent。
- 不得把 Report 当成证明；必须审计证据，并在可行时复跑关键检查。
- 除非 Review 结果为 PASS，否则不得推进共享状态。
- 最终批次 PASS 不等于任务完成，必须回交 `openspec-superpower-change`。

## License

MIT. See [LICENSE](LICENSE).
