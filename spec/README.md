# Spec 治理目录

本目录下的所有 spec 文档按以下四种状态管理：

| 状态目录 | 含义 |
|----------|------|
| `governance/` | 规则、流程、模板类 spec（如分支命名规范、PR 流程、对账清单） |
| `planned/`   | 已评审通过但尚未实现的 spec |
| `implemented/` | 已完成实现且通过验收的 spec |
| `archived/`  | 已废弃或被替代的 spec |

## 生命周期

```
planned -> implemented -> archived
                ^            |
                |            v
              (迭代)      (不再使用)
```

## 文件命名规范

```
{YYYYMMDD}-{短标题}.md
```

示例：`20260101-branch-naming-convention.md`

## Spec 模板字段

每份 spec 必须包含以下字段：

- **状态**：planned / implemented / archived
- **契约**：该 spec 承诺的行为、接口或约束
- **验收标准**：如何验证该 spec 已正确实现
- **实现锚点**：关键代码路径或模块引用
- **兼容影响**：对已有系统的破坏性变更说明
