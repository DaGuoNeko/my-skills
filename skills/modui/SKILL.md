---
name: modui
description: >
  modui — 网易 MC 基岩版 Mod UI 统一规范
---
# Skill: modui — 网易 MC 基岩版 Mod UI 统一规范

本技能讲 UI 的工程约定：文件结构、Screen 约定、绑定命名、Modal 注入、ScreenNode 装配、动画和生产实战模式。不收录公共组件参数，组件与视觉风格以前置当前源码为准。

## 规范优先级（强制）

### 总原则
用户本次要求 > 项目实际代码与前置源码 > 下表各技能。控件名、参数、接口签名一律以实际加载的源码为准。

### 按内容分工

| 管什么 | 依赖 DAGUOMIAO_API_MOD 的项目 | 不依赖前置的老项目 |
|---|---|---|
| 视觉风格：配色、贴图、字体、按钮和面板样式 | **前置**：按 [UI 风格对齐前置](../daguomiao-api/references/ui-style.md)，用脚本读前置当前控件与贴图，继承 `DAGUOMIAO_API_MOD_common` | 项目自己的 `<modname>_common.json` |
| 公共功能：弹窗、选择器、分组列表、数量和颜色面板 | **前置**：[前置 UI 参考](../daguomiao-api/references/ui.md) | 项目自己的公共库源码 |
| 布局：版式、分栏、标签页、控件位置 | **AI 按内容决定**，守 ui-style.md 的布局底线，同类界面优先沿用前置样板 | AI 按内容决定 |
| JsonUI 语法、绑定写法、动画 | `jsonui` 技能 | 同左 |
| 文件结构、命名后缀、ScreenNode 装配、生产实战模式 | 本技能 | 同左 |
| SDK 接口签名 | ModSDK MCP：`search_api` / `get_api_detail` | 同左 |

### 冲突处理
- 依赖前置的项目，视觉一律听前置；本技能和旧项目代码里的样式写法不再套用。
- 前置没有需要的贴图、颜色或控件：先问用户，或建议加进前置；不在业务模组里自己画、自己调色。
- 本技能覆盖不了的场景（新增 SDK API、引擎版本差异）主动查 MCP 文档，不以本技能为唯一限制。

## 触发关键词

当用户提到 UI、界面、JsonUI、屏幕、控件、绑定、绑定设计、Modal、弹窗、列表、按钮、堆叠面板、滚动视图、网格、Toggle、EditBox、Slider、Toast、动画、ScreenNode、ViewBinder 等关键词时触发。与通用 `jsonui` 技能互补：`jsonui` 讲语法，本技能讲**工程约定**，视觉风格看上方优先级表。

---

## 一、加载策略

- **本文件**：工程约定，始终在触发时加载
- **需要深入时**：
  - 查公共控件和 `$` 参数 → 依赖前置时运行 `daguomiao-api/scripts/ui_catalog.py show <控件名>`；老项目读其 `*_common.json`
  - 要完整的 screen JSON / ScreenNode 写法 → 读最接近的前置样板界面（`ui_catalog.py screens`）
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

### Python 写法

遵循 dev 技能「网易 Minecraft Mod 专用约定」中的 Python 2.7、编码和 `:type:` 注释规则。

---

## 三、文件结构

```
资源包/ui/
├── _ui_defs.json              # 注册所有 UI 文件（除 _global_variables / _ui_defs 本身）
├── _global_variables.json     # 全局变量（贴图根路径等）；可选但推荐
├── <modname>_common.json      # 业务公共组件库（依赖前置时只放前置没有的业务控件，不复制前置）
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
- 完整 screen JSON 参考最接近的前置样板界面（`ui_catalog.py screens`）

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

## 六、数据绑定规范

### 6.1 绑定类型

`global` / `collection` / `collection_details` / `view` 四类绑定的语法、装饰器和 grid 内按钮取 index 的写法统一见 jsonui 技能 `references/guide.md` 第十三章与 16.1。本章只规定命名和写法约定。

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
Python 回调通过 `args.get('#collection_index')` 取索引；兜底从 `button_scene_name` 正则解析。完整写法见 jsonui 手册 16.1。

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

**Mode 过滤约定**：大多数场景只想在输入完成时处理逻辑，用 `Mode == 'Finished'` 过滤。写法参考前置样板界面里的搜索框回调。

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

> 依赖前置时，确认弹窗用前置 `ResiPopup` / `OpenPopup`，见前置 UI 参考。

### 7.4 遮罩标准写法

遮罩由 `input_panel` + `hei` 图片组成，写法参考前置样板界面。关键规则：

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

> 此处仅列核心结构，完整写法参考前置样板界面对应的 ScreenNode。

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

### 8.2 ViewBinder 装饰器

`BF_*` 常量、组合写法（如 `ToggleFilter | BF_ToggleChanged`、`BF_EditChanged | BF_EditFinished`）和集合绑定回调签名见 jsonui 技能 `references/guide.md` 第七、十三章及 16.15。绑定名按 6.2 的后缀约定命名。

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
            'modScripts.myClientSystem.MyScreen',      # ← 业务 ScreenNode 子类
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

## 附录：硬性检查清单

编写 UI 前后对照以下清单逐项确认：

### JSON 端
- [ ] `_ui_defs.json` 注册了所有 screen 文件
- [ ] `_global_variables.json` 定义了贴图根路径变量
- [ ] 每个 screen JSON 含三键：`namespace` + `main@common.base_screen` + 根 panel
- [ ] `main` 的 `$screen_content` 指回本文件根 panel
- [ ] 贴图路径不硬编码，用全局变量或 `textures/ui/<modname>/` 标准路径
- [ ] 公共组件从实际业务库或 `DAGUOMIAO_API_MOD_common` 继承，避免重复实现
- [ ] 依赖前置时视觉按 ui-style.md：没有自造贴图、颜色、字体，截图和前置样板界面一致
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

> **用脚本查前置当前组件 → 视觉跟前置、布局按内容 → 按真实组件契约注册与绑定 → PushScreen 保存实例并配套 PopScreen → 保留原有绑定和回调语义 → Python 2.7 写法**
