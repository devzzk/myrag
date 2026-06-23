# 项目行为规范 Spec

> 状态：**governance** | 创建日期：2026-06-10

## 契约

本项目（myrag - RAG 知识库）遵循以下开发治理规则：

1. **版本管理**：使用 Git 进行版本控制。
2. **分支保护**：禁止在 `main` / `master` / `develop` 分支上直接提交。所有变更必须在功能分支上进行。
3. **分支命名**：分支必须采用以下前缀之一 + 具体任务名：
   - `feature/` — 新功能开发
   - `update/` — 功能增强或优化
   - `docs/` — 文档变更
   - `bugfix/` — Bug 修复
4. **提交控制**：所有更新仅在明确获得"可以提交"指令后，方可推送到远程仓库。
5. **Spec 管理**：项目以 spec 驱动，spec 文档存放于 `spec/` 目录，按四种状态（governance / planned / implemented / archived）组织。
6. **AGENTS.md** 作为 AI Agent 与开发者协作的入口文件，定义 issue 分类、分支命名、测试要求、spec 对账规则和完成定义。

## 验收标准

- [x] `.gitignore` 已创建并包含 Python / IDE / OS 常见忽略项
- [x] `spec/` 目录结构已建立（governance / planned / implemented / archived）
- [x] `spec/README.md` 已创建并说明四种状态
- [x] `AGENTS.md` 已创建并包含完整的治理规则
- [x] 本项目行为 spec 已归档至 `spec/governance/`

## 实现锚点

| 锚点 | 位置 |
|------|------|
| .gitignore | `.gitignore` |
| Spec 目录 | `spec/` |
| Spec 治理说明 | `spec/README.md` |
| Agent 协作规范 | `AGENTS.md` |
| 行为契约 | `spec/governance/20260610-project-behavior-spec.md` |

## 兼容影响

- 无破坏性变更。本次为项目初始化，所有文件为新建。
