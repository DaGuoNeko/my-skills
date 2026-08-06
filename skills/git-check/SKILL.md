---
name: git-check
description: >
  检查当前项目是否为 Git 仓库，若非仓库则询问用户是否初始化。
  配合 dev 工作流使用，会话启动时自动执行，也可随时手动调用 /git-check。
---

# Git 仓库检查

你是 AI 编程助手。本规则配合 [dev 工作流]($dev) 使用。

## 执行时机

- 会话启动时自动注入执行
- 用户随时可通过 `/git-check` 手动触发

## 规则

**被触发时，在输出任何其他内容之前，按顺序执行：**

### 步骤 1：检测 Git 仓库

立即运行以下命令：

```bash
cd "<当前工作目录>" && git status 2>&1
```

### 步骤 2：根据结果行动

| 结果 | 行动 |
|------|------|
| 是 Git 仓库 | 告知："✅ Git 仓库已就绪" |
| 不是 Git 仓库 | 询问用户："当前项目没有 Git 仓库，是否需要我帮你创建并初始化？" |

### 步骤 3：初始化仓库

用户同意后，严格按顺序执行：

**3.1** 运行 `git init`

**3.2** 创建 `.gitignore` 文件，写入以下内容：

```
# MC Studio 本地开发环境配置
.mcdev.json

# 其他
.zcode/
.mcs/
.miao/
studio
/st


# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual env
venv/
.env/

# IDE
.vscode/
.idea/
.kilocode/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
studio.json
```

**3.3** 告知用户初始化完成。

### 禁止

- ❌ 未经用户确认自动创建 Git 仓库
