---
name: mod-gen
cc_switch_update_marker: 2026-08-06-b
description: >
  网易 Minecraft MOD 脚手架生成器：通过模板克隆生成行为包+资源包+脚本框架。
  当用户提到生成 MOD、创建模组、脚手架、模板、custom_warehouse、占位符替换、
  一键生成 等关键词时触发。覆盖目录结构、占位符规则、贴图路径规范、Python 2.7 注释规范。
---

# MOD 脚手架生成器规范

本工作区是一个**网易 Minecraft MOD 脚手架生成器**。运行 `一键生成完整MOD.py`，输入模组名，从 `custom_warehouses/` 模板克隆出完整的行为包 + 资源包 + 脚本框架。

**运行环境**：模组脚本运行于 **Python 2.7**，生成脚本本身运行于 Python 3.10+。

---

## 目录结构

```
自动创建Minecraft模组完整版/
├── 一键生成完整MOD.py              # 生成脚本（核心入口）
├── miao_lid.py                     # 通用工具库
└── custom_warehouses/              # 模板目录（复数，不参与替换）
    ├── custom_warehouseB/          # 行为包模板
    │   ├── manifest.json
    │   ├── entities/
    │   ├── netease_items_beh/
    │   └── custom_warehouseScripts/
    │       ├── modMain.py
    │       ├── miao_Config.py              # C_Path / S_Path 路径配置
    │       ├── custom_warehouseClientSystem/
    │       └── custom_warehouseServerSystem/
    └── custom_warehouseR/          # 资源包模板
        ├── manifest.json
        ├── textures/ui/custom_warehouse/
        └── ui/
            ├── _global_variables.json
            ├── _ui_defs.json
            ├── ModName_common.json
            └── ModName_screen.json
```

---

## 占位符替换规则

| 占位符 | 含义 | 替换目标 |
|--------|------|---------|
| `custom_warehouse` | 模组主名（单数） | 文件内容 + 文件/目录名 |
| `custom_warehouse_common` | UI 公共命名空间 | 文件内容（必须**先于** `custom_warehouse` 替换） |
| `ModName` | UI 文件名/类名占位符 | 文件内容 + 文件/目录名 |

**替换顺序（强制）**：`custom_warehouse_common` → `custom_warehouse` → `ModName`

> `custom_warehouses`（外层模板文件夹，复数）**不是**占位符，不参与替换。

---

## UI 贴图路径规范

```json
// ✅ 正确
"texture": "($Miao_ModUiTexturesPath + '/文件名')"

// ❌ 错误 — 生成后路径不会跟随模组名变化
"texture": "textures/ui/custom_warehouse/文件名"
```

---

## Python 2.7 类型注释

```python
# 实例变量 — 写在赋值语句的紧下一行
self.AnyEvent = AE.AnyEvent(self)
""":type: custom_warehouseScripts.custom_warehouseServerSystem.AnyEvent.AnyEvent"""

# getattr 返回值
__PopupClass__ = getattr(uinode, '__PopupClass__', None)
""":type: custom_warehouseScripts.custom_warehouseClientSystem.utils.Popup | None"""
```

---

## 模板变更检查清单

1. **占位符一致性**：新增文件/目录名包含 `custom_warehouse` 或 `ModName`；模块路径用 `custom_warehouseScripts.` 前缀；`miao_Config.py` 路径与目录一致
2. **UI 贴图路径**：JSON 中用 `$Miao_ModUiTexturesPath` 变量；`_ui_defs.json` 列入新文件
3. **生成脚本**：`TEMPLATE_TOKEN` 为 `"custom_warehouse"`；替换顺序正确；`TEXT_EXTS` 覆盖新增类型
4. **类型注释**：新增 `self.xxx = 外部对象` 加 `:type:` 注释
5. **已生成模组**：生成脚本只处理新建，同步已有模组需手动对比

---

## 常见错误

| 现象 | 根因 | 修复 |
|------|------|------|
| 路径仍含 `custom_warehouse` | 替换用了复数 | 改用单数 `TEMPLATE_TOKEN` |
| UI 贴图路径不变 | JSON 硬编码路径 | 改为 `"($Miao_ModUiTexturesPath + '/xxx')"` |
| UI JSON 报错 | 路径格式缺引号 | 确认格式正确 |
| IDE 无法跳转 | 缺 `:type:` 注释 | 补完整模块路径注释 |
| Python 语法错误 | 用了 Python 3 语法 | 改写为 Python 2.7 兼容 |
