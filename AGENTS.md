# AGENTS.md — myrag 项目协作规范

> 本文档定义 AI Agent 与开发者协作时必须遵守的规则。所有参与者（人 & Agent）均以此为准。

---

## 1. 分支命名规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能开发 | `feature/rag-retrieval-pipeline` |
| `update/` | 功能增强或重构 | `update/improve-embedding-cache` |
| `docs/` | 文档变更 | `docs/api-reference-update` |
| `bugfix/` | Bug 修复 | `bugfix/fix-empty-query-crash` |

**规则**：
- 禁止在 `main`、`master`、`develop` 分支上直接提交。
- 分支名必须小写，用 `-` 连接，简洁描述任务。
- 每个分支只做一件事。

---

## 2. Issue 分类

提交 Issue 时必须标注以下四类之一：

| 分类 | 标签 | 判定标准 |
|------|------|----------|
| **局部 Bug** | `type:local-bug` | 仅影响单个模块内部逻辑，不改变对外接口，修复无需跨模块联动 |
| **设计变更** | `type:design-change` | 涉及模块划分、数据流、架构层面的调整，可能影响多个模块 |
| **公共接口 / 兼容影响** | `type:breaking` | 修改了公开 API、配置格式、数据存储结构等，对下游有破坏性影响 |
| **多 Issue 同根因** | `type:root-cause` | 多个 issue 由同一根因导致，本 issue 作为追踪锚点，标记关联 issue |

---

## 3. 测试要求

| 变更类型 | 最低测试要求 |
|----------|-------------|
| `bugfix/` | 必须包含一个复现该 bug 的 regression test |
| `feature/` | 必须覆盖核心 happy path + 至少一个异常路径 |
| `update/` | 原测试全部通过；如行为有变更，需同步更新测试 |
| `docs/` | 无需测试 |

---

## 4. Spec 对账规则

### 生命周期

```
governance → planned → implemented → archived
```

### 对账时机

每次 PR 合并前，必须执行以下对账检查：

- [ ] 本次变更是否对应一条 `planned` spec？若无，是否应该补？
- [ ] 若对应 `planned` spec，验收标准是否全部通过？
- [ ] 是否有公共接口变更？若有，是否已在相关 spec 中记录兼容影响？
- [ ] 实现锚点是否准确指向实际代码路径？
- [ ] PR 描述中是否引用了对应的 spec 文件路径？

### 状态流转条件

- `planned → implemented`：验收标准全部通过，代码已合并
- `planned → archived`：评审后决定不实现
- `implemented → archived`：被新版本替代或废弃

---

## 5. 完成定义 (Definition of Done)

一个任务视为"完成"的充要条件：

1. **代码**：变更在对应 feature/update/docs/bugfix 分支上完成
2. **测试**：满足上方测试要求，且 CI 通过
3. **Spec 对账**：PR 描述中通过 spec 对账清单
4. **文档**：如有公共接口变更，相关 spec 已更新
5. **评审**：至少一人 Review 通过
6. **合并**：仅在明确获得"可以提交"指令后合入 main/master/develop

---

## 6. PR 合并前 Spec 对账清单

```
□ 1. 是否有对应的 planned spec？标识：__________
□ 2. 验收标准是否全部满足？ □ 是 □ 否（说明：__________）
□ 3. 公共接口是否变更？    □ 是 □ 否
    若"是"，兼容影响是否已在 spec 中记录？ □ 是 □ 否
□ 4. 实现锚点是否准确？    □ 是 □ 否
□ 5. PR 描述是否包含 spec 链接？ □ 是 □ 否
□ 6. 测试是否按规范覆盖？  □ 是 □ 否
□ 7. 分支命名是否符合规范？ □ 是 □ 否
□ 8. 是否有破坏性变更未标记 breaking？ □ 是（需阻塞） □ 否
```

---

## 7. 提交规范

- **禁止**在未获得明确"可以提交"指令前推送到远程仓库。
- 提交信息格式：`{type}: {简短描述}`
  - 示例：`feature: add hybrid search module`
  - 示例：`bugfix: handle empty query in retriever`
