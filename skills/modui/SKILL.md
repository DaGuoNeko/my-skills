---
name: modui
description: >
  modui — 网易 MC 基岩版 Mod UI 统一规范
---
# Skill: modui — 网易 MC 基岩版 Mod UI 统一规范

本技能提取自 `custom_warehouse` 和 `quest_engine` 的 UI 设计体系，用于布局和绑定约定。依赖 `DAGUOMIAO_API_MOD` 的项目先阅读 [前置接入技能](../daguomiao-api/SKILL.md) 及其 UI 参考，复用当前前置的公共能力。

## 规范优先级（强制）

在用户要求和项目实际接口契约内，按以下分工取用规范：

1. **本技能（modui）**：结构、布局、视觉风格与命名约定；公共组件参数核对实际源码
2. **`jsonui` 技能**：本技能未覆盖的纯语法问题（如 `$` / `#` / `@` 符号机制、控件 type 含义）可参考 `jsonui` 技能
3. **ModSDK MCP 文档**：本技能未列出的 SDK API 签名，调 `search_api` / `get_api_detail` 查询
4. **其他来源**（官方文档、社区示例、旧项目代码）：仅当以上 3 级均未覆盖时参考，且不得与本技能冲突

> 本技能覆盖不了的场景（如新增 SDK API、引擎版本差异），应主动查 MCP 文档补全，不以本技能为唯一限制。

> **冲突处理**：用户要求、项目实际加载的公共组件和 API 契约优先于这里的历史模板。以下业务模组自建公共库示例只用于解释实现；前置已有等价入口时直接复用。涉及引擎参数时核对实际版本，不因模板未列出就判定参数不受支持。

## 触发关键词

当用户提到 UI、界面、JsonUI、屏幕、控件、绑定、绑定设计、Modal、弹窗、列表、按钮、堆叠面板、滚动视图、网格、Toggle、EditBox、Slider、Toast、动画、ScreenNode、ViewBinder 等关键词时触发。与通用 `jsonui` 技能互补：`jsonui` 讲语法，本技能讲**设计风格与规范**。

---

## 一、加载策略

- **本文件**：规范索引 + 模板片段，始终在触发时加载
- **需要深入时**：
  - 查具体控件的 `$` 参数表 → 阅读目标 mod 的 `*_common.json` 源文件
  - 查 SDK 接口签名/参数 → 调用 MCP 工具 `search_api` / `get_api_detail`
  - 查最佳实践 → 调用 MCP `get_best_practices` category="ui"
- **禁止**：凭记忆猜 API 签名、猜组件参数名。先查源文件或 MCP，再落笔

---

## 二、核心设计哲学（5 条铁律）

| # | 铁律 | 说明 |
|---|------|------|
| 1 | **绑定优先** | 一切可见/可变属性优先用 `#binding` 驱动（数据→UI），仅交互回调用事件绑定（UI→数据）。`GetBaseUIControl().SetText()` 等直接操作仅在无法用绑定表达时使用 |
| 2 | **公共库优先** | 先查已依赖前置及业务公共库，有现成组件或控制器则复用；缺失时按任务范围决定扩展共享库或实现业务控件 |
| 3 | **Modal 注册** | 按组件契约动态注入或绑定预置控件；前置部分注册方法支持 `dynamic_create=False`。动态绑定在 `Create()` 阶段完成 |
| 4 | **真实资源路径** | 查实际贴图和 namespace；允许引用已声明依赖的前置资源，避免复制整套公共贴图或猜路径 |
| 5 | **`common.base_screen` 默认 `is_showing_menu: true`** | `PushScreen` 打开的业务界面需要 `is_showing_menu: true`。网易 `common.base_screen` 已内置该默认值，因此 `main@common.base_screen` 只写 `$screen_content` 即可，无需显式覆盖。若继承自其他基类则需手动传 `$is_showing_menu: true` |

### Python 2.7 约束（全适用）

- 禁止 f-string、type hints、async/await
- 字符串格式化用 `.format()` 或 `%`
- 文件顶部写 `# -*- coding: utf-8 -*-`
- 可用 `print` 语句或 `from __future__ import print_function`
- 禁止函数内 import；import 放文件顶部
- 用 `:type:` 注释字符串提供 IDE 类型提示：
  ```python
  self.cs = param["cs"]
  """:type: clientApi.GetClientSystemCls()"""
  ```

---

## 三、文件结构

```
资源包/ui/
├── _ui_defs.json              # 注册所有 UI 文件（除 _global_variables / _ui_defs 本身）
├── _global_variables.json     # 全局变量（贴图根路径等）；可选但推荐
├── <modname>_common.json      # 唯一公共组件库，namespace = <modname>_common
├── <modname>_<feature>_screen.json  # 每个屏幕一个文件
└── <modname>_anims.json        # 独立动画库（大型项目可选；小型项目直接内嵌 common）
```

### `_ui_defs.json`

```json
{
  "ui_defs": [
    "ui/<modname>_common.json",
    "ui/<modname>_anims.json",
    "ui/<modname>_<feature>_screen.json"
  ]
}
```

- 必须 `{"ui_defs": [...]}` 对象格式，不能是纯数组
- 必须放 `resource_pack/ui/` 目录，不是根目录
- 先列 common/anims，后列 screen 文件
- `_global_variables.json` 不在此注册（引擎自动加载）

### `_global_variables.json`

```json
{
  "$<ModName>_UiTexturesPath": "textures/ui/<modname>"
}
```

- **推荐变量**：贴图根路径（几乎所有项目必备）
- 可按需追加更多全局变量（如公共颜色、字体比例等），无数量限制
- 公共库中引用：`"texture": "($<ModName>_UiTexturesPath + '/<name>')"`
- Screen JSON 中可直接用字面路径 `textures/ui/<modname>/<name>`

### 命名约定汇总

| 对象 | 约定 | 示例 |
|------|------|------|
| 文件名 | `<modname>_<feature>_screen.json` | `quest_engine_setting_screen.json` |
| namespace | = 文件名去 `.json` 和 `_screen`，admin 屏幕用 ` quest_engineUI` 等特殊名 | `quest_setting_screen` / `quest_engine_common` |
| 公共组件 | `M_` 前缀（大写） | `M_scroll_view` / `M_Popup` / `M_Tips_Panel` |
| 原子组件 | 小写 | `text` / `button_label` / `button_icon` |
| JSON 控件内重复子控件 | `(0)` `(1)` 后缀消除歧义 | `newbutt2(0)` / `panel(0)` / `text(0)(0)` |
| 贴图族 | `set_btn_a_1`(亮默认) / `set_btn_a`(亮按下) / `set_btn_b`(暗默认) / `set_btn_b_1`(暗按下) | 9宫格 `nineslice_size: [1,1,1,1]` |
| 关闭按钮 | `xxx_a`(默认/hover) / `xxx_b`(按下) | 正方形、无文字、贴边 1px |
| 遮罩图 | `hei`(黑色半透明) / `bai`(白色半透明) | alpha 0.5, size 300% |
| 滚动条透明 | `toum` |

---

## 四、Screen 三键约定

每个 screen JSON 文件**必须**包含三个顶层键：

```json
{
  "namespace": "<screen_namespace>",
  "main@common.base_screen": {
    "$screen_content": "<screen_namespace>.<root_panel_name>"
  },
  "<root_panel_name>": {
    "type": "panel", "layer": 1, "controls": [ ... ]
  }
}
```

| 键 | 说明 |
|----|------|
| `namespace` | 本文件的命名空间，用于跨文件引用 `@<namespace>.<control>` |
| `main@common.base_screen` | 注册入口，`$screen_content` 指回本文件的根 panel（格式 `namespace.rootName`） |
| 根 panel | `type: "panel"`, `layer: 1`，承载所有子控件 |

- Python 注册时使用 `"<namespace>.main"` 作为 `uiScreenDef`
- HUD 屏幕用 `clientApi.CreateUI(..., {"isHud": 1})` 创建（**JSON 结构不变**，仍遵循三键约定 `namespace` + `main@common.base_screen` + 根 panel，仅在 Python 创建方式上有别于 PushScreen）
- 业务屏幕用 `clientApi.PushScreen(...)` 打开
- 完整展开的 screen JSON 骨架见 **§10.1**

### 典型布局嵌套

```
根 panel (layer 1)
├── image 遮罩 (hei/bai, alpha 0.5, size 300%)  ← 背景暗化
├── stack_panel 主体 (vertical)
│   ├── panel 顶部栏 (标题 text + 关闭 newbutt2)
│   ├── M_Scroll_View_Grid_Panel ← 滚动列表
│   └── panel 底部栏 (按钮区)
├── input_panel 弹窗A (visible: false, modal: true, layer 1000+)
└── input_panel 弹窗B (visible: false, modal: true, layer 1000+)
```

### 布局尺寸选择指南

**这不是可选项——新建 screen 时必须根据内容类型选择布局尺寸。** 上方嵌套图中的 `stack_panel 主体` 有三种尺寸模式：

| 模式 | 尺寸 | 定位 | 遮罩 | 适用场景 |
|------|------|------|------|---------|
| **全屏** | `["100%+0px", "100%+0px"]` | 自然填满（不设 anchor_from/anchor_to） | 可选保留 `hei` 遮罩 | 数据密集界面：**列表/表格/网格、设置面板、跨存档管理、物品浏览器** |
| **弹窗** | `["80%+0px", "60%+0px"]`（长约 60%~80%） | `anchor_from: center, anchor_to: center` | **必须**保留 `hei` 遮罩 | 轻量交互：确认框、信息卡片、简单表单、单项选择 |
| **固定尺寸** | `[W, H]`（如 `[427, 453]`） | `anchor_from: center, anchor_to: center` | **必须**保留 `hei` 遮罩 | 内容尺寸已知且不依赖列表/滚动的紧凑工具界面 |

**决策优先级**（从上到下匹配，命中了就用）：

```
1. 界面核心是「列表/网格/表格」展示数据？
   └─ 是 → 全屏（内容多，需要最大空间）

2. 界面只是「确认/输入/提示」等单一任务？
   └─ 是 → 弹窗（短平快，居中聚焦注意力）

3. 界面内容固定且紧凑（如计算器、颜色选择器）？
   └─ 是 → 固定尺寸（内容不会溢出，不用滚动）

4. 不确定？→ 默认全屏（全屏错了只是浪费一点空间，弹窗错了会挤压内容）
```

**常见错误**：
- ❌ 列表界面用弹窗尺寸 → 内容被挤压，滚动区太小，用户体验差
- ❌ 全屏界面加 `anchor_from: center` → 全屏布局不需要居中，自然填满 safezone 即可
- ❌ 弹窗不加遮罩 `hei` → 背景穿透干扰，用户不知道是模态弹窗

**HUD 特殊说明**：HUD 由 `CreateUI(isHud:1)` 创建，不参与上述模式。HUD 的尺寸由业务决定（常为角落小面板或全宽横幅），且**不设遮罩**（HUD 不能阻挡游戏）。

---

## 五、公共组件库规范

namespace 固定为 `<modname>_common`。所有 `M_` 组件用 `$` 变量参数化，便于各 screen 注入不同的绑定名。

### 5.1 按钮 `newbutt2`

继承 `@common.button`，是主力按钮。完整 `$` 参数：

**贴图类**

| 参数 | 默认 | 说明 |
|------|------|------|
| `$default_texture` | `set_btn_a_1` | 默认态贴图 |
| `$hover_texture` | `set_btn_a_1` | 悬停态贴图 |
| `$pressed_texture` | `top_bg` | 按下态贴图 |
| `$is_new_nine_slice` | — | 新版九宫格开关 |
| `$nineslice_size` | `[1,1,1,1]` | 九宫格切片（上/左/下/右） |
| `$nine_slice_top` | — | 九宫格上边距 |
| `$nine_slice_buttom` | — | 九宫格下边距（注意拼写 buttom） |
| `$nine_slice_left` | — | 九宫格左边距 |
| `$nine_slice_right` | — | 九宫格右边距 |
| `$texture_layer` | — | 贴图层级 |

**颜色/透明度类**

| 参数 | 默认 | 说明 |
|------|------|------|
| `$button_img_color` | `[1, 1, 1]` | 按钮背景着色 RGB |
| `$control_alpha` | — | 控件整体透明度 |

**文字类**

| 参数 | 默认 | 说明 |
|------|------|------|
| `$label_text` | `"None"` | 按钮文字 |
| `$label_color` | `[1, 1, 1]` | 文字颜色 |
| `$label_font_size` | `"normal"` | 字号 |
| `$label_font_type` | `"smooth"` | 字体 |
| `$label_font_scale_factor` | — | 文字缩放因子 |
| `$label_alignment` | — | 文字对齐 |
| `$label_alp` | — | 文字透明度 |
| `$label_offset` | `[0, 0]` | 文字偏移 |
| `$label_layer` | — | 文字层级 |

**图标类**

| 参数 | 默认 | 说明 |
|------|------|------|
| `$icon_texture` | `""` | 图标贴图（空=纯文字按钮） |
| `$icon_size` | `[16, 16]` | 图标尺寸 |
| `$icon_offset` | `[0, 0]` | 图标偏移 |
| `$icon_anchor_from` | `left_middle` | 图标锚点 |
| `$icon_nineslice_size` | — | 图标九宫格切片 |
| `$icon_rot` | — | 图标旋转角度 |

**交互类**

| 参数 | 默认 | 说明 |
|------|------|------|
| `$pressed_button_name` | `"#xxx_btn"` | 点击事件绑定名（UI→Python），必须与 §六.2 `_btn` 后缀命名一致 |

实例（screen JSON 中）：

```json
{
  "close_btn(0)@<modname>_common.newbutt2": {
    "size": [80, 30],
    "anchor_from": "right_middle",
    "anchor_to": "right_middle",
    "offset": [-5, 0],
    "$label_text": "关闭",
    "$label_color": [0.1176, 0.1176, 0.1216],
    "$pressed_button_name": "#close_btn"
  }
}
```

### 5.1.1 UI 标准色

`$button_img_color`、`color`、`$xxx_color` 等所有颜色属性统一使用以下 6 色，**不自行发挥**。适用于按钮、标题栏背景、面板着色等任何需要色彩的场景。

| # | 名称 | 色值（0~1） | 搭配文字色 | 用途 |
|---|------|------------|-----------|------|
| 1 | **白色** | `[1, 1, 1]` | `[0, 0, 0]` | 普通按钮、默认背景 |
| 2 | **绿色** | `[0.2353, 0.5216, 0.1529]` | `[0, 0, 0]` | 确认按钮、标题栏背景 |
| 3 | **红色** | `[0.7922, 0.2118, 0.2118]` | `[1, 1, 1]` | 高危操作（删除、重置等） |
| 4 | **紫色** | `[0.4510, 0.2706, 0.8980]` | `[1, 1, 1]` | 操作性按钮（选择、打开等） |
| 5 | **金色** | `[1, 0.9098, 0.4]` | `[1, 1, 1]` | 显著操作按钮 |
| 6 | **蓝色** | `[0.1804, 0.4196, 0.8980]` | `[1, 1, 1]` | 随意使用 |

> **⚠️ 色值范围**：ModSDK JSON UI 中的 `color` 属性使用 **0.0~1.0** 浮点范围（RGB 各通道除以 255）。**不要混入** 0~255 整数范围的颜色值（如 `[255, 255, 255]`），否则会导致颜色过曝/全白。SDK 部分 API（如 `SetTextColor`）可能使用不同范围，以 MCP 文档为准。

实例——绿色标题栏背景、红色删除按钮：
```json
// 标题栏背景用绿色
"title_bg(0)": {
  "type": "image",
  "texture": "textures/ui/<modname>/set_btn_a_1",
  "color": [0.2353, 0.5216, 0.1529]
}

// 删除按钮用红色
"delete_btn(0)@<myns>_common.newbutt2": {
  "$button_img_color": [0.7922, 0.2118, 0.2118],
  "$label_color": [1, 1, 1]
}
```

### 5.2 Toggle `M_toggle`

继承 `@common_toggles.switch_toggle_collection`。**`M_toggle` 是唯一推荐的 Toggle 控件**，grid 内外均使用它，不要换成 `collection_M_toggle`。

| 参数 | 默认 | 说明 |
|------|------|------|
| `$toggle_name` | - | 交互绑定名（UI->Python, `BF_ToggleChanged`） |
| `$toggle_state_binding_name` | - | 状态绑定名（Python->UI, `BF_BindBool` 指示开/关） |
| `$toggle_text` | - | 标签文本 |
| `$M_toggle_checked_img` | `bai` | 选中态背景 |
| `$M_toggle_unchecked_img` | `030303` | 未选中态背景 |
| `$M_toggle_nineslice` | `[3,3,3,3]` | 九宫格 |
| `$toggle_binding_type` | - | grid 行内使用时设为 `"collection"` |
| `$toggle_grid_collection_name` | - | grid 行内使用时设为 collection 名 |

> **grid 行内 Toggle**：`M_toggle` 传入 `$toggle_binding_type: "collection"` + `$toggle_grid_collection_name: "xxx"` 即可在 grid/collection 内逐行渲染，无需改用 `collection_M_toggle`。
>
> **`BF_ToggleChanged` 回调参数**：`args = {'index': int, 'state': bool}`，其中 `index` 为 collection 中的行索引，`state` 为开关状态。


### 5.3 滚动列表 `M_Scroll_View_Grid_Panel`

封装 `M_scroll_view`（`@common.scrolling_panel`）+ `_Grid` / `_Stack_Grid`。核心参数：

| 参数 | 说明 |
|------|------|
| `$Grid_Collection_Name` | grid 的 `collection_name` |
| `$Grid_Count` | grid 行数 binding 名（`#xxx_count`） |
| `$Grid_Item_Template` | 行模板控件路径 `<namespace>.<row_name>` |
| `$Grid_Items_Maximum` | 最大行数（默认 5） |
| `$Grid_Binding_Condition` | 绑定条件（默认 `always_when_visible`） |
| `$Grid_Rescaling_Type` | `"horizontal"` |
| `$is_stack_grid` | `false`=grid, `true`=stack_grid |
| `$Stack_Grid_Orientation` | `"vertical"` |

实例：

```json
{
  "wh_list(0)@<modname>_common.M_Scroll_View_Grid_Panel": {
    "$Grid_Collection_Name": "wh_list",
    "$Grid_Count": "#wh_list_count",
    "$Grid_Item_Template": "<screen_ns>.wh_item",
    "$Grid_Items_Maximum": 5,
    "$Grid_Binding_Condition": "none"
  }
}
```

行模板定义在**同一 screen 文件**的顶层：

```json
{
  "wh_item": {
    "type": "panel",
    "size": ["100%", 30],
    "controls": [
      { "text(0)@<modname>_common.text": {
          "text": "#wh_item_name",
          "bindings": [
            {"binding_name": "#wh_item_name", "binding_type": "collection", "binding_collection_name": "wh_list"}
          ]
      }}
    ]
  }
}
```

#### 5.3.1 行列表 vs 卡片方格

`M_Scroll_View_Grid_Panel` 有两种显示模式，根据内容密度选择：

| 模式 | 行模板尺寸 | `$Grid_Binding_Condition` | 效果 |
|------|-----------|--------------------------|------|
| **行列表** | `["100%+0px", "26px"]`（横向长条） | `"none"` | 每行撑满宽度，适合文本为主的列表 |
| **卡片方格** | `["56px", "56px"]`（固定方形） | `"always_when_visible"` | 固定尺寸卡片，列数动态自适应，适合头像/物品格 |

**卡片方格模板**：

```json
{
  "card_list(0)@<myns>_common.M_Scroll_View_Grid_Panel": {
    "$Grid_Collection_Name": "card_list",
    "$Grid_Count": "#card_list_count",
    "$Grid_Item_Template": "my_screen.card_item",
    "$Grid_Items_Maximum": 20,
    "$Grid_Binding_Condition": "always_when_visible"
  }
}
```

```json
"card_item": {
  "type": "panel",
  "size": ["56px", "56px"],
  "controls": [
    {
      "bg": {
        "type": "image",
        "texture": "textures/ui/<modname>/set_btn_b_1",
        "nineslice_size": [2, 2, 2, 2],
        "alpha": 0.5,
        "size": ["100%+-2px", "100%+-2px"],
        "anchor_from": "center",
        "anchor_to": "center"
      }
    },
    {
      "label@<myns>_common.text": {
        "text": "#card_name",
        "anchor_from": "center",
        "anchor_to": "center",
        "font_scale_factor": 0.75,
        "bindings": [
          {"binding_name": "#card_name", "binding_type": "collection", "binding_collection_name": "card_list"}
        ]
      }
    },
    {
      "close_btn@<myns>_common.newbutt2": {
        "size": ["12px", "12px"],
        "anchor_from": "top_right",
        "anchor_to": "top_right",
        "offset": ["-1px", "1px"],
        "$default_texture": "textures/ui/<modname>/xxx_a",
        "$hover_texture": "textures/ui/<modname>/xxx_a",
        "$pressed_texture": "textures/ui/<modname>/xxx_b",
        "$label_text": "",
        "$pressed_button_name": "#card_close_btn",
        "bindings": [
          {"binding_collection_name": "card_list", "binding_condition": "always_when_visible", "binding_type": "collection_details"}
        ]
      }
    }
  ]
}
```

> **卡片使用固定 px 尺寸**（如 56×56），**不要用 `100%`**（会撑满整列变得很宽）。`$Grid_Binding_Condition: "always_when_visible"` 让列数 = 数据条数，引擎自动计算每列宽度。

### 5.4 EditBox `M_edit_box`

继承 `@common.text_edit_box`。完整 `$` 参数：

**绑定类**

| 参数 | 说明 |
|------|------|
| `$text_box_name` | 交互绑定名（UI→Python `BF_EditChanged`，带 `#`） |
| `$text_edit_box_content_binding_name` | 内容绑定名（Python→UI `BF_BindString`，带 `#`） |

**文本/占位类**

| 参数 | 说明 |
|------|------|
| `$place_holder_text` | 占位提示文本 |
| `$place_holder_text_color` | 占位文本颜色 |
| `$text_box_text_color` | 输入文本颜色 |
| `$font_size` | 字号 |
| `$font_scale_factor` | 文字缩放因子 |

**贴图/背景类**

| 参数 | 说明 |
|------|------|
| `$text_background_default` | 默认态背景贴图 |
| `$text_background_hover` | 悬停态背景贴图 |
| `$edit_box_default_texture` | 默认态贴图 |
| `$edit_box_hover_texture` | 悬停态贴图 |
| `$nineslice_size` | 九宫格切片 |
| `$is_new_nine_slice` | 新版九宫格开关 |
| `$nine_slice_top` | 九宫格上边距 |
| `$nine_slice_buttom` | 九宫格下边距（注意拼写 buttom） |
| `$nine_slice_left` | 九宫格左边距 |
| `$nine_slice_right` | 九宫格右边距 |

**布局类**

| 参数 | 说明 |
|------|------|
| `$text_edit_box_label_anchor_point` | 文本锚点 |
| `$text_edit_box_label_size` | 文本尺寸 |
| `$text_edit_box_label_min_size` | 文本最小尺寸 |

> `$text_edit_box_max_length` 在公共库中未声明为 `$` 变量；如需限制输入长度，Python 侧用 `GetBaseUIControl(path).asTextEditBox().SetEditTextMaxLength(n)` 设置。

### 5.5 Slider `M_slider`

依赖 DAGUOMIAO_API_MOD 时，优先用 [公共 SliderControl](../daguomiao-api/references/slider.md) 注册独立 ID、业务范围与输入联动；仅修改 `$slider_name` 不会隔离数值和步数绑定。公共选轮和资源选择见 [选轮与资源目录](../daguomiao-api/references/selectors.md)。下表只解释底层模板参数。

继承 `@common.slider`。

| 参数 | 说明 |
|------|------|
| `$slider_name` | 交互绑定名（`BF_SliderChanged`/`BF_SliderFinished`） |
| `$slider_value_binding_name` | 当前值绑定名（`BF_BindInt`/`BF_BindFloat`） |
| `$slider_steps_binding_name` | 步数绑定名 |

### 5.6 ItemRenderer `M_item_renderer`

type `custom`，`renderer: inventory_item_renderer`。绑定名：

| 绑定 | 类型 | 说明 |
|------|------|------|
| `#item_id_aux` | Int | 物品 aux 值 |
| `#item_custom_color` | Color | 着色 |
| `#armor_trim_material` | String | 锻造模板材质 |

用 `property_bag` 预设默认值：
```json
"property_bag": {"#item_id_aux": 0, "#item_custom_color": -1, "#armor_trim_material": ""}
```

### 5.7 背景 `BG`

type `custom`，`renderer: background_renderer`，`layer: 1`。渲染游戏模糊背景。

### 5.8 内置 Modal 组件（共 5 种）

| 组件 | 作用 | layer | 关键 binding 前缀 |
|------|------|-------|-------------------|
| `M_Popup` | 确认/取消弹窗 | 1400 | `#POPUP_TITLE_NAME`, `#POPUP_TEXT_NAME`, `#POPUP_TEXT_QX_BTN`(取消), `#POPUP_TEXT_QR_BTN`(确认), `#POPUP_TEXT_BTN_QR_0_VISIBLE`, `#POPUP_TEXT_BTN_QR_1_VISIBLE` |
| `M_CountContPanel` | 数量选择器（键盘+滑条） | 1000 | `#count_cont_gn_btn`, `#slider_value`, `#slider_steps`, `#slider_state`, `#count_cont_sum_text`, `#count_conts_value_btn`, `#count_cont_clear_btn`, `#count_cont_mb_xx_btn` |
| `M_CUSBOX_PANEL` | 自定义下拉选择器 | 1000 | `#M_CUSBOX_PANEL_TITLE_TEXT`, `#M_CUSBOX_PANEL_XX_BTN`, `#M_CUSBOX_GRID_ITEM_COUNT`, `#M_CUSBOX_TOGGLE_NAME`, `#M_CUSBOX_TOGGLE_STATE`, `#M_CUSBOX_TOGGLE_ITEM_TEXT`, `#M_CUSBOX_TOGGLE_ITEM_ICON` |
| `M_Tips_Panel` | Toast 提示条 | 9999 | 无 binding，通过 `SetVisible + StopAnimation + PlayAnimation` 触发 |
| `M_ITEMS_TIPS_PANEL` | 物品悬浮提示 | 1888 | 同上动画驱动 |

---

## 六、数据绑定规范

### 6.1 绑定类型 4 类

| 类型 | 用途 | Python 装饰器 |
|------|------|--------------|
| `global` | 屏幕级单值绑定（标题/权限/总数等） | `@ViewBinder.binding(BF_BindString, '#name')` |
| `collection` | grid 行级逐行绑定（必带 `binding_collection_name`） | `@ViewBinder.binding_collection(BF_BindString, 'coll_name', '#name')` |
| `collection_details` | **grid 内按钮点击**：告知引擎该按钮属于某个 collection，点击时 `args` 携带 `#collection_index` 和 `button_scene_name`。**JSON 端必须加 `bindings` 数组**（否则按钮不响应），Python 端**必须用普通 `binding` 装饰器**（❌ 禁止用 `binding_collection`，否则回调收不到 index） | `@ViewBinder.binding(BF_ButtonClickUp, '#my_btn')`, index 从 `args['#collection_index']` 或 `args['button_scene_name']` 取 |
| `view` | 控件间派生绑定（source→target，表达式计算） | 无 Python 端，纯 JSON `property_bag` + expression |

### 6.2 绑定名命名后缀约定（强制）

> **后缀来源速记**（拼音首字母缩写）：
> - `jh` = 交互 (jiāohù) — UI→Python 事件
> - `nr` = 内容 (nèiróng) — Python→UI 数据回显  
> - `kg` = 开关 (kāiguān) — switch/toggle 状态
> - `xz` = 选择 (xuǎnzé) — 选择器入口
> - `qr` / `qx` = 确认 (quèrèn) / 取消 (qǔxiāo) — Modal 按钮

**核心 7 后缀**（新界面必用）：

| 后缀 | 含义 | Python 装饰器 | 示例 |
|------|------|--------------|------|
| `_jh` | 交互事件（UI→Python） | `BF_ButtonClickUp` / `BF_ToggleChanged` / `BF_EditChanged` | `#wh_sous_edit_jh` |
| `_nr` | 内容显示（Python→UI） | `BF_BindString` / `BF_BindInt` / `BF_BindBool` | `#wh_sous_edit_nr` |
| `_btn` | 按钮点击事件 | `BF_ButtonClickUp` | `#close_btn` |
| `_count` | grid/stack_grid 行数驱动 | `BF_BindInt` | `#wh_list_count` |
| `_state` | 布尔状态 | `BF_BindBool` | `#wh_mode_state` |
| `_visible` | 可见性 | `BF_BindBool` + `binding_name_override: "#visible"` | `#auto_toitems_btn_visible` |
| `_is_xxx` | 权限/条件 gate | `BF_BindBool` + `binding_name_override: "#visible"` | `#wh_is_op` |

**扩展后缀**（quest_engine 实战总结）：

| 后缀 | 含义 | 说明 |
|------|------|------|
| `_edit_jh` / `_edit_nr` | EditBox 双向绑定 | `_jh/_nr` 的编辑框专用变体，`_edit_jh` 用 `BF_EditChanged\|BF_EditFinished` |
| `_toggle_jh` / `_toggle_nr` | Toggle 双向绑定 | `_toggle_jh` 用 `ToggleFilter\|BF_ToggleChanged`；`_nr` 回读 `BF_BindBool` |
| `_kg_jh` / `_kg_nr` | 开关（switch）双向绑定 | 语义同 toggle，命名区分「开关型」toggle |
| `_qr_btn` / `_qx_btn` | 确认 / 取消按钮 | Modal 弹窗二选一按钮的固定命名，如 `#POPUP_TEXT_QR_BTN` |
| `_open_btn` | 打开子面板 | 触发 `SetVisible(True, False)` |
| `_copy_btn` | 复制到剪贴板 | `CF.CreateGame(LevelID).SetClipboardContent(...)` |
| `_get_btn` | 从游戏取值 | 如从剪贴板 / 玩家背包 / 选中区域取值 |
| `_help_btn` | 打开帮助面板 | |
| `_xz_btn` | 选择器入口 | 打开选择列表（选择物品/目标/位置等） |
| `_up_btn` / `_down_btn` | 列表项上移/下移 | 常用于配置项列表重排 |
| `_add_btn` / `_del_btn` | 列表新增/删除 | |
| `_next_btn` / `_prev_btn` | 分页 | quest_engine 用 `not_top_next_btn`（命名反直觉，**推荐 `_prev_btn`**） |
| `_visible_N` | 数字编号可见性 | `#item_panel_visible_0`, `#item_panel_visible_1`（多档尺寸切换） |
| `_state_N` | 数字编号状态 | radio 组多档状态 |
| `_texture` | 贴图路径绑定 | `BF_BindString` + `binding_name_override: "#texture"` |
| `_color` / `_bg_color` | 颜色绑定 | `BF_BindColor` 返回 `(r,g,b,a)` |
| `_alpha` | 透明度绑定 | `BF_BindFloat` |
| `_id_aux` / `_custom_color` / `_trim_material` / `_materialr` | 物品渲染 5 元组 | ItemRenderer 属性各绑一路（asItemRenderer 参数） |

全部小写 snake_case，前缀 `#`。

### 6.3 绑定写法模板

**文本绑定（Python→UI）**：
```json
{
  "text": "#wh_active_title_text",
  "bindings": [
    {"binding_name": "#wh_active_title_text", "binding_type": "global", "binding_condition": "none"}
  ]
}
```

**可见性绑定（bool→#visible）**：
```json
{
  "bindings": [
    {"binding_name": "#wh_is_op", "binding_name_override": "#visible", "binding_type": "global", "binding_condition": "none"}
  ]
}
```

**行级集合绑定**：
```json
{
  "text": "#wh_item_name",
  "bindings": [
    {"binding_name": "#wh_item_name", "binding_type": "collection", "binding_collection_name": "wh_list", "binding_condition": "none"}
  ]
}
```

**网格行数绑定**：
```json
{
  "bindings": [
    {"binding_name_override": "#maximum_grid_items", "binding_name": "#wh_list_count", "binding_condition": "none"}
  ]
}
```

**View 表达式绑定（控件间派生）**：
```json
{
  "bindings": [
    {
      "binding_type": "view",
      "source_property_name": "(not #texture_icon_path)",
      "target_property_name": "#visible"
    }
  ]
}
```
配合 `property_bag: {"#texture_icon_path": ""}` 预设初始值。

**颜色绑定**：
```json
{
  "bindings": [
    {"binding_name": "#toggle_bg_color", "binding_name_override": "#color", "binding_type": "global"}
  ]
}
```

**贴图动态切换**：
```json
{
  "bindings": [
    {"binding_name": "#img_pos_texture0", "binding_name_override": "#texture", "binding_type": "global"}
  ]
}
```

**grid/stack_grid 内按钮点击**（`collection_details`）：
```json
{
  "my_btn(0)@<myns>_common.newbutt2": {
    "$pressed_button_name": "#my_item_btn",
    "bindings": [
      {
        "binding_collection_name": "my_collection",
        "binding_condition": "always_when_visible",
        "binding_type": "collection_details"
      }
    ]
  }
}
```
Python 回调通过 `args.get('#collection_index')` 取索引；兜底从 `button_scene_name` 正则解析。完整示例见 **§10.2** 的 `row_select_btn`。

> **`collection_details` 是 grid/stack_grid 内按钮能点击的前提。** 不加这个 bindings，按钮点了不会触发任何事件。

### 6.4 EditBox 两路绑定

JSON 中：
```json
{
  "$text_box_name": "#wh_sous_edit_jh",
  "$text_edit_box_content_binding_name": "#wh_sous_edit_nr"
}
```

Python 中：`_jh` 用 `BF_EditChanged | BF_EditFinished` 接收用户输入；`_nr` 用 `BF_BindString` 回写显示。Python 侧保持单一数据源（如 `self.search_text`），双向同步。

#### EditBox 回调 args 键名（强制）

`BF_EditChanged` / `BF_EditFinished` 的回调 `args` 是一个 dict，**键名首字母大写**：

| 键 | 类型 | 说明 |
|----|------|------|
| `Text` | str | 当前输入框内容（**大写 T**，不是 `text`） |
| `Mode` | str | 触发模式：`'Changed'`（输入中每次按键）或 `'Finished'`（失焦/回车确认） |

**Mode 过滤约定**：大多数场景只想在输入完成时处理逻辑，用 `Mode == 'Finished'` 过滤。完整 Python 示例见 **§10.6**。

> **不写 Mode 过滤则每次按键都触发**——仅适用于需要实时搜索过滤等极少数场景。

---

## 七、Modal 动态注入模式

### 7.1 注入流程

Modal 组件不在 screen JSON 中声明，运行时从 `<modname>_common` 注入：

```python
def Create(self):
    # 1. 注入 Tips 面板
    self.mclienSystem.RegisterTipsPanel(self, self.base_paths)
    # 2. 注入 Popup 确认框
    self.mclienSystem.ResiPopup(self, self.base_paths)
    # 3. 注入数量选择器
    self.mclienSystem.RegisterContPanel(self, self.base_paths)
    # 4. 注入物品提示
    self.mclienSystem.RegisterItemsTipsPanel(self, self.base_paths)
```

> `RegisterTipsPanel`、`ResiPopup`、`RegisterContPanel`、`RegisterItemsTipsPanel` 不是 SDK 内置 API。`DAGUOMIAO_API_MOD` 已提供这些入口：依赖此前置时通过其 ClientSystem 实例调用，不需要在业务 ClientSystem 重写。下方 `_inject` 仅供不使用前置的自建公共库参考，不能假定业务系统自动拥有这些方法。

底层调用：

```python
def _inject(self, screen_node, base_paths, component_name):
    parent = screen_node.GetBaseUIControl(base_paths)
    uicontrol = screen_node.CreateChildControl(
        "<modname>_common.%s" % component_name,
        component_name,
        parent
    )
    return uicontrol
```

### 7.2 `CreateChildControl` 性能注意

- `forceUpdate` 默认 `True`（同帧刷新）
- 批量注入多个 Modal 时设 `forceUpdate=False`，最后统一调 `UpdateScreen()`
- 示例：
  ```python
  self.CreateChildControl(ns_name, name, parent, False)  # 不立即刷
  self.CreateChildControl(ns_name2, name2, parent, False)
  self.UpdateScreen()  # 统一刷新
  ```

### 7.3 动态绑定挂接

Modal 内的 binding 方法不能预定义为 ScreenNode 的 class 属性（因为注入时机不确定），用闭包动态挂接：

```python
import types

def CreateDynamicBind(uinode, fn):
    """将闭包 fn 绑定为 uinode 的方法"""
    bound = types.MethodType(fn, uinode)
    setattr(uinode, fn.__name__, bound)
```

> Popup 确认弹窗的完整使用示例见 **§10.3**。

### 7.4 遮罩标准写法

遮罩由 `input_panel` + `hei` 图片组成，完整 JSON 模板见 **§13.4**。关键规则：

- `modal: true` 拦截穿透
- **不要**设 `is_swallow: true`（会导致子控件无法点击）
- `visible: false` 初始隐藏，Python 侧 `SetVisible(True, False)` 打开
- 关闭用 `SetVisible(False, False)`；销毁本屏用 `clientApi.PopScreen()`（PushScreen 打开）或 `self.SetRemove()`（CreateUI 创建）
- 遮罩尺寸约定（按父容器语境二选一）：
  - **根 panel 下的遮罩**：`size: ["300%", "300%"]`（因为根 panel 可能被安全区裁切，300% 确保四边完全覆盖）
  - **input_panel 内的遮罩**：`size: ["100%+0px", "100%+0px"]`（因为 input_panel 本身已全屏，100% 即完全覆盖）
- `alpha: 0.5` 统一

---

## 八、Python ScreenNode 装配模式

### 8.1 基类骨架

> 完整带绑定的 ScreenNode 骨架见 **§10.2**，此处仅列核心结构。

```python
class MyScreen(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.mclienSystem = param["cs"]
        self.Playerid = clientApi.GetLocalPlayerId()
        self.base_paths = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
        self._ui_dirty = False

    def Create(self):
        self.mclienSystem.RegisterTipsPanel(self, self.base_paths)
        self.mclienSystem.ResiPopup(self, self.base_paths)

    def Init(self): pass

    def Update(self):
        if self._ui_dirty:
            self._ui_dirty = False
            self._refresh_screen()

    def Destroy(self): pass
```

**节流模式**：`_ui_dirty` 标记 + `Update()` 检查，多个状态变更合并为一次刷新。用 `_MarkUIUpdate()` 设标记。

### 8.2 ViewBinder 装饰器全表

| 装饰器 | 用途 | 示例 |
|--------|------|------|
| `BF_ButtonClickUp` | 按钮点击 | `@ViewBinder.binding(ViewBinder.BF_ButtonClickUp, '#close_btn')` |
| `BF_BindBool` | 布尔绑定（可见性/状态） | `@ViewBinder.binding(ViewBinder.BF_BindBool, '#wh_is_op')` |
| `BF_BindString` | 字符串绑定 | `@ViewBinder.binding(ViewBinder.BF_BindString, '#wh_title')` |
| `BF_BindInt` | 整数绑定 | `@ViewBinder.binding(ViewBinder.BF_BindInt, '#wh_list_count')` |
| `BF_BindFloat` | 浮点绑定 | `@ViewBinder.binding(ViewBinder.BF_BindFloat, '#slider_value')` |
| `BF_BindColor` | 颜色绑定 RGBA | `@ViewBinder.binding(ViewBinder.BF_BindColor, '#item_color')` |
| `BF_ToggleChanged \| ToggleFilter` | Toggle 变更 | `@ViewBinder.binding(ViewBinder.ToggleFilter \| ViewBinder.BF_ToggleChanged, '#mode_toggle_jh')` |
| `BF_EditChanged \| BF_EditFinished` | EditBox 变更 | `@ViewBinder.binding(ViewBinder.BF_EditChanged \| ViewBinder.BF_EditFinished, '#search_edit_jh')` |
| `BF_SliderChanged \| BF_SliderFinished` | Slider 变更 | `@ViewBinder.binding(ViewBinder.BF_SliderChanged \| ViewBinder.BF_SliderFinished, '#count_slider_jh')` |
| `binding_collection(flag, coll, '#name')` | 行级集合绑定 | `@ViewBinder.binding_collection(ViewBinder.BF_BindString, 'wh_list', '#wh_item_name')` |

集合绑定的回调签名：
```python
@ViewBinder.binding_collection(ViewBinder.BF_BindString, 'wh_list', '#wh_item_name')
def wh_item_name(self, index):
    """:type: int"""
    return self._data[index]['name']
```

### 8.3 ClientSystem 装配

**PushScreen 实例保存规范（强制）**：

- `__init__` 中为每个 screen 预置 `self.<screenDef> = None`
- `Open_xxx` 方法中 `self.<screenDef> = clientApi.PushScreen(...)` 保存返回的 ScreenNode 实例
- 再次打开时直接覆盖，不需要在 `Destroy()` 中手动清空
- 保存的实例可用于 ClientSystem → ScreenNode 反向调用（转发事件/推送数据）

```python
# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

ClientSystem = clientApi.GetClientSystemCls()
EngineNs = clientApi.GetEngineNamespace()       # 引擎命名空间
EngineSys = clientApi.GetEngineSystemName()     # 引擎系统名


class MyClientSystem(ClientSystem):
    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.BackFun = {}
        # 预置所有 screen 实例为 None
        self.my_screen = None
        self.sub_screen = None
        self.hud_node = None
        # 监听引擎 UI 初始化完成事件（必须用引擎命名空间，不是本 mod）
        self.ListenForEvent(EngineNs, EngineSys, 'UiInitFinished', self, self.InitUi)
        # 监听本 mod 服务端事件
        self.ListenForEvent('mod', 'modServerSystem', 'AnyEvent', self, self.OnServerEvent)

    def InitUi(self, args):
        # RegisterUI 必须在 UiInitFinished 回调中调用
        clientApi.RegisterUI('mod', 'my_screen',
            'modScripts.myClientSystem.MyScreen',      # ← §10.2 中定义的 ScreenNode 子类
            'my_screen.main')
        clientApi.RegisterUI('mod', 'sub_screen',
            'modScripts.myClientSystem.SubScreen',     # ← 另一份 ScreenNode 子类（此处省略）
            'sub_screen.main')
        clientApi.RegisterUI('mod', 'my_hud',
            'modScripts.myClientSystem.MyHud',         # ← HUD ScreenNode 子类
            'my_hud.main')
        # HUD 用 CreateUI 常驻（RegisterUI 必须先于 CreateUI）
        self.hud_node = clientApi.CreateUI('mod', 'my_hud', {'isHud': 1, 'cs': self})

    def OnServerEvent(self, args):
        """服务端事件回调分发（按 eventsuid 找回调）"""
        uid = args.get('eventsuid')
        cb = self.BackFun.pop(uid, None)
        if cb:
            cb(args)

    def OpenMyScreen(self):
        # 直接 PushScreen，保存返回的 ScreenNode 实例到成员变量
        self.my_screen = clientApi.PushScreen('mod', 'my_screen', {'cs': self})

    def OpenSubScreen(self, back=None):
        # 2级独立屏：传入 back 回调
        self.sub_screen = clientApi.PushScreen('mod', 'sub_screen', {'cs': self, 'back': back})

    def TS(self, data, callback, eventsuid=None):
        """统一客户端→服务端 RPC 通道"""
        data['eventsuid'] = eventsuid
        if eventsuid:
            self.BackFun[eventsuid] = callback
        self.NotifyToServer('AnyEvent', data)
```

**反向调用示例**（ClientSystem 通过保存的实例向已打开界面转发事件）：

```python
def OnServerPushData(self, args):
    # 通过保存的成员变量调用 ScreenNode 的方法
    screen = self.my_screen
    if screen and hasattr(screen, 'OnDataChanged'):
        screen.OnDataChanged(args)
```

### 8.4 关闭 UI

**核心原则：怎么打开，就怎么关闭。与层级深度无关，只与打开方式有关。**

```
0级  HUD（CreateUI 常驻，不关闭）
 │
1级  主界面 screen（PushScreen 打开）
 │   ├── 2级·同屏面板  input_panel（SetVisible 切换）
 │   │              └── 3级·公共弹层  M_Popup / M_CUSBOX / M_Tips（注入）
 │   └── 2级·独立屏  再 PushScreen 打开的另一个 .screen
```

| 层级 | 打开方式 | 关闭方式 |
|------|---------|---------|
| 0级 HUD | `CreateUI(isHud:1)` | 不关闭（常驻） |
| 1级 主界面 | `PushScreen(...)` | `clientApi.PopScreen()` |
| 2级·同屏面板 | `SetVisible(True, False)` | `SetVisible(False, False)` |
| 2级·独立屏 | `PushScreen(...)` | `clientApi.PopScreen()` |
| 3级·公共弹层 | `SetVisible(True, False)` + `PlayAnimation()` | `SetVisible(False, False)` |
| 3级·独立屏 | `PushScreen(...)` | `clientApi.PopScreen()` |

> **一句话规律：PushScreen 打开的 → `PopScreen()` 关；SetVisible 显示的 → `SetVisible(False, False)` 关。**

### 8.4.1 跨级关闭场景

**场景 1：2级面板还开着，直接关1级屏**
`PopScreen` 销毁整个 ScreenNode，引擎自动连带销毁子控件。无需先隐藏 2/3 级。

**场景 2：从 1级切换到另一个 1级屏**
先关 2级面板再 PopScreen，避免面板短暂残留：
```python
def switch_screen(self, args):
    self._HidePanel()
    clientApi.PopScreen()
    self.mclienSystem.OpenOtherScreen()
```

**场景 3：3级 M_Popup 确认后关 1级屏**
```python
def _on_popup_confirm(args):
    popup.SetVisible(False, False)
    clientApi.PopScreen()
```

**场景 4：关屏前有异步写操作**
把 `PopScreen` 放在回调最后一步：
```python
def close_btn(self, args):
    def on_flushed():
        clientApi.PopScreen()
    self.mclienSystem.FlushData(callback=on_flushed)
```

**场景 5：2级独立屏回传数据给1级**
子屏自己 `PopScreen` 退出，通过 `back` 回调传值：
```python
def on_confirm(self, args):
    self.mclienSystem.back(self._selected)
    clientApi.PopScreen()
```

> `PopScreen` 弹出全局 UI 栈顶，实践中通过规范「仅用 PushScreen/PopScreen 管理 JsonUI」避免栈错乱。

---

## 九、动画规范

### 9.1 存储位置

- 小型项目：动画 `anim_type` 块直接内嵌在 `*_common.json` 中
- 大型项目：可拆出 `<modname>_anims.json`（独立 namespace），通过 `@<anim_ns>.<anim_id>` 引用

### 9.2 动画链式结构

```json
{
  "tips_anim_tm": {
    "anim_type": "alpha",
    "duration": 0.1,
    "from": 0,
    "to": 1,
    "easing": "out_bounce",
    "next": "@<modname>_common.tips_anim_tm_1"
  },
  "tips_anim_tm_1": {
    "anim_type": "alpha",
    "duration": 1.5,
    "from": 1,
    "to": 1,
    "next": "@<modname>_common.tips_anim_tm_3"
  },
  "tips_anim_tm_3": {
    "anim_type": "alpha",
    "duration": 0.3,
    "from": 1,
    "to": 0,
    "easing": "out_expo"
  }
}
```

### 9.3 三种引用方式

**方式 1 — 属性 inline 引用**（最常用）：
```json
{
  "alpha": "@<modname>_common.tips_anim_tm",
  "size": "@<modname>_common.tips_anim"
}
```

**方式 2 — `anims` 数组（顺序播放）**：
```json
{
  "anims": ["@<anim_ns>.bg_alpha_in", "@<anim_ns>.bg_pop"]
}
```

**方式 3 — Python 驱动**：
```python
uicontrol.StopAnimation()
uicontrol.PlayAnimation()
```

### 9.3.1 三种引用方式选择指南

| 方式 | 适用场景 | 限制 | 示例 |
|------|---------|------|------|
| **属性 inline 引用**（最常用） | 控件属性动画（alpha/size/offset），自动播放 | 只能挂在控件属性上 | `"alpha": "@xxx.anim"` |
| **`anims` 数组** | 入场/退场链式动画，顺序播放 | 不能单独控制某一段 | `"anims": ["@a.in", "@a.pop"]` |
| **Python 驱动** | 需运行时控制播放时机/条件/参数 | 不能引用 `@` 外部动画定义；动态注册的动画不支持变量解析 | `PlayAnimation("offset")` |

> **常见选错**：Toast 弹出 → 用方式1（`alpha: @...`）让动画随 visible 自动播；屏幕入场 → 用方式2（`anims` 数组）；按钮按下反馈 → 用方式3（Python 按需触发的 offset 动画）。

### 9.4 常用缓动函数

| 缓动 | 适用场景 |
|------|---------|
| `out_bounce` | 弹出动画（Toast/按钮 pop） |
| `out_expo` | 淡出动画 |
| `out_cubic` | 平滑过渡 |
| `out_quart` | 快速减速 |
| `in_quart` | 缓慢加速 |
| `in_sine` | 柔和入场 |
| `in_out_sine` | 双向柔和 |

### 9.5 无限循环动画

```json
{
  "attr_toum_0_amin": {
    "anim_type": "alpha",
    "duration": 1,
    "from": 1,
    "to": 0,
    "next": "@<modname>_common.attr_toum_1_amin"
  },
  "attr_toum_1_amin": {
    "anim_type": "alpha",
    "duration": 1,
    "from": 0,
    "to": 1,
    "next": "@<modname>_common.attr_toum_0_amin"
  }
}
```

### 9.6 动态注册动画约束

`RegisterUIAnimations(data)` 可在运行时代码注册动画，但：
- **不支持外部继承**（`@` 引用）
- **不支持变量解析**（`$` 变量）
- 仅用于运行时计算参数的场景，一般情况用 JSON 内嵌

---

## 十、可复用模板片段

以下片段可直接复制后修改 namespace `<myns>` 和 modname。

> **⚠️ 必须执行：使用模板前，先根据 §四「布局尺寸选择指南」决策树确定你的界面用全屏还是弹窗。**
> 
> 下方模板默认展示**弹窗模式**（`80%×60%` 居中 + 遮罩）。如果你的界面是列表/网格/表格类（数据密集），**必须改为全屏模式**：
> 1. `main_body` 尺寸改为 `["100%+0px", "100%+0px"]`
> 2. 删除 `main_body` 的 `anchor_from` / `anchor_to`（全屏布局不居中）
> 3. 遮罩 `hei` 可保留但非必须（全屏内容已占满，遮罩在根 panel 下用 300% 尺寸仍可保留）
> 
> **常见错误**：拿弹窗模板直接套到列表界面 → 内容被挤压、滚动区太小。

### 10.1 完整 Screen JSON 骨架

```json
{
  "namespace": "my_screen",

  "main@common.base_screen": {
    "$screen_content": "my_screen.root_panel"
  },

  "root_panel": {
    "type": "panel",
    "layer": 1,
    "controls": [
      {
        "bg_dim(0)": {
          "type": "image",
          "texture": "textures/ui/<modname>/hei",
          "alpha": 0.5,
          "size": ["300%", "300%"],
          "layer": 1
        }
      },
      {
        "main_body(0)": {
          "type": "stack_panel",
          "orientation": "vertical",
          "size": ["80%", "60%"],
          "anchor_from": "center",
          "anchor_to": "center",
          "controls": [
            {
              "top_bar(0)": {
                "type": "panel",
                "size": ["100%", 17],
                "controls": [
                  {
                    "title(0)@<myns>_common.text": {
                      "text": "#screen_title",
                      "anchor_from": "center",
                      "anchor_to": "center",
                      "color": [1, 1, 1],
                      "bindings": [
                        {"binding_name": "#screen_title", "binding_type": "global", "binding_condition": "none"}
                      ]
                    }
                  },
                  {
                    "close_btn(0)@<myns>_common.newbutt2": {
                      "size": [15, 15],
                      "anchor_from": "right_middle",
                      "anchor_to": "right_middle",
                      "offset": [-1, 0],
                      "$default_texture": "textures/ui/<modname>/xxx_a",
                      "$hover_texture": "textures/ui/<modname>/xxx_a",
                      "$pressed_texture": "textures/ui/<modname>/xxx_b",
                      "$label_text": "",
                      "$pressed_button_name": "#close_btn"
                    }
                  }
                ]
              }
            },
            {
              "content_list(0)@<myns>_common.M_Scroll_View_Grid_Panel": {
                "$Grid_Collection_Name": "item_list",
                "$Grid_Count": "#item_list_count",
                "$Grid_Item_Template": "my_screen.list_row",
                "$Grid_Items_Maximum": 5,
                "$Grid_Binding_Condition": "none"
              }
            }
          ]
        }
      }
    ]
  },

  "list_row": {
    "type": "panel",
    "size": ["100%", 30],
    "controls": [
      {
        "row_text(0)@<myns>_common.text": {
          "text": "#row_name",
          "anchor_from": "left_middle",
          "anchor_to": "left_middle",
          "offset": [5, 0],
          "bindings": [
            {"binding_name": "#row_name", "binding_type": "collection", "binding_collection_name": "item_list"}
          ]
        }
      },
      {
        "row_btn(0)@<myns>_common.newbutt2": {
          "size": [60, 24],
          "anchor_from": "right_middle",
          "anchor_to": "right_middle",
          "offset": [-5, 0],
          "$label_text": "选择",
          "$pressed_button_name": "#row_select_btn",
          "bindings": [
            {
              "binding_collection_name": "item_list",
              "binding_condition": "always_when_visible",
              "binding_type": "collection_details"
            }
          ]
        }
      }
    ]
  }
}
```

### 10.2 Python ScreenNode 完整骨架

```python
# -*- coding: utf-8 -*-
import re
import mod.client.extraClientApi as clientApi

ScreenNode = clientApi.GetScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()


class MyScreen(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.mclienSystem = param["cs"]
        """:type: ClientSystem"""
        self.Playerid = clientApi.GetLocalPlayerId()
        self.base_paths = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
        self._data = []
        self._ui_dirty = False

    def Create(self):
        # 标准 Modal 注入 4 步
        self.mclienSystem.RegisterTipsPanel(self, self.base_paths)
        self.mclienSystem.ResiPopup(self, self.base_paths)
        self.mclienSystem.RegisterContPanel(self, self.base_paths)
        self.mclienSystem.RegisterItemsTipsPanel(self, self.base_paths)
        self._fetch_data()

    def Init(self):
        pass

    def Update(self):
        if self._ui_dirty:
            self._ui_dirty = False
            self._refresh()

    def Destroy(self):
        self._data = None

    def _MarkUIUpdate(self):
        self._ui_dirty = True

    def _fetch_data(self):
        self.mclienSystem.TS({"lx": "GetData"}, self._on_data_back, "GetData")

    def _on_data_back(self, data):
        self._data = data.get("list", [])
        self._MarkUIUpdate()

    def _refresh(self):
        self.UpdateScreen()

    # ===== ViewBinder 绑定 =====

    @ViewBinder.binding(ViewBinder.BF_BindString, "#screen_title")
    def screen_title(self):
        return "我的界面"

    @ViewBinder.binding(ViewBinder.BF_BindInt, "#item_list_count")
    def item_list_count(self):
        return len(self._data)

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "item_list", "#row_name")
    def row_name(self, index):
        """:type: int"""
        return self._data[index].get("name", "")

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "item_list", "#row_select_label")
    def row_select_label(self, index):
        """:type: int"""
        return self._data[index].get("btn_text", "选择")

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#close_btn")
    def close_btn(self, args):
        clientApi.PopScreen()

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#row_select_btn")
    def row_select_btn(self, args):
        # 优先取 #collection_index；引擎版本差异导致取不到时，从行控件名末尾数字兜底
        index = args.get("#collection_index", -1)
        if index < 0:
            m = re.search(r'(\d+)$', args.get("button_scene_name", ""))
            if m:
                # button_scene_name 形如 "player_row1"、"player_row2"，末尾数字是 1-based 行号
                index = int(m.group(1)) - 1
        # 用 index 做业务逻辑
```

> **⚠️ 注意**：`button_scene_name` 正则兜底是引擎版本兼容 hack，**不建议作为首选方式**。新项目应优先确保 `collection_details` 的 `bindings` 正确配置（见 §六.3），让引擎直接提供 `#collection_index`。仅在测试发现取不到时才使用正则兜底。

**同名绑定原则**：`#row_select_label`（绑到 label 显示文字，`BF_BindString`）与 `#row_select_btn`（绑到 button 点击事件，`BF_ButtonClickUp`）**必须使用不同 name**，不可复用同一个 `#name` 挂两种类型的绑定。

> 模板用 `clientApi.PopScreen()` 关闭，因为业务界面通过 `PushScreen` 打开。若通过 `CreateUI` 创建则改为 `self.SetRemove()`，详见 §8.4。

### 10.3 Popup 确认弹窗调用

**前置**：`_popup_control` 需在 `Create()` 中通过 `ResiPopup` 注入后拿到 BaseUIControl 缓存下来。

```python
def Create(self):
    # ... 其他 Modal 注入
    self.mclienSystem.ResiPopup(self, self.base_paths)
    # 缓存 popup 控件引用（注入后 path 固定）
    self._popup_control = self.GetBaseUIControl(self.base_paths + "/M_Popup")
    self._popup_callback = None
    self._popup_cancel_callback = None

def show_confirm(self, title, text, on_confirm, on_cancel=None):
    popup = self._popup_control
    self.GetBaseUIControl(self.base_paths + "/M_Popup/title").asLabel().SetText(title)
    self.GetBaseUIControl(self.base_paths + "/M_Popup/content").asLabel().SetText(text)
    popup.SetVisible(True, False)
    self._popup_callback = on_confirm
    self._popup_cancel_callback = on_cancel

# 通过 CreateDynamicBind 在注入时绑定的回调：
def _bind_popup_confirm(self, screen_node):
    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, '#POPUP_TEXT_QR_BTN')
    def _on_confirm(args):
        screen_node._popup_control.SetVisible(False, False)
        if screen_node._popup_callback:
            screen_node._popup_callback()
    CreateDynamicBind(screen_node, _on_confirm)
```

### 10.4 Toast Tips 触发

**前置**：`_tips_control` 同样需在 `Create()` 中注入 + 缓存。

```python
def Create(self):
    self.mclienSystem.RegisterTipsPanel(self, self.base_paths)
    self._tips_control = self.GetBaseUIControl(self.base_paths + "/M_Tips_Panel")

def show_tips(self, text, duration=3.0):
    tips = self._tips_control
    label = self.GetBaseUIControl(self.base_paths + "/M_Tips_Panel/tips_text").asLabel()
    label.SetText(text)
    tips.SetVisible(True, False)
    tips.StopAnimation("alpha")
    tips.PlayAnimation("alpha")
    self.AddTimer(duration, lambda: tips.SetVisible(False, False))
```

> `PlayAnimation` / `StopAnimation` 建议显式传属性名（如 `"alpha"`、`"offset"`）；无参调用引擎行为在不同版本可能不一致。定时器用 `ScreenNode.AddTimer(delay, cb)`，不要用 `clientApi.AddTimer`。

### 10.5 Toggle 实例（screen JSON）

```json
{
  "mode_toggle(0)@<myns>_common.M_toggle": {
    "size": ["100%", 30],
    "$toggle_name": "#mode_toggle_jh",
    "$toggle_state_binding_name": "#mode_toggle_state",
    "$toggle_text": "显示模式"
  }
}
```

```python
@ViewBinder.binding(ViewBinder.BF_BindBool, '#mode_toggle_state')
def mode_toggle_state(self):
    return self._current_mode == "display"

@ViewBinder.binding(ViewBinder.ToggleFilter | ViewBinder.BF_ToggleChanged, '#mode_toggle_jh')
def mode_toggle_jh(self, args):
    state = args.get("state", False)
    self._current_mode = "display" if state else "edit"
    self._MarkUIUpdate()
```

### 10.6 EditBox 实例

```json
{
  "search_box(0)@<myns>_common.M_edit_box": {
    "size": ["100%", 30],
    "$text_box_name": "#search_edit_jh",
    "$text_edit_box_content_binding_name": "#search_edit_nr",
    "$place_holder_text": "请输入搜索内容"
  }
}
```

```python
@ViewBinder.binding(ViewBinder.BF_BindString, '#search_edit_nr')
def search_edit_nr(self):
    return self._search_text

@ViewBinder.binding(ViewBinder.BF_EditChanged | ViewBinder.BF_EditFinished, '#search_edit_jh')
def search_edit_jh(self, args):
    if not args or args.get('Mode', '') != 'Finished':
        return    # 仅输入完成时处理
    text = (args.get('Text') or '').strip()
    self._search_text = text
    self._MarkUIUpdate()
```

### 10.7 Slider 实例

```json
{
  "count_slider(0)@<myns>_common.M_slider": {
    "size": ["80%", 20],
    "$slider_name": "#count_slider_jh",
    "$slider_value_binding_name": "#count_slider_value",
    "$slider_steps_binding_name": "#count_slider_steps"
  }
}
```

```python
@ViewBinder.binding(ViewBinder.BF_BindInt, '#count_slider_value')
def count_slider_value(self):
    return self._count

@ViewBinder.binding(ViewBinder.BF_BindInt, '#count_slider_steps')
def count_slider_steps(self):
    return self._max_count

@ViewBinder.binding(ViewBinder.BF_SliderChanged | ViewBinder.BF_SliderFinished, '#count_slider_jh')
def count_slider_jh(self, args):
    self._count = int(args.get("value", 0))
    self._MarkUIUpdate()
```

### 10.8 折叠面板/区域 header 模板

```json
{
  "section_header(0)": {
    "type": "image",
    "texture": "textures/ui/<modname>/set_btn_a_1",
    "nineslice_size": [1, 1, 1, 1],
    "size": ["100%", 35],
    "controls": [
      {
        "header_text(0)@<myns>_common.text": {
          "text": "#section_title",
          "anchor_from": "left_middle",
          "anchor_to": "left_middle",
          "offset": [10, 0],
          "color": [1, 1, 1],
          "bindings": [
            {"binding_name": "#section_title", "binding_type": "global", "binding_condition": "none"}
          ]
        }
      },
      {
        "header_btn(0)@<myns>_common.newbutt2": {
          "size": [30, 30],
          "anchor_from": "right_middle",
          "anchor_to": "right_middle",
          "offset": [-5, 0],
          "$label_text": "X",
          "$pressed_button_name": "#section_close_btn"
        }
      }
    ]
  }
}
```

---

## 十一、UI 控件 API 速查与查图

### 11.1 类型转换器（16 个）

`GetBaseUIControl(path)` 返回 `BaseUIControl`，必须转换后才能调特定方法：

| 转换器 | 适用 | 常用方法 |
|--------|------|---------|
| `.asButton()` | button | `AddTouchEventParams()`, `SetButtonTouchUpCallback(fn)` |
| `.asLabel()` | label | `SetText(str)`, `GetText()`, `SetTextColor(rgb)` |
| `.asImage()` | image | `SetSprite(path)`, `SetSpriteColor(rgb)`, `SetSpriteGray(bool)`, `SetSpriteClipRatio(float)` |
| `.asSlider()` | slider | `SetSliderValue(val)`, `GetSliderValue()` |
| `.asSwitchToggle()` | toggle | `SetToggleState(val)`, `GetToggleState()` |
| `.asTextEditBox()` | edit_box | `SetEditText(str)`, `GetEditText()`, `SetEditTextMaxLength(n)` |
| `.asGrid()` | grid | `GetGridItem(x,y)`, `SetGridDimension(rows)` |
| `.asScrollView()` | scroll_view | `GetScrollViewContentControl()`, `SetScrollViewPos()`, `GetScrollViewPos()` |
| `.asItemRenderer()` | custom（item） | `SetUiItem(name, aux, ench, userData)` |
| `.asInputPanel()` | input_panel | `SetIsModal(bool)`, `GetIsModal()`, `SetIsSwallow(bool)` |
| `.asStackPanel()` | stack_panel | `SetOrientation(str)`, `GetOrientation()` |
| `.asProgressBar()` | progress_bar | `SetValue(float)` |
| `.asNeteaseComboBox()` | 下拉框 | `RegisterSelectItemCallback(fn)`, `RegisterOpenComboBoxCallback(fn)` |
| `.asNeteasePaperDoll()` | 纸娃娃 | — |
| `.asMiniMap()` | 小地图 | `RepaintMiniMap()` |
| `.asSelectionWheel()` | 选择轮 | — |

### 11.2 常用通用方法（BaseUIControl）

| 方法 | 说明 |
|------|------|
| `SetVisible(visible, animate)` | 显隐控件（animate 默认 False） |
| `SetPosition(x, y)` | 设置位置 |
| `SetSize(w, h)` | 设置尺寸 |
| `SetAlpha(alpha)` | 设置透明度 |
| `SetLayer(layer)` | 设置层级 |
| `SetAnchorFrom(anchor)` | 设置锚点来源 |
| `SetAnchorTo(anchor)` | 设置锚点目标 |
| `PlayAnimation(prop)` | 播放属性动画（必传属性名，如 `"size"`, `"offset"`, `"alpha"`） |
| `StopAnimation(prop)` | 停止属性动画（必传属性名） |
| `SetAnimation(animData, prop)` | 动态注册并播放动画（签名以 MCP `get_api_detail` 为准） |
| `SetTouchEnable(bool)` | 是否可触摸 |

### 11.3 查 API 的指引

编写 Python 代码前，对不确定的 API 签名：
1. 先调 MCP `search_api(query=关键词, entry_type='api')` 查搜索结果
2. 再调 `get_api_detail(name=接口名)` 查详细签名
3. 交叉验证后落笔，禁止凭记忆猜

---

## 十二、通用设置 vs 自建 JSON

### 12.1 两种路线

| 路线 | 适用场景 | 优势 | 劣势 |
|------|---------|------|------|
| **自建 JSON UI** | 需要完全自定义外观/交互/复杂布局 | 100% 可控，风格统一 | 工作量大 |
| **引擎通用设置** `RegisterSettingInst` | 纯配置项（开关/文本/滑条），无需自定义外观 | 开箱即用，链式 API | 无法自定义布局，功能受限 |

### 12.2 引擎通用设置用法

```python
comp = CF.CreateNeteaseWindow(LevelID)
settingInst = comp.RegisterSettingInst("my_mod", "我的模组", "textures/ui/my_mod/icon")
if settingInst:
    settingInst.AddText("text_uid_01", "提示文字")
    settingInst.AddToggle("toggle_uid_01", "自动排序", False, self.on_toggle_changed)
```

- 在 `UiInitFinished` 回调中注册（过早注册返回 None）
- 每个 mod 仅能注册**一个 `RegisterSettingInst` 设置实例**（与自建 JSON UI 屏数量无关，自建 JSON 可以注册任意多个 screen）
- `OpenSettingUI()` 打开，`CloseSettingUI()` 关闭

### 12.3 选择建议

- **需要品牌一致性**（与项目其他界面统一的风格/布局/动画）→ 自建 JSON
- **快速添加几个开关/配置** → 引擎通用设置
- **需要跨存档导入导出界面** → 自建 JSON（通用设置无法实现）
- 两个参考项目（custom_warehouse / quest_engine）全部选择自建 JSON

---

## 十三、input_panel 模态弹窗模板（用户自定义子面板）

> **⚠️ 与 §五.8 公共 Modal 组件的区别**：
> - 本节描述的 `1_input_panel` / `2_input_panel` 是**自定义子面板**，直接写在 screen JSON 的根 panel 中，通过 `SetVisible` 切换显隐。
> - §五.8 的 `M_Popup` / `M_CUSBOX_PANEL` / `M_Tips_Panel` 等是**公共可复用组件**，必须用 `CreateChildControl` 运行时从 `<modname>_common` 注入（见 §七），**不得**直接写在 screen JSON 中。
> - 简单判断：需要跨屏复用 / 标准确认框 → 走公共 Modal 注入；有特殊布局 / 固定在此屏使用 → 走 input_panel 静态声明。

本节是**用户手绘并验证过的标准弹窗模板**，所有需要自定义弹出子窗口的场景（设置、编辑、确认等）一律从此模板展开，不得自创结构。

### 13.1 结构总览

```
input_panel (layer 300, visible false, modal true)
├── bg              ← hei 遮罩 (alpha 0.5, nineslice 1px)
└── panel           ← 弹窗主体 (固定宽, 高 100%cm 自适应)
    ├── bg          ← 主体背景图 (set_toggle_b, alpha 0.5, 100%sm+2px)
    └── stack_panel ← 垂直内容栈 (100%+-2px × 100%c+1px)
        ├── title_panel  ← 标题栏 (高 18px)
        │   ├── bg       ← 标题背景图 (set_btn_a_1 或 top_bg, nineslice 1px)
        │   ├── text(0)  ← 标题文字
        │   └── xxx_btn  ← 关闭按钮 (xxx_a/xxx_b 贴图, 15×15)
        ├── nr × N       ← 功能行 (高 24px, 可重复)
        │   └── gn       ← 控件容器 (100%+-1px, 放 text/newbutt2/toggle/slider 等)
        └── down_panel   ← 底部确认栏 (仅"有确认"版本, 高 18px)
            └── newbutt2 ← 确认按钮 (绿色, 100%+-1px)
```

### 13.2 两个版本

| 版本 | 命名 | 特征 |
|------|------|------|
| **无按钮版** | `1_input_panel` | 只有 title_panel + nr 行，无 down_panel |
| **有确认版** | `2_input_panel` | title_panel + nr 行 + down_panel（绿色确认按钮） |

### 13.3 关键尺寸约定

| 控件 | size | 说明 |
|------|------|------|
| `input_panel` | `["100%+0px", "100%+0px"]` | 全屏覆盖 |
| `bg`（遮罩） | `["100%+0px", "100%+0px"]` | 同上，alpha 0.5 |
| `panel`（主体） | `[170.0, "100%cm+0px"]` | **固定宽 170px**，高自适应内容 |
| `bg`（主体背景） | `["100%sm+2px", "100%sm+0px"]` | 比主体大 2px（1px 边框效果），offset `[0, -1]` |
| `stack_panel` | `["100%+-2px", "100%c+1px"]` | 左右各缩 1px，高自适应+1px |
| `title_panel` | `["100%+0px", 18.0]` | 高 18px |
| `nr` | `["100%+0px", 24.0]` | 高 24px |
| `gn` | `["100%+0px", "100%+-1px"]` | 比父缩 1px（顶部留 1px 分割线间隙） |
| `down_panel` | `["100%+0px", 18.0]` | 高 18px |

### 13.4 模板 JSON — 无按钮版（1_input_panel）

```json
{
    "1_input_panel": {
        "type": "input_panel",
        "size": ["100%+0px", "100%+0px"],
        "layer": 300,
        "visible": false,
        "button_mappings": [
            {
                "to_button_id": "#netease_to_button_id",
                "from_button_id": "button.menu_select",
                "mapping_type": "pressed"
            }
        ],
        "modal": true,
        "controls": [
            {
                "bg": {
                    "type": "image",
                    "size": ["100%+0px", "100%+0px"],
                    "layer": 1,
                    "alpha": 0.5,
                    "nineslice_size": [1, 1, 1, 1],
                    "texture": "textures/ui/<modname>/hei"
                }
            },
            {
                "panel": {
                    "type": "panel",
                    "size": [170, "100%cm+0px"],
                    "layer": 5,
                    "controls": [
                        {
                            "bg": {
                                "type": "image",
                                "anchor_from": "top_middle",
                                "anchor_to": "top_middle",
                                "offset": [0, -1],
                                "size": ["100%sm+2px", "100%sm+0px"],
                                "layer": 1,
                                "alpha": 0.5,
                                "nineslice_size": [1, 1, 1, 1],
                                "texture": "textures/ui/<modname>/set_toggle_b"
                            }
                        },
                        {
                            "stack_panel": {
                                "type": "stack_panel",
                                "anchor_from": "top_middle",
                                "anchor_to": "top_middle",
                                "size": ["100%+-2px", "100%c+1px"],
                                "layer": 1,
                                "controls": [
                                    {
                                        "title_panel": {
                                            "type": "panel",
                                            "anchor_from": "top_middle",
                                            "anchor_to": "top_middle",
                                            "size": ["100%+0px", 18],
                                            "layer": 1,
                                            "controls": [
                                                {
                                                    "bg": {
                                                        "type": "image",
                                                        "size": ["100%+0px", "100%+0px"],
                                                        "layer": 1,
                                                        "color": [0.2353, 0.5216, 0.1529],
                                                        "nineslice_size": [1, 1, 1, 1],
                                                        "texture": "textures/ui/<modname>/set_btn_a_1"
                                                    }
                                                },
                                                {
                                                    "text(0)@<myns>_common.text": {
                                                        "layer": 2,
                                                        "text": "标题"
                                                    }
                                                },
                                                {
                                                    "xxx_btn@<myns>_common.newbutt2": {
                                                        "$default_texture": "textures/ui/<modname>/xxx_a",
                                                        "$hover_texture": "textures/ui/<modname>/xxx_a",
                                                        "$label_text": "",
                                                        "$pressed_texture": "textures/ui/<modname>/xxx_b",
                                                        "anchor_from": "right_middle",
                                                        "anchor_to": "right_middle",
                                                        "offset": [-1, 0],
                                                        "size": [15, 15]
                                                    }
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "nr": {
                                            "type": "panel",
                                            "size": ["100%+0px", 24],
                                            "layer": 1,
                                            "controls": [
                                                {
                                                    "gn": {
                                                        "type": "panel",
                                                        "anchor_from": "top_middle",
                                                        "anchor_to": "top_middle",
                                                        "size": ["100%+0px", "100%+-1px"],
                                                        "layer": 1,
                                                        "controls": [
                                                            {
                                                                "text(0)@<myns>_common.text": {
                                                                    "anchor_from": "left_middle",
                                                                    "anchor_to": "left_middle",
                                                                    "offset": [1, 0],
                                                                    "text": "设置"
                                                                }
                                                            },
                                                            {
                                                                "newbutt2(0)@<myns>_common.newbutt2": {
                                                                    "$label_text": "设置",
                                                                    "anchor_from": "right_middle",
                                                                    "anchor_to": "right_middle",
                                                                    "size": [40, 18]
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }
}
```

### 13.5 模板 JSON — 有确认版（2_input_panel）

在 `stack_panel` 的 `controls` 数组末尾追加 `down_panel`：

```json
{
    "down_panel": {
        "type": "panel",
        "anchor_from": "top_middle",
        "anchor_to": "top_middle",
        "size": ["100%+0px", 18],
        "layer": 1,
        "controls": [
            {
                "newbutt2(0)@<myns>_common.newbutt2": {
                    "$button_img_color": [0.2353, 0.5216, 0.1529],
                    "$label_text": "确认",
                    "anchor_from": "top_middle",
                    "anchor_to": "top_middle",
                    "size": ["100%+0px", "100%+-1px"]
                }
            }
        ]
    }
}
```

> **标题栏 bg 差异**：无按钮版标题用 `set_btn_a_1` + 绿色 color 叠加；有确认版标题可用 `top_bg` + 白色 color。两种均可，按视觉需要选择。

### 13.6 gn 控件容器用法

`gn` 是每个 `nr`（功能行）内的控件容器，标准尺寸 `["100%+0px", "100%+-1px"]`（顶部缩 1px 做分割线）。常见放法：

| 场景 | 左侧 | 右侧 |
|------|------|------|
| 设置项 | `text`（标签名, left_middle, offset [1, 0]） | `newbutt2`（按钮, right_middle, [40, 18]） |
| 开关项 | `text`（标签名） | `M_toggle`（开关, right_middle） |
| 滑条项 | `text`（标签名） | `M_slider`（滑条, right_middle） |
| 输入项 | `text`（标签名） | `M_edit_box`（输入框, right_middle） |
| 纯文字 | `text`（居中或左对齐） | — |

### 13.7 弹窗显隐

弹窗默认 `visible: false`，通过 Python 控制：

```python
# 显示弹窗
self.GetBaseUIControl(self.base_paths + "/root_panel/1_input_panel").SetVisible(True, False)

# 隐藏弹窗
self.GetBaseUIControl(self.base_paths + "/root_panel/1_input_panel").SetVisible(False, False)
```

### 13.8 命名约定

| 名称 | 含义 |
|------|------|
| `1_input_panel`, `2_input_panel` | 数字前缀区分版本（1=无按钮, 2=有确认） |
| `title_panel` | 标题栏（固定名称） |
| `nr` | 功能行（可重复，用 `nr`, `nr(0)`, `nr(1)` ... 递增） |
| `gn` | 控件容器（每个 nr 内固定名称） |
| `down_panel` | 底部确认栏（固定名称，仅 2_input_panel） |

---

## 十四、生产实战模式速查

以下模式在 custom_warehouse / quest_engine 中高频出现，是 modui 骨架之外的必备技能。

### 14.1 CD 防抖（AddUserUiCd）

避免快速连点导致的重复请求 / 界面抖动：

```python
def AddUserUiCd(self, key='none', times=1.0):
    """返回 True 表示处于 CD，应直接 return"""
    if key in self.UserUITickList:
        return True
    self.UserUITickList[key] = time.time() + times
    return False

def Update(self):
    now = time.time()
    for k in list(self.UserUITickList):
        if self.UserUITickList[k] < now:
            del self.UserUITickList[k]
```

**使用**：
```python
@ViewBinder.binding(ViewBinder.BF_ButtonClickUp, '#save_btn')
def save_btn(self, args):
    if self.mclienSystem.AddUserUiCd('save_btn', 0.3):
        return    # 0.3s 内重复点击直接忽略
    self._save_data()
```

### 14.2 延迟统一刷新（合并多次 UpdateScreen）

多个数据源同帧变更时，聚合成一次刷新：

```python
def Update(self):
    if self.delaytick >= 1:
        self.delaytick -= 1
        if self.delaytick == 0:
            self.UpTopUI(delaytickupdate=True)

def UpTopUI(self, defdelaytick=20, delaytickupdate=False):
    if not delaytickupdate:
        self.delaytick = defdelaytick    # 排队
        return
    uinode = clientApi.GetTopUINode()
    if uinode:
        uinode.UpdateScreen(True)         # 20 tick 后统一触发
```

**与 §8.1 `_ui_dirty` 的区别**：`_ui_dirty` 是**当前 ScreenNode 内部**节流；`UpTopUI` 是 **ClientSystem 全局**节流，适合服务端推送数据到多屏刷新的场景。

### 14.3 剪贴板导入 / 导出

跨存档共享数据的最简单方案：

```python
# 导出（复制 UID / JSON 到剪贴板）
CF.CreateGame(clientApi.GetLevelId()).SetClipboardContent(uid)
self.mclienSystem.ShowTipsPanel('复制UID成功！')

# 导入（从剪贴板取）
text = CF.CreateGame(clientApi.GetLevelId()).GetClipboardContent()
# 支持自由文本 + 坐标解析
apos = M.parse_minecraft_coordinates(text)   # "10 64 20" / "/execute at ... run tp 10 64 20"
```

### 14.4 数据分层与版本对齐

大型 Mod 客户端数据 4 层：

| 层级 | 用途 | 存储方式 |
|------|------|---------|
| **世界级** | 服务端权威 + 客户端缓存 | `ExtraData` 主键 |
| **玩家级** | 单玩家进度 | `ExtraData` 玩家键 |
| **客户端本地** | 单机偏好（UI 布局/开关） | `compConfigClient.SetConfigData('*.json', ...)` |
| **跨存档** | 全局配置迁移 | `compConfigClient.SetConfigData('*.json', True)` |

**版本对齐**（先问服务端版本再决定是否覆盖）：

```python
def SavaData(self, key):
    def on_ver(args):
        if args['ser_version'] != args['cla_version']:
            # 版本不一致才真写
            self.TS({'lx': 'cla_data_to_ser_sava', 'key': key, 'data': self._data}, None)
    self.TS({'lx': 'data_get_version', 'key': key, 'claversion': self._version},
            on_ver, 'has_data_version')
```

### 14.5 数据变更后 `_version_` 自增

编辑保存时对比差异，仅在有变化时递增版本号，让服务端知道是"新变更"：

```python
if server_data.getobj(self.data['_uid_']) != self.data:
    self.data['_version_'] = self.data.get('_version_', 0) + 1
    self.mclienSystem.Quest_Engine_Data['quest_item']['version'] += 1
```

### 14.6 保存时数据裁剪 `_clear_or_sedef_data`

减小落盘体积：与默认值相同的字段不存；加载时补齐：

```python
def _clear_or_sedef_data(self, isclear=False):
    keys = ['pos', 'events', 'keyquest']
    if isclear:
        for k in list(self.data):
            if k in keys and self.data[k] == CG.default_data[k]:
                self.data.pop(k)          # 删除等于默认的字段
    else:
        for k in keys:
            if k not in self.data:
                self.data[k] = copy.deepcopy(CG.default_data[k])   # 加载时补齐
```

### 14.7 UID 生成（8/16/32 位）

```python
import uuid
uid = uuid.uuid4().hex[:6].upper()   # 6 位短 uid，界面动态子控件用
uid = uuid.uuid4().hex[:8].upper()   # 8 位业务 uid（任务/配置项）
uid = uuid.uuid4().hex                # 32 位完整
```

### 14.8 动态子控件按 uid 命名（自毁 tips 卡）

```python
def PopTipsItem(self, title, subtitle, icondata):
    ui_uid = uuid.uuid4().hex[:6]
    self.CreateChildControl('mod_common.tips_item', ui_uid, self.tips_parent_path)
    # tips_item 模板中带 anims，动画 destroy_at_end 自毁
```

配套 JSON：
```json
"tips_item": {
    ...,
    "anims": ["@mod_anims.chat_stack_size"],   // 带 destroy_at_end 的动画链
}
```

### 14.9 动画事件驱动队列

`SetAnimEndCallback` 挂钩动画结束事件，形成"当前动画播完 → 播下一条"的队列：

```python
def PlayHudSubTitles(self):
    self._SetSubtitle(self.subtitles_queue.pop(0))
    self.SetAnimEndCallback('maxtips_alpha_on_2', self.AnimationCallback)

def AnimationCallback(self):
    if self.subtitles_queue:
        self.PlayHudSubTitles()
```

**支持的动画事件类型**：

| anim_type | 用途 |
|-----------|------|
| `wait` | 占位停顿（`duration` 直接设时长） |
| `destroy_at_end` | 播完销毁指定名字的子控件 |
| `play_event` / `end_event` | 屏幕入场/退场生命周期事件 |
| `flip_book` | 帧动画（`frame_count` + `fps`） |

### 14.10 3D 世界坐标 → 2D 屏幕投影（HUD 目标追踪）

HUD 常见需求：把世界坐标标记转为 2D 屏幕位置（超出屏幕时贴边显示带箭头）：

```python
def get_task_icon_screen_pos(player_pos, camera_yaw, camera_pitch,
                              target_pos, screen_size,
                              edge_left, edge_right, edge_top, edge_bottom,
                              center_angle=10.0):
    """返回 (x, y, arrow_angle, in_center)"""
    # 1. 世界向量 → 相机空间投影
    # 2. 计算角度差
    # 3. 落在 center_angle 内 → in_center=True
    # 4. 超出 → 边缘 + 箭头方向
```

配 `GameRenderTickEvent()` 每帧更新，`Update()` 里 `tick % 5 == 0` 节流刷新距离文本。

### 14.11 拖拽按钮（`MoveBtnMappings`）

一个透明按钮覆盖在目标 UI 上，用户拖动同步 offset，位置落盘可一键归位：

```python
# 注册可拖拽区
MoveBtnMappings(self, 'Quest_MoveDta', [
    {'btn_path': self.base_paths + '/hud_task_bar',
     'target_path': self.base_paths + '/task_bar_container'},
])

# 一键归位
self.mclienSystem.ResetAllBtnsToDefault('Quest_MoveDta')
```

### 14.12 JEI 风格物品选择器

分页 + 搜索 + 三态切换（全物品 / 玩家背包 / 自定义 RPG 物品）：

```python
class JEIStyleSorter(object):
    def __init__(self, all_items, mclass, items_per_page=100):
        self.mclass = mclass
        self._AllItemsList = all_items
        self.current_items = []
        self.search_term = ''
        self.is_backpack_mode = False

    def search(self, term=''):
        self.search_term = term.strip()
        # 按 (是否原版, 分类, 类型, 中文名, id) 排序
        self._recalc()

    def next_page(self): ...
    def prev_page(self): ...
    def go_to_page(self, n): ...
    def set_to_backpack_mode(self):
        raw = CF.CreateItem(LevelID).GetPlayerAllItems(0, True)
        self.update_items(self._convert_backpack(raw))
    def set_to_normal_mode(self):
        self.update_items(self._AllItemsList)
```

UI 侧：三档 toggle（正常 / 背包 / RPG）+ 分页按钮 + 搜索 edit + `_count` 绑定物品格数。

### 14.13 多阶段编辑器：分组 tab + 子面板路径预置

复杂编辑器（任务/角色/装备）常用「tab 切换 + 子面板集合可见性」：

```python
class MyEditorScreen(ScreenNode):
    def __init__(self, ...):
        # 一次性预置所有子面板路径为属性
        self.set_panel_general = self.base_paths + '/set_panel_general'
        self.set_panel_detail = self.base_paths + '/set_panel_detail'
        self.set_panel_target = self.base_paths + '/set_panel_target'
        self.tab_index = 0
        # 分组：tab index → 应显示的子面板 index 列表
        self.tab_groups = [
            [0, 1, 2, 3],       # tab 0: 通用
            [4, 5, 6, 7],       # tab 1: 详情
            [8, 9],             # tab 2: 目标
        ]

    def all_get_gn_panel_visible(self, tab_idx):
        for i, panel in enumerate(self.all_panels):
            visible = i in self.tab_groups[tab_idx]
            self.GetBaseUIControl(panel).SetVisible(visible, False)
```

### 14.14 编辑态标记 `_IsEditState_`

区分「创建新项 vs 编辑已有项」，避免编辑时误触新建逻辑：

```python
# 打开编辑时
self.item_data = copy.deepcopy(existing_data)
self.item_data['_IsEditState_'] = True

# 保存前清除
if '_IsEditState_' in self.data:
    self.data.pop('_IsEditState_')
    # ...仅编辑态才做版本 +1
```

### 14.15 UI 内嵌调试日志（环形缓冲）

在 ClientSystem 里维护 FIFO 环形日志，可在专属屏内展示：

```python
self._GameDevLogList = []
self.GameDevLogSetting = {
    'log_toggle': False,
    'enable_openui_change': True,
    'enable_quest_status_change': True,
    # ... 分级开关
}

def AddGameDevLogList(self, text):
    if not self.GameDevLogSetting['log_toggle']:
        return
    if len(self._GameDevLogList) >= 100:
        self._GameDevLogList.pop(0)     # FIFO 上限 100
    ts = time.strftime('§7[%H:%M:%S] ', time.localtime())
    self._GameDevLogList.append(ts + text)
```

---

## 十五、公共库跨屏控件详解（补充）

### 15.1 M_CUSBOX_* 下拉框（优先使用前置）

> 前置已提供 `API_RegisterCusBoxPanel` / `API_OpenCusBoxPanel` 和兼容入口 `ResiCusBoxUi`。依赖前置的项目按 [公共 UI 接入](../daguomiao-api/references/ui.md) 注册与打开，不再从 quest_engine 复制组件。以下代码仅说明旧调用形态；数据格式和参数以当前前置源码为准。

`M_CUSBOX_BTN` + `M_CUSBOX_PANEL` + `M_CUSBOX_GRID` 三件套，实现选项按钮弹出选择列表：

```python
# 1. Create() 中注入
self.M_CUSBOX_BTN_Cont = self.mclienSystem.ResiCusBoxUi(
    self,
    self.base_paths,
    self.M_CUSBOX_BTN,           # 挂载点 path
    self._on_cusbox_selected     # 选中回调 back(data)
)

# 2. 展示时给数据
self.M_CUSBOX_BTN_Cont.OnShow(
    [
        ['显示名', 'id值', 'textures/ui/mod/xxx'],   # 三元组：文本+值+图标
        ['选项 B', 'b_id', ''],
    ],
    title='请选择目标类型'
)

# 3. 预选中
self.M_CUSBOX_BTN_Cont.SelectItem('显示名')
```

**核心绑定名**（内部固定）：
- `#M_CUSBOX_GRID_ITEM_COUNT`
- `#M_CUSBOX_TOGGLE_NAME` / `#M_CUSBOX_TOGGLE_STATE`
- `#M_CUSBOX_TOGGLE_ITEM_TEXT` / `#M_CUSBOX_TOGGLE_ITEM_ICON`

数据源通过 `setattr(self.UInode, '__CusBoxDataList__', ...)` 挂到 UInode，collection 绑定通过它取当前值。

### 15.2 Popup 智能显示（参考实现，可复用于任意项目）

`M_Popup` 的确认/取消按钮通过 visible 绑定动态显示：

```python
class Popup(object):
    def Popup(self, text, callback=None, title='提醒'):
        self.text, self.callback, self.title = text, callback, title
        # 无 callback → 只显示确认按钮（`#POPUP_TEXT_BTN_QR_0_VISIBLE` = True）
        # 有 callback → 显示两按钮（`#POPUP_TEXT_BTN_QR_1_VISIBLE` = True）
        self.UInode.GetBaseUIControl(path + '/M_Popup').SetVisible(True, False)

    def CreateUI(self):
        if 'M_Popup' not in self.UInode.GetChildrenName(self.createpath):
            self.UInode.CreateChildControl(...)
            setattr(self.UInode, '__PopupClass__', self)   # 挂 UInode 供全局访问
```

**跨屏调用**：
```python
self.mclienSystem.OpenPopup('确定删除？', on_confirm, title='警告')
# 内部走 getattr(clientApi.GetTopUINode(), '__PopupClass__').Popup(...)
```

### 15.3 全局 ShowTipsPanel / ShowItemsTipsPanel

统一走 `clientApi.GetTopUINode()`，任何屏都能触发：

```python
def ShowTipsPanel(self, text, isdisp=False):
    if isdisp:
        # 延迟 0.5s 触发（避免和当前动画冲突）
        CF.CreateGame(LevelID).AddTimer(0.5, self.ShowTipsPanel, text)
        return
    uinode = clientApi.GetTopUINode()
    if uinode and getattr(uinode, '__TipsPanel__', None):
        uinode.__TipsPanel__.Show(text)
```

`ShowItemsTipsPanel` 统一 3 种输入源：
- `i(minecraft:apple,False,-1,)` — 原生物品
- `r(uid)` — 自定义 RPG 物品
- 原生 nbt dict — 直接传入

### 15.4 复合物品渲染器（3 源统一）

任务/仓库常需要展示物品/贴图/自定义 RPG 物品，用统一格式字符串：

| 前缀 | 语法 | 含义 |
|------|------|------|
| `p(` | `p(book` | 贴图（查 `icon_list` 表） |
| `i(` | `i(minecraft:apple,False,-1,` | 原生物品：id, isEnchant, color, materialr |
| `r(` | `r(<uid>)` | 自定义 RPG 物品（跨 Mod） |

Python 端统一函数：

```python
def GetQusetIconSetUI(self, icodata, is_img=True, getrendererdata=False):
    icon = {'aux': 0, 'color': -1, 'materialr': '', 'p': ''}
    if icodata.startswith('p('):
        icon['p'] = CG.icon_list.get(icodata[2:], {}).get('p', '')
    elif icodata.startswith('i('):
        parts = icodata[2:].split(',')
        icon.update({'aux': 0, 'color': int(parts[2]), 'materialr': parts[3]})
    elif icodata.startswith('r('):
        # 走 RPG 物品接口
        pass
    return icon
```

UI 侧 5 元组绑定（`_texture` / `_id_aux` / `_custom_color` / `_trim_material` / `_materialr`）分别驱动 image + ItemRenderer。

---

## 附录：硬性检查清单

编写 UI 前后对照以下清单逐项确认：

### JSON 端
- [ ] `_ui_defs.json` 注册了所有 screen 文件
- [ ] `_global_variables.json` 定义了贴图根路径变量
- [ ] 每个 screen JSON 含三键：`namespace` + `main@common.base_screen` + 根 panel
- [ ] `main` 的 `$screen_content` 指回本文件根 panel
- [ ] 贴图路径不硬编码，用全局变量或 `textures/ui/<modname>/` 标准路径
- [ ] 公共组件从实际业务库或 `DAGUOMIAO_API_MOD_common` 继承，避免重复实现
- [ ] 绑定名遵循 `_jh/_nr/_btn/_state/_visible/_is_` 后缀约定
- [ ] collection 控件带 `binding_collection_name`
- [ ] `#visible` 重定向用 `binding_name_override: "#visible"`
- [ ] 根 panel `layer: 1`，Modal `layer: 1000+`
- [ ] Modal `modal: true`，不设 `is_swallow: true`
- [ ] 遮罩图 `alpha: 0.5`；根 panel 下用 `size: ["300%", "300%"]`，input_panel 内用 `size: ["100%+0px", "100%+0px"]`
- [ ] 布局尺寸已按 §四「布局尺寸选择指南」选择：全屏用 `100%` 不居中；弹窗/固定尺寸必须居中+遮罩

### Python 端
- [ ] `RegisterUI` 在 `UiInitFinished` 回调中调用
- [ ] `PushScreen` 返回值保存到 `self.<screenDef>` 成员变量（`__init__` 预置 `None`）
- [ ] HUD 用 `CreateUI(isHud:1)`，业务用 `PushScreen`
- [ ] `ScreenNode.__init__` 取 `param["cs"]`，设 `self.base_paths`
- [ ] `Create()` 中注入公共 Modal 子组件
- [ ] `Update()` 用 `_ui_dirty` 节流
- [ ] ViewBinder 装饰器绑定名与 JSON 中的 `#name` 完全匹配
- [ ] collection 绑定用 `binding_collection` 装饰器
- [ ] 关闭 UI 用 `clientApi.PopScreen()`（PushScreen 打开）或 `self.SetRemove()`（CreateUI 创建）
- [ ] 无 f-string、无 type hints
- [ ] 文件顶部 `# -*- coding: utf-8 -*-`

---

## 一句话总结

> **先查前置和业务公共库 → 按真实组件契约注册与绑定 → PushScreen 保存实例并配套 PopScreen → 保留原有绑定和回调语义 → Python 2.7 写法**
