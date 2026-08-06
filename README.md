# my-skills

本仓库用于集中管理个人 skill，供 CC Switch 通过 GitHub 仓库来源统一安装和更新。

## 目录结构

```text
my-skills/
└── skills/
    ├── dev/
    ├── game-screenshot/
    ├── git-check/
    ├── jsonui/
    ├── mcdk-game/
    ├── mod-gen/
    ├── modui/
    └── release-notes/
```

每个技能一个文件夹，内部包含 `SKILL.md` 以及可能需要的 `references/` 等附属文件。

## 在 CC Switch 中添加本仓库

1. 打开 CC Switch 的 Skills 页面。
2. 点击「仓库管理」→「添加仓库」。
3. 填写：
   - Owner: `DaGuoNeko`
   - Name: `my-skills`
   - Branch: `main`
   - Subdirectory: `skills`
4. 保存后刷新技能列表，即可安装和更新。

## 更新流程

1. 修改 `skills/` 下对应技能的文件。
2. 提交并推送到 GitHub。
3. 在 CC Switch 中点击「刷新」，再对技能执行「更新」。
