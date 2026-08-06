---
name: jsonui
description: >
  Minecraft 基岩版 JsonUI 开发：UI 界面编写、数据绑定、控件使用、布局、动画。
  当用户提到 UI、界面、JsonUI、面板、按钮、数据绑定、ViewBinder、_ui_defs、grid、
  stack_panel、toggle、scroll_view、动画、贴图路径 等关键词时触发。
  网易中国版规范 + 公共组件库 + 实战陷阱全覆盖。
---

# JsonUI 开发技能

## 加载策略

- 本文件（SKILL.md）：快速索引，始终在触发时加载
- `references/guide.md`：完整开发手册（~1900 行），遇到以下情况时读取：
  - 需要具体控件属性/写法（如 button、slider、toggle、grid）
  - 需要数据绑定详细语法（ViewBinder、collection、binding_type）
  - 需要动画系统用法
  - 需要公共组件库（ModName_common）用法
  - 遇到 UI 报错需要排查

---

## 核心概念速查

| 符号 | 名称 | 生效时机 | 用途 |
|------|------|---------|------|
| `$` | 变量 | JSON 加载时（静态） | 值替换、配置传递 |
| `#` | 绑定 | 运行时（动态） | 动态数据显示（Python 驱动） |
| `@` | 继承 | JSON 加载时 | 组件复用 |

---

## 文件结构

```
资源包/ui/
├── _ui_defs.json          # 注册所有 UI 文件
├── _global_variables.json # 全局变量（贴图路径等）
├── xxx_common.json        # 公共组件库
└── xxx_screen.json        # 具体屏幕
```

---

## 控件类型速查

| 控件 | type | 用途 |
|------|------|------|
| 面板 | `panel` | 容器/布局 |
| 文字 | `label` | 显示文本 |
| 图片 | `image` | 贴图/背景 |
| 按钮 | `button` | 可点击交互 |
| 堆叠 | `stack_panel` | 自动排列 |
| 网格 | `grid` | 规则排列 |
| 滚动 | `scroll_view` | 超出滚动 |
| 输入框 | `edit_box` | 文本输入 |
| 滑动条 | `slider` | 数值选择 |
| 开关 | `toggle` | 选中切换 |
| 自定义 | `custom` | 物品渲染器等 |

---

## 布局速查

- **锚点居中**：`anchor_from: center, anchor_to: center`
- **尺寸单位**：`"100%"` 百分比 / `"100%c"` 子元素撑开 / `"fill"` 填充剩余 / `"100%+-20px"` 混合
- **偏移**：`offset: [X, Y]`（正值右/下）

---

## 变量 vs 绑定

| | 变量（$） | 绑定（#） |
|------|---------|---------|
| 时机 | JSON 加载时 | 运行时 |
| 可变 | 否 | 是（实时更新） |
| 来源 | JSON 配置 | Python ViewBinder |

---

## 一句话记住

- 创建 UI 前先查 `ModName_common` 公共组件库有没有现成的
- 贴图路径用 `($Miao_ModUiTexturesPath + '/xxx')`，不硬编码
- Button 在 collection 内取 index 用 `args['#collection_index']`（带 `#`）
- Toggle 取 index 用 `args['index']`（不带 `#`），取状态用 `args['state']`
