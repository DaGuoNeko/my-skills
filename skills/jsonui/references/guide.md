# Minecraft 基岩版 JsonUI 开发规范

> 知识来源：[猫猫子 JsonUI 教程](https://www.yuque.com/maomaozi-hldyx/bgelcp)（作者未知，由猫猫子整理发布）
> Content was rephrased for compliance with licensing restrictions.

---

## 一、JsonUI 核心概念

JsonUI 是 Minecraft 基岩版（含网易中国版）使用 JSON 文件描述 UI 界面的系统。每个 UI 文件放在资源包的 `ui/` 目录下，通过 `_ui_defs.json` 注册，通过 `_global_variables.json` 定义全局变量。

**三大核心符号：**

| 符号 | 名称 | 生效时机 | 数据来源 | 用途 |
|------|------|---------|---------|------|
| `$` | 变量 | JSON 加载时（静态） | JSON 配置 | 值替换、配置传递 |
| `#` | 绑定 | 运行时（动态） | Python 代码 | 动态数据显示 |
| `@` | 继承 | JSON 加载时 | 其他控件 | 组件复用 |

---

## 二、文件结构规范

```
资源包R/
├── ui/
│   ├── _ui_defs.json          # 注册所有 UI 文件（必须）
│   ├── _global_variables.json # 全局变量定义
│   ├── xxx_common.json        # 公共组件库
│   └── xxx_screen.json        # 具体屏幕 UI
```

**`_ui_defs.json` 格式：**
```json
{
    "ui_defs": [
        "ui/xxx_common.json",
        "ui/xxx_screen.json"
    ]
}
```

**每个 UI 文件必须声明命名空间：**
```json
{
    "namespace": "my_ui",
    "my_panel": { ... }
}
```

命名规范：全小写 + 下划线，如 `shop_ui`、`player_hud`，避免中文、大写和空格。

---

## 三、基础语法

### 元素结构

```json
{
    "元素名": {
        "type": "panel",
        "size": [200, 100],
        "controls": [
            {
                "子元素名": { "type": "label", "text": "Hello" }
            }
        ]
    }
}
```

### 继承语法（@）

```json
{
    "my_button@common.base_button": {
        "size": [150, 40]
    }
}
```

跨命名空间：`命名空间.元素名`；同文件内可省略命名空间直接用 `元素名`。

### 属性覆盖规则

| 属性类型 | 覆盖行为 |
|---------|---------|
| 简单值（字符串/数字/布尔） | 完全替换 |
| 数组 | 完全替换 |
| 对象 | 合并（子+父） |

### 语法速查

| 语法 | 说明 | 示例 |
|------|------|------|
| `{}` | 对象/元素 | `{"key": "value"}` |
| `[]` | 数组 | `[1, 2, 3]` |
| `@namespace.element` | 继承引用 | `"btn@common.button": {}` |
| `$variable` | 变量 | `"$width": 100` |
| `#binding` | 数据绑定 | `"text": "#player_name"` |

---

## 四、控件类型速查

| 控件类型 | type 值 | 主要用途 |
|---------|---------|---------|
| 面板容器 | `"panel"` | 组织布局，类似 div |
| 文本标签 | `"label"` | 显示文字 |
| 图片 | `"image"` | 贴图、背景、图标 |
| 按钮 | `"button"` | 可点击交互 |
| 堆叠布局 | `"stack_panel"` | 自动排列子元素 |
| 网格 | `"grid"` | 规则网格排列 |
| 输入面板 | `"input_panel"` | 接受键盘/鼠标输入的容器 |
| 文本输入框 | `"edit_box"` | 用户输入文本 |
| 滑动条 | `"slider"` | 数值范围选择 |
| 开关 | `"toggle"` | 选中/未选中切换 |
| 滚动视图 | `"scroll_view"` | 超出范围可滚动 |
| 自定义渲染 | `"custom"` | 物品渲染器等特殊内容 |

### Panel

```json
{
    "my_panel": {
        "type": "panel",
        "size": [200, 100],
        "visible": true,
        "layer": 1,
        "clips_children": false,
        "controls": []
    }
}
```

### Label

```json
{
    "my_label": {
        "type": "label",
        "text": "显示内容",
        "color": [1.0, 1.0, 1.0],
        "font_size": "normal",
        "font_type": "smooth",
        "shadow": false,
        "localize": false
    }
}
```

`font_size`：`small` / `normal` / `large` / `extra_large`
`font_type`：`default` / `smooth` / `unicode`
颜色为 RGB 数组，每个分量 0.0~1.0。

### Image

```json
{
    "my_image": {
        "type": "image",
        "texture": "textures/ui/White",
        "color": [1.0, 0.5, 0.0],
        "alpha": 1.0,
        "nineslice_size": [4, 4, 4, 4],
        "uv": [0, 0],
        "uv_size": [16, 16]
    }
}
```

九宫格（`nineslice_size`）：`[上, 右, 下, 左]`，让图片缩放时边角不变形。

### Button

```json
{
    "my_button": {
        "type": "button",
        "default_control": "default",
        "hover_control": "hover",
        "pressed_control": "pressed",
        "locked_control": "locked",
        "button_mappings": [
            {
                "from_button_id": "button.menu_select",
                "to_button_id": "#my_btn_click",
                "mapping_type": "pressed"
            }
        ],
        "controls": [
            {"default": {"type": "image", "texture": "..."}},
            {"hover":   {"type": "image", "texture": "..."}}
        ]
    }
}
```

常用按钮 ID：`button.menu_select`（鼠标左键）、`button.menu_ok`（回车）、`button.menu_cancel`（ESC）

### Stack Panel

```json
{
    "my_stack": {
        "type": "stack_panel",
        "orientation": "vertical",
        "controls": []
    }
}
```

`orientation`：`"vertical"` 或 `"horizontal"`

---

## 五、布局系统

### 坐标系

左上角为原点，X 向右递增，Y 向下递增。

### 锚点（Anchor）

`anchor_from`：父元素的参考点；`anchor_to`：自身的对齐点。

9个锚点位置：
```
top_left      top_middle      top_right
left_middle      center      right_middle
bottom_left  bottom_middle  bottom_right
```

**常用组合：**

| 需求 | anchor_from | anchor_to |
|------|-------------|-----------|
| 居中 | `center` | `center` |
| 左上对齐 | `top_left` | `top_left` |
| 右下对齐 | `bottom_right` | `bottom_right` |
| 左侧垂直居中 | `left_middle` | `left_middle` |
| 顶部居中 | `top_middle` | `top_middle` |
| 底部居中 | `bottom_middle` | `bottom_middle` |

### 尺寸单位

| 单位 | 语法 | 说明 |
|------|------|------|
| 像素 | `100` 或 `"100px"` | 固定像素 |
| 百分比 | `"50%"` | 相对父元素百分比 |
| 子元素总尺寸 | `"100%c"` | 自动撑开至子元素总大小 |
| 最大子元素 | `"100%cm"` | 与最大子元素同尺寸 |
| 混合运算 | `"100%+-20px"` | 百分比加减像素 |
| 填充剩余 | `"fill"` | 填满剩余空间 |

### 偏移量（Offset）

```json
"offset": [X, Y]
```

正值向右/向下，负值向左/向上。支持与尺寸相同的单位。

### 常用布局模板

```json
// 全屏背景
{"size": ["100%", "100%"], "anchor_from": "center", "anchor_to": "center"}

// 居中对话框
{"size": [400, 300], "anchor_from": "center", "anchor_to": "center"}

// 顶部标题栏
{"size": ["100%", 60], "anchor_from": "top_middle", "anchor_to": "top_middle"}

// 底部按钮栏
{"size": ["100%", 60], "anchor_from": "bottom_middle", "anchor_to": "bottom_middle"}

// 右下角角标（偏移微调）
{"anchor_from": "bottom_right", "anchor_to": "bottom_right", "offset": [-10, -10]}
```

---

## 六、变量系统（$）

变量在 JSON 加载时完成静态替换，**不能在运行时改变**。

### 定义与使用

```json
{
    "my_panel": {
        "type": "panel",
        "$panel_width": 200,
        "$panel_height": 100,
        "size": ["$panel_width", "$panel_height"]
    }
}
```

### 默认值

```json
"$my_var|default": 100
```

### 变量传递

继承时通过键值对传递变量：

```json
{
    "my_instance@common.my_component": {
        "$title_text": "标题",
        "$bg_color": [0.2, 0.2, 0.2]
    }
}
```

### 变量拼接（路径拼接）

```json
"texture": "($Miao_ModUiTexturesPath + '/btn_bg')"
```

### 变量 vs 绑定

| 特性 | 变量（$） | 绑定（#） |
|------|---------|---------|
| 生效时机 | JSON 加载时 | 运行时 |
| 能否改变 | 不能 | 能（实时更新） |
| 数据来源 | JSON 配置 | Python 代码 |
| 用途 | 配置传递 | 动态数据显示 |

---

## 七、数据绑定（#）

绑定在运行时动态更新，数据由 Python 通过 `ViewBinder` 注册。

### 在 JSON 中声明绑定

```json
{
    "my_label": {
        "type": "label",
        "text": "#player_name",
        "bindings": [
            {
                "binding_name": "#player_name",
                "binding_condition": "always_when_visible"
            }
        ]
    }
}
```

`binding_condition` 常用值：
- `"always_when_visible"`：可见时每帧更新
- `"once"`：只绑定一次

### 在 Python 中注册绑定（网易版 ViewBinder）

```python
@ViewBinder.binding(ViewBinder.BF_BindString, '#player_name')
def _player_name(ui):
    return "玩家名称"

M.CreateDynamicBind(self.UInode, _player_name)
```

常用绑定类型：

| 类型常量 | 绑定说明 |
|---------|---------|
| `BF_BindString` | 字符串（label text 等） |
| `BF_BindBool` | 布尔值（visible 等） |
| `BF_BindInt` | 整数（Grid 数量等） |
| `BF_BindFloat` | 浮点数（Slider 值等） |
| `BF_ButtonClickUp` | 按钮点击事件 |
| `BF_SliderChanged \| BF_SliderFinished` | 滑动条变化 |
| `BF_ToggleChanged` | 开关状态变化 |
| `binding_collection` 装饰器 | Grid/列表集合绑定（需指定集合名） |

---

## 八、继承与复用（@）

### 组件模板模式

1. 在公共文件（如 `xxx_common.json`）定义模板，用 `$` 变量暴露可配置项
2. 在具体文件中继承并传入变量

```json
// common.json 定义模板
{
    "namespace": "common",
    "base_icon_btn": {
        "type": "button",
        "$btn_texture|default": "textures/ui/default_btn",
        "$btn_label|default": "按钮",
        "size": [100, 30],
        "controls": [
            {"bg": {"type": "image", "texture": "$btn_texture"}},
            {"label": {"type": "label", "text": "$btn_label"}}
        ]
    }
}

// screen.json 使用模板
{
    "namespace": "my_screen",
    "confirm_btn@common.base_icon_btn": {
        "$btn_texture": "textures/ui/confirm",
        "$btn_label": "确认"
    },
    "cancel_btn@common.base_icon_btn": {
        "$btn_texture": "textures/ui/cancel",
        "$btn_label": "取消"
    }
}
```

---

## 九、网易中国版特殊规范

### UI 注册与创建

```python
# 注册
clientApi.RegisterUI("ModName", "screen_name",
    "ModScripts.ClientSystem.MyUI.MyUI", "screen_namespace.main")

# 创建（isHud=1 为 HUD 层）
self.UINode = clientApi.CreateUI("ModName", "screen_name",
    {"isHud": 1, "cs": self})
```

### 动态创建子控件

```python
# 在运行时动态添加组件
self.UInode.CreateChildControl(
    'common_namespace.ComponentName',  # 来源：命名空间.组件名
    'control_name',                    # 新控件的名称
    self.UInode.GetBaseUIControl('parent/path')  # 父控件
)
```

### 获取控件并操作

```python
ctrl = self.UInode.GetBaseUIControl('panel/label')
ctrl.asLabel().SetText("新文本")
ctrl.asButton().SetButtonTouchUpCallback(self.on_click)
ctrl.SetVisible(True, False)
ctrl.SetPosition((x, y))
```

### 全局变量 + 贴图路径规范

在 `_global_variables.json` 定义路径变量，UI JSON 中通过变量引用避免硬编码：

```json
// _global_variables.json
{ "$Miao_ModUiTexturesPath": "textures/ui/my_mod" }

// UI JSON
"texture": "($Miao_ModUiTexturesPath + '/bg')"
```

---

## 十、常见错误速查

| 现象 | 根因 | 修复 |
|------|------|------|
| 控件不显示 | `visible` 为 false 或 layer 被遮挡 | 检查 visible 和 layer 值 |
| 贴图不显示 | texture 路径错误或后缀多写了 `.png` | 路径不加 `.png` 后缀 |
| 布局错位 | anchor 组合错误 | 对照锚点表重新设置 |
| 绑定不更新 | `binding_condition` 设置错误 | 改为 `always_when_visible` |
| JSON 解析失败 | 多余逗号、缺引号、使用了单引号 | 用 [JSONLint](https://jsonlint.com/) 检查 |
| 继承不生效 | 命名空间或元素名拼写错误 | 检查 `namespace.element` 引用路径 |
| 变量未替换 | 变量作用域不覆盖当前控件 | 确认变量在父控件中定义 |
| Grid 不显示内容 | 数量绑定返回 0 | 检查 Python 侧数量绑定逻辑 |
| 按钮无响应 | `button_mappings` 缺失或 `to_button_id` 未绑定 | 检查映射和 Python 绑定 |

---

---

## 十一、网易官方 UI 编辑器补充说明

> 来源：[网易我的世界开发者文档 - 界面与交互](https://mc.163.com/dev/guide.html)
> Content was rephrased for compliance with licensing restrictions.

### 文件命名限制

- UI 贴图文件名：**只支持数字、字母、下划线**，不满足则导入失败
- UI 文件名（JSON）：同样遵循上述命名规则

### UI 文件输出路径

- UI 编辑器保存后，JSON 文件输出到：`资源包/ui/` 目录
- 贴图资源放置于：`资源包/textures/ui/`

### 特殊文件（禁止修改/删除）

| 文件名 | 说明 |
|--------|------|
| `netease_editor_template_namespace.json` | 网易编辑器内置控件模板，勿改 |
| `_ui_defs.json` | 当前作品所有 UI 文件的注册表，自动维护 |

### Layer（层级）规则

- layer 值越大，控件显示越靠前（遮挡 layer 小的控件）
- 编辑器默认「自动设定层级」：控件结构中**靠下**的控件会遮挡靠上的控件
- 一旦取消「自动层级」勾选，将**无法再重新勾选**，需手动设置 `layer` 属性

### 控件路径规则

获取控件时使用路径字符串，路径为从根向下用 `/` 分隔：

```python
# 示例：root_panel/child_panel/label_name
ctrl = self.UInode.GetBaseUIControl('root_panel/child_panel/label_name')
```

### 平台判断（PC vs PE）

```python
import mod.client.extraClientApi as clientApi

# 0 = PC，非 0 = PE（手机）
if clientApi.GetPlatform() == 0:
    # PC 界面逻辑
    pass
else:
    # PE 界面逻辑
    pass
```

### 按钮三态贴图说明

Button 控件有三种贴图状态需要分别配置：

| 状态 | 说明 | 触发条件 |
|------|------|---------|
| 默认贴图 | 普通状态 | 未交互时 |
| 按下贴图 | 点击/触摸按下 | 手指/鼠标按下时 |
| 悬停贴图 | 鼠标悬浮 | 仅 PC 端有效 |

> 手机版开发时悬停贴图通常与按下贴图相同。

### 图片控件注意事项

- 默认保持图片原生宽高比，如需铺满父控件需**取消勾选「保持宽高比」**
- 勾选尺寸 XY 的「适应」可让图片铺满屏幕

### 位移方向约定

- 位移 X 正值 → 向右；负值 → 向左
- 位移 Y 正值 → 向下；负值 → 向上

---

## 十二、常用 Python API 速查（网易版）

| API | 说明 |
|-----|------|
| `clientApi.GetPlatform()` | 获取当前平台（0=PC，其他=PE） |
| `clientApi.GetTopUINode()` | 获取最顶层 UI 节点 |
| `clientApi.RegisterUI(mod, name, path, "ns.main")` | 注册 UI |
| `clientApi.CreateUI(mod, name, param)` | 创建 UI |
| `uiNode.GetBaseUIControl(path)` | 获取控件 |
| `uiNode.GetChildrenName(path)` | 获取子控件名称列表 |
| `uiNode.CreateChildControl("ns.comp", name, parent)` | 动态创建子控件 |
| `ctrl.asLabel().SetText(str)` | 设置文本 |
| `ctrl.asLabel().GetText()` | 获取文本 |
| `ctrl.asButton().SetButtonTouchUpCallback(fn)` | 设置按钮点击回调 |
| `ctrl.SetVisible(bool, anim)` | 设置控件可见性 |
| `ctrl.SetPosition((x, y))` | 设置控件位置 |
| `ctrl.GetSize()` | 获取控件尺寸 |
| `ctrl.GetGlobalPosition()` | 获取全局坐标 |
| `ctrl.StopAnimation()` | 停止动画 |
| `ctrl.PlayAnimation()` | 播放动画 |
| `uiNode.UpdateScreen()` | 强制刷新界面（触发绑定重新计算） |

---

## 十三、UI 数据绑定深度说明

> 来源：[网易官方文档 - UI数据绑定](https://mc.163.com/dev/mcmanual/mc-dev/mcguide/18-%E7%95%8C%E9%9D%A2%E4%B8%8E%E4%BA%A4%E4%BA%92/70-UI%E6%95%B0%E6%8D%AE%E7%BB%91%E5%AE%9A.html)
> Content was rephrased for compliance with licensing restrictions.

### 绑定 vs UI API 的取舍

| 方式 | 优点 | 缺点 |
|------|------|------|
| UI API（`SetText` 等） | 代码直观简单 | 性能相对较低，需手动触发 |
| 数据绑定（ViewBinder） | 性能更好，数据驱动，自动刷新 | 代码较复杂，需理解绑定机制 |

> **关键场景**：Grid/Stack_Grid 大量格子时，集合绑定性能远优于逐格调用 API。

---

### 完整绑定流程

**① JSON 侧声明绑定变量**

```json
"label0": {
    "text": "#my_text",
    "bindings": [{
        "binding_name": "#my_text",
        "binding_condition": "always_when_visible"
    }]
}
```

**② Python 侧注册绑定函数**

```python
@ViewBinder.binding(ViewBinder.BF_BindString, '#my_text')
def ReturnMyText(self):
    return self.someText  # self.someText 改变时，label 自动刷新
```

**注意**：`$` 是 JSON 层静态变量；`#` 是运行时动态绑定变量，两者不能混用。

---

### binding_condition 可选值

| 值 | 触发时机 |
|----|---------|
| `always` | 持续触发（每帧） |
| `always_when_visible` | 可见时持续触发（推荐） |
| `visible` | 变为可见时触发一次 |
| `visibility_changed` | 可见性发生变化时触发 |
| `once` | 只触发一次 |
| `none` | 不触发 |

---

### 绑定默认值（property_bag）

Python 未返回数据时使用默认值：

```json
"label0": {
    "text": "#my_text",
    "property_bag": {
        "#my_text": "默认文字"
    }
}
```

---

### binding_name_override：名称映射

当 JSON 绑定变量名与 Python 函数名不一致时，用 `binding_name_override` 桥接：

```json
"label0": {
    "text": "#abcdefg",
    "bindings": [{
        "binding_name": "#my_python_binding",       // Python 端的函数名
        "binding_name_override": "#abcdefg",        // 映射给本控件的 #abcdefg
        "binding_condition": "always_when_visible"
    }]
}
```

**内置属性**（`visible`、`alpha` 等）可直接用 `binding_name_override` 映射，无需在控件上手动写 `"visible": "#visible"`：

```json
"bindings": [{
    "binding_name": "#my_visible",
    "binding_name_override": "#visible",
    "binding_condition": "always"
}]
```

---

### 支持的绑定类型全表

| 常量 | 类型 | 说明 |
|------|------|------|
| `BF_ButtonClickUp` | binding | 按钮松开事件 |
| `BF_ButtonClickDown` | binding | 按钮按下事件 |
| `BF_ButtonClick` | binding | 同时绑定Up和Down |
| `BF_ButtonClickCancel` | binding | 按钮取消事件（按下后在外松开） |
| `BF_InteractButtonClick` | binding | 原生按钮点击事件 |
| `BF_BindBool` | binding / binding_collection | 绑定 bool |
| `BF_BindInt` | binding / binding_collection | 绑定 int |
| `BF_BindFloat` | binding / binding_collection | 绑定 float |
| `BF_BindString` | binding / binding_collection | 绑定 string |
| `BF_BindGridSize` | binding | 绑定 GridSize |
| `BF_BindColor` | binding / binding_collection | 绑定颜色 |
| `BF_EditChanged` | binding | 输入框内容变化 |
| `BF_EditFinished` | binding | 输入框输入完成 |
| `BF_ToggleChanged` | binding | 开关状态变化 |

---

### 集合绑定（binding_collection）

用于 `grid` / `stack_grid` 的多格子绑定，只需写一个函数，通过 `index` 区分不同格子。

**Python 侧：**

```python
@ViewBinder.binding_collection(ViewBinder.BF_BindString, "my_grid_collection", "#item_count_text")
def ReturnItemCount(self, index):
    return str(self.itemList[index]['count'])
```

**JSON 侧（grid定义）：**

```json
"inventory_grid": {
    "type": "grid",
    "collection_name": "my_grid_collection",
    "grid_dimensions": [9, 3],
    "grid_item_template": "namespace.item_template"
}
```

**JSON 侧（格子模板内的子控件）：**

```json
"count_label": {
    "type": "label",
    "text": "#item_count_text",
    "bindings": [{
        "binding_type": "collection",
        "binding_collection_name": "my_grid_collection",
        "binding_name": "#item_count_text",
        "binding_condition": "always_when_visible"
    }]
}
```

---

### 视图绑定（binding_type: view）

读取本控件或其他控件的变量，经过表达式计算后写入另一个属性，无需 Python 干预。

**典型用途：根据数值自动控制显隐**

```json
"durability_bar": {
    "type": "custom",
    "renderer": "progress_bar_renderer",
    "property_bag": {
        "#progress_bar_total_amount": 1.0
    },
    "bindings": [{
        "binding_type": "view",
        "source_property_name": "(#progress_bar_current_amount < 1.0)",
        "target_property_name": "#touch_progress_bar_visible"
    }]
}
```

**跨控件视图绑定**（读取兄弟/父控件的变量）：

```json
"child_control": {
    "bindings": [{
        "binding_type": "view",
        "source_control_name": "parent_panel",
        "resolve_sibling_scope": true,
        "source_property_name": "(#lock_mode = 1)",
        "target_property_name": "#visible"
    }]
}
```

> `resolve_sibling_scope: true` 时，在兄弟控件/父控件中查找 `source_control_name`；默认（false）只查找子控件。

---

### binding 对象属性速查

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `ignored` | bool | false | 是否忽略此绑定 |
| `binding_type` | enum | `global` | `global` / `view` / `collection` / `collection_details` / `none` |
| `binding_condition` | enum | `none` | 触发条件（见上表） |
| `binding_name` | string | — | Python 端绑定变量名 |
| `binding_name_override` | string | `""` | 映射到的控件属性名 |
| `binding_collection_name` | string | — | 集合绑定名（`collection` 类型必填） |
| `source_control_name` | string | `""` | 视图绑定：源控件名（`view` 类型） |
| `source_property_name` | string | — | 视图绑定：源属性名，支持表达式 |
| `target_property_name` | string | — | 视图绑定：写入目标属性名 |
| `resolve_sibling_scope` | bool | false | 是否在兄弟/父控件中查找源控件 |

---

### Toggle 控件（单选/多选分页）

**JSON 定义关键字段：**

```json
"my_toggle@common.toggle": {
    "$radio_toggle_group": true,        // true = 单选（同组只能选一个）
    "$toggle_name": "#my_group_name",   // 绑定的 toggle 组名
    "$toggle_group_default_selected": 0,// 默认选中的 index
    "$toggle_group_forced_index": 0,    // 当前 toggle 在组中的 index
    "$unchecked_control": "ns.unchecked_panel",
    "$checked_control": "ns.checked_panel",
    "$unchecked_hover_control": "ns.unchecked_panel",
    "$checked_hover_control": "ns.checked_panel"
}
```

**Python 回调：**

```python
@ViewBinder.binding(ViewBinder.BF_ToggleChanged, "#my_group_name")
def OnToggleChanged(self, args):
    index = args["index"]   # 被点击的 toggle 序号
    # 根据 index 切换显示内容
```

**Toggle 八种状态：**

| 状态 | 说明 |
|------|------|
| `unchecked` | 未选中 |
| `checked` | 选中 |
| `unchecked_hover` | 未选中 + 鼠标悬停 |
| `checked_hover` | 选中 + 鼠标悬停 |
| `unchecked_locked` | 未选中 + 锁定（不可交互） |
| `checked_locked` | 选中 + 锁定 |
| `unchecked_locked_hover` | 未选中 + 锁定 + 悬停 |
| `checked_locked_hover` | 选中 + 锁定 + 悬停 |

---

### stack_grid 动态列表

`stack_grid` = 一维 grid，支持集合绑定，适合做动态长度的列表/分页 tab。

**控制列表数量（通过 `#StackGridItemsCount`）：**

```json
"my_stack_grid": {
    "type": "stack_grid",
    "collection_name": "my_collection",
    "orientation": "vertical",
    "bindings": [{
        "binding_name": "#my_count",
        "binding_name_override": "#StackGridItemsCount",
        "binding_condition": "always"
    }],
    "property_bag": {
        "#my_count": 10
    },
    "controls": [
        {"item_template@ns.item_template": {}}
    ]
}
```

**Python 侧控制数量：**

```python
@ViewBinder.binding(ViewBinder.BF_BindInt, "#my_count")
def OnGetListCount(self):
    return len(self.myDataList)
```

**集合绑定子控件内容：**

```python
@ViewBinder.binding_collection(ViewBinder.BF_BindString, "my_collection", "#item_label_text")
def OnGetItemLabel(self, index):
    return self.myDataList[index]["name"] if index < len(self.myDataList) else ""
```

---

## 十四、控件属性动画

> 来源：[网易官方文档 - 控件属性动画](https://mc.163.com/dev/mcmanual/mc-dev/mcguide/18-%E7%95%8C%E9%9D%A2%E4%B8%8E%E4%BA%A4%E4%BA%92/19-%E6%8E%A7%E4%BB%B6%E5%B1%9E%E6%80%A7%E5%8A%A8%E7%94%BB.html)
> Content was rephrased for compliance with licensing restrictions.

### 概述

属性动画让控件的某个属性值随时间变化，从而产生动画效果。所有属性动画在界面创建后**自动播放**。

**支持动画的属性类型：**

| anim_type | 挂载属性 | 说明 |
|-----------|---------|------|
| `alpha` | `alpha` | 透明度动画（0~1） |
| `clip` | `clip_ratio` | 裁剪动画（0=不裁剪，1=完全裁剪） |
| `color` | `color` | 颜色动画（RGB 各分量 0~1） |
| `flip_book` | `uv` | 序列帧动画 |
| `uv` | `uv` | UV 坐标动画 |
| `offset` | `offset` | 位移动画 |
| `size` | `size` | 尺寸动画 |

> 目前所有可动画属性均存在于**图片控件**（`type: image`）中。

---

### JSON 写法

**方式一：直接内联**（不可复用）

```json
{
    "my_img": {
        "type": "image",
        "texture": "textures/ui/xxx",
        "alpha": {
            "anim_type": "alpha",
            "duration": 0.3,
            "from": 0.0,
            "to": 1.0
        }
    }
}
```

**方式二：外部定义后引用**（可复用，推荐）

```json
{
    "my_img": {
        "type": "image",
        "texture": "textures/ui/xxx",
        "alpha": "@show_alpha_ani"
    },
    "show_alpha_ani": {
        "anim_type": "alpha",
        "duration": 0.3,
        "from": 0.0,
        "to": 1.0
    }
}
```

---

### 通用属性

| 属性 | 说明 |
|------|------|
| `anim_type` | 动画类型，见上表 |
| `duration` | 动画持续时间（秒） |
| `from` | 起始值（控件初始化时用此值设置属性） |
| `to` | 结束值 |
| `next` | 当前片段播放完毕后接续播放的动画名（`"@动画名"` 格式） |

**用 `next` 串联多个片段（alpha 淡入→停留→淡出示例）：**

```json
{
    "my_img": {
        "type": "image",
        "texture": "textures/ui/xxx",
        "alpha": "@show_alpha_ani"
    },
    "show_alpha_ani": {
        "anim_type": "alpha", "duration": 0.3,
        "from": 0.0, "to": 1.0,
        "next": "@hold_alpha_ani"
    },
    "hold_alpha_ani": {
        "anim_type": "alpha", "duration": 1.0,
        "from": 1.0, "to": 1.0,
        "next": "@hide_alpha_ani"
    },
    "hide_alpha_ani": {
        "anim_type": "alpha", "duration": 0.3,
        "from": 1.0, "to": 0.0
    }
}
```

---

### 各动画类型详解

#### 透明度动画（alpha）

```json
{
    "anim_type": "alpha",
    "duration": 0.3,
    "from": 0.0,
    "to": 1.0
}
```

#### 裁剪动画（clip）

```json
{
    "clipImg": {
        "type": "image",
        "texture": "textures/ui/xxx",
        "clip_ratio": {
            "anim_type": "clip",
            "duration": 1.0,
            "from": 0.0,
            "to": 1.0
        }
    }
}
```

#### 颜色动画（color）

`from` / `to` 为 `[R, G, B]`，各分量取值 0~1，**不支持** alpha 值：

```json
{
    "color_ani": {
        "anim_type": "color",
        "duration": 1.0,
        "from": [1, 0, 0],
        "to": [0, 0, 1]
    }
}
```

#### 位移动画（offset）

```json
{
    "offset_ani": {
        "anim_type": "offset",
        "duration": 1.0,
        "from": [0, 0],
        "to": [0, 50]
    }
}
```

> ⚠️ `from` 和 `to` 的偏移类型必须一致（如都用像素，或都用百分比）。
> ⚠️ 有动画时，动态修改偏移请用 `SetFullPosition` **代替** `SetPosition`。

#### 尺寸动画（size）

```json
{
    "size_ani": {
        "anim_type": "size",
        "duration": 1.0,
        "from": [100, 100],
        "to": [150, 150]
    }
}
```

> ⚠️ `from` 和 `to` 的尺寸类型必须一致。
> ⚠️ 有动画时，动态修改尺寸请用 `SetFullSize` **代替** `SetSize`。

#### UV 动画（uv）

控制图片 UV 坐标的偏移，实现滚动/平移贴图效果：

```json
{
    "uv_ani": {
        "anim_type": "uv",
        "duration": 5,
        "from": [0, 0],
        "to": [2240, 0]
    }
}
```

#### 序列帧动画（flip_book）

逐帧切换图片 UV 区域实现帧动画，挂载在 `uv` 属性上：

```json
{
    "flipbookImg": {
        "type": "image",
        "texture": "textures/ui/my_sprite_sheet",
        "uv": "@flipbook_ani",
        "uv_size": [64.0, 64.0]
    },
    "flipbook_ani": {
        "anim_type": "flip_book",
        "initial_frame": 0,
        "frame_count": 36,
        "fps": 10,
        "reversible": false
    }
}
```

| 属性 | 说明 |
|------|------|
| `initial_frame` | 起始帧 index |
| `frame_count` | 序列帧总帧数 |
| `fps` | 每秒播放帧数 |
| `reversible` | `true` = 播放完后倒放回第一帧 |

> ⚠️ `uv_size` 必须与序列帧中**单帧尺寸**一致，不能为 `[0,0]`。
> ⚠️ 序列帧动画**自带循环**，`next` 后的片段会被忽略，且**不支持**手动设置循环片段数。
> ⚠️ 序列帧贴图要求每帧大小一致。

---

### 动画循环规则

- 只有**最后一个**动画片段有「循环片段」属性
- `循环片段 = 0`：不循环
- `循环片段 = N`：最后 N 段循环播放（例如 5 片段循环 3 段：A→B→C→D→E→C→D→E→…）
- 循环片段数不能超过总片段数
- **首段动画没有名称时，不能参与循环**
- 序列帧动画**不支持**此循环设置

---

### 动画控制 API（Python 侧）

| API | 说明 |
|-----|------|
| `RegisterUIAnimations(anim_dict)` | 注册动画定义（可在运行时添加新动画） |
| `UnregisterUIAnimation(anim_name)` | 取消注册动画 |
| `ctrl.PlayAnimation()` | 播放该控件的所有属性动画 |
| `ctrl.PauseAnimation()` | 暂停该控件的所有属性动画 |
| `ctrl.StopAnimation()` | 停止播放动画（重置到初始状态） |
| `ctrl.SetAnimation(prop, anim_name)` | 给单一属性设置动画 |
| `ctrl.RemoveAnimation(prop)` | 移除单一属性的动画 |
| `ctrl.SetAnimEndCallback(fn)` | 设置动画播放结束回调 |
| `ctrl.RemoveAnimEndCallback()` | 删除结束回调 |

**示例：运行时注册并播放动画**

```python
# 注册动画
self.UInode.RegisterUIAnimations({
    "fade_in": {
        "anim_type": "alpha",
        "duration": 0.5,
        "from": 0.0,
        "to": 1.0
    }
})

# 给控件属性设置动画
ctrl = self.UInode.GetBaseUIControl('panel/my_img')
ctrl.SetAnimation('alpha', 'fade_in')
ctrl.PlayAnimation()

# 设置结束回调
def on_anim_end():
    print('动画播放完毕')

ctrl.SetAnimEndCallback(on_anim_end)
```

---

### 关键注意事项

| 场景 | 错误做法 | 正确做法 |
|------|---------|---------|
| 动态修改有动画的控件尺寸 | `ctrl.SetSize(...)` | `ctrl.SetFullSize(...)` |
| 动态修改有动画的控件位置 | `ctrl.SetPosition(...)` | `ctrl.SetFullPosition(...)` |
| 序列帧贴图 uv_size | 填 `[0, 0]` | 填与单帧相同的实际尺寸 |
| 多段动画中除首段外的动画名 | 留空 | **必须有名称** |
| 同一属性动画中 | 出现重复动画名 | 每段名称必须唯一 |

---

## 十五、ModName_common 公共 UI 组件库

本项目有一套自制的公共 UI 组件库，模板文件为 `custom_warehouseR/ui/ModName_common.json`。

**重要：`ModName` 是占位符。** 生成脚本运行后会把 `ModName` 替换为你输入的模组名：
- 模板命名空间：`ModName_common` → 生成后：`{模组名}_common`（如 `myShop_common`）
- 模板文件名：`ModName_common.json` → 生成后：`{模组名}_common.json`
- Python 中通过 `CG.Ui_CommonName` 引用（值为 `{模组名}_common`），不要硬编码

因此文档中统一用 `{模组名}_common` 表示命名空间，用 `CG.Ui_CommonName` 表示 Python 引用。

**创建任何 UI 控件前，优先检查此库是否有可复用的组件**，再决定是否新建。

---

### 可用组件速查

#### 1. 按钮类

| 组件名 | 用途 | 关键变量 |
|--------|------|---------|
| `ModName_common.newbutt2` | 通用图标按钮（带贴图+文字+图标） | `$default_texture` / `$hover_texture` / `$pressed_texture` / `$label_text` / `$button_img_color` / `$icon_texture` |
| `ModName_common.newbutton` | 简单按钮（无图标） | `$default_texture` / `$label_text` / `$button_img_color` |
| `ModName_common.M_TextBtn` | 纯文字小按钮 | `$label_text` / `$label_color` |
| `ModName_common.M_CUSBOX_BTN` | 下拉选择框按钮（带箭头） | `$btn_label_text` / `$btn_you_texture` |

**`newbutt2` 完整用法：**

```json
{
    "my_btn@ModName_common.newbutt2": {
        "$default_texture": "($Miao_ModUiTexturesPath + '/set_btn_a_1')",
        "$hover_texture": "($Miao_ModUiTexturesPath + '/set_btn_a_1')",
        "$pressed_texture": "($Miao_ModUiTexturesPath + '/set_btn_b_1')",
        "$label_text": "确认",
        "$label_color": [1, 1, 1],
        "$button_img_color": [0.235, 0.522, 0.153],
        "$pressed_button_name": "#my_btn_click",
        "size": [80, 20]
    }
}
```

---

#### 2. 文字类

| 组件名 | 用途 |
|--------|------|
| `ModName_common.text` | 基础文字标签（`type: label`，layer=1） |

```json
{
    "my_text@ModName_common.text": {
        "text": "显示内容",
        "color": [1, 1, 1],
        "layer": 5
    }
}
```

---

#### 3. 滑动条

| 组件名 | 用途 | 关键变量 |
|--------|------|---------|
| `ModName_common.M_slider` | 完整滑动条（继承自 `common.slider`） | `$slider_name` / `$slider_value_binding_name` / `$slider_steps_binding_name` / `$M_slider_background_textures` / `$M_slider_button_layout_textures` |

```json
{
    "my_slider@ModName_common.M_slider": {
        "$M_slider_background_textures": "($Miao_ModUiTexturesPath + '/toum')",
        "$M_slider_button_layout_textures": "($Miao_ModUiTexturesPath + '/slider_state_1')",
        "$M_slider_button_hover_layout_textures": "($Miao_ModUiTexturesPath + '/slider_state_0')",
        "$M_slider_bar_default_background_textures": "($Miao_ModUiTexturesPath + '/toum')",
        "$slider_name": "#my_slider_value",
        "$slider_value_binding_name": "#my_slider_value",
        "$slider_steps_binding_name": "#my_slider_steps",
        "size": [120, 10]
    }
}
```

---

#### 4. 滚动视图

| 组件名 | 用途 | 关键变量 |
|--------|------|---------|
| `ModName_common.M_scroll_view` | 滚动视图（继承自 `common.scrolling_panel`） | `$scrolling_content`（内容控件路径） |

```json
{
    "my_scroll@ModName_common.M_scroll_view": {
        "$scrolling_content": "my_namespace.my_content_panel",
        "size": ["100%", 200]
    }
}
```

---

#### 5. 弹窗

| 组件名 | 用途 | Python 绑定名 |
|--------|------|--------------|
| `ModName_common.M_Popup` | 二次确认弹窗（含标题/内容/确认/取消按钮） | `#POPUP_TITLE_NAME` / `#POPUP_TEXT_NAME` / `#POPUP_TEXT_QR_BTN` / `#POPUP_TEXT_QX_BTN` / `#POPUP_TEXT_BTN_QR_0_VISIBLE` |

在 Python 中通过 `CreateChildControl` 动态创建：

```python
# 注册
self.UInode.CreateChildControl('ModName_common.M_Popup', 'M_Popup',
    self.UInode.GetBaseUIControl('root_panel'))

# 显示
self.UInode.GetBaseUIControl('root_panel/M_Popup').SetVisible(True, False)
```

---

#### 6. 数量选择器

| 组件名 | 用途 | 说明 |
|--------|------|------|
| `ModName_common.M_CountContPanel` | 数字键盘式数量输入面板 | 含滑动条 + 数字按钮 + 确认 |

Python 侧通过 `count_controls` 类管理（见 `utils.py`），绑定名：`#count_cont_gn_btn` / `#slider_value` / `#count_cont_sum_text` 等。

---

#### 7. 提示条

| 组件名 | 用途 |
|--------|------|
| `ModName_common.M_Tips_Panel` | 顶部弹出式文字提示（自动淡入淡出动画） |
| `ModName_common.M_ITEMS_TIPS_PANEL` | 底部物品悬停信息提示面板 |

```python
# 显示提示条
ctrl = uinode.GetBaseUIControl('root_panel/M_Tips_Panel')
uinode.GetBaseUIControl('root_panel/M_Tips_Panel/tips_text').asLabel().SetText("提示内容")
ctrl.SetVisible(True, False)
ctrl.StopAnimation()
ctrl.PlayAnimation()
```

---

#### 8. 下拉选择框

| 组件名 | 用途 |
|--------|------|
| `ModName_common.M_CUSBOX_PANEL` | 完整下拉选择弹窗（含 Grid 列表 + 标题 + 关闭按钮） |
| `ModName_common.M_CUSBOX_BTN` | 下拉框触发按钮 |

Python 侧通过 `CusBoxUi` 类管理（见 `utils.py`）。

---

#### 9. Toggle 开关

| 组件名 | 用途 |
|--------|------|
| `ModName_common.M_toggle` | 通用单选/多选 Toggle（带贴图） |
| `ModName_common.collection_M_toggle` | 集合绑定版 Toggle（用于 Grid/Stack_Grid） |
| `ModName_common.Text2_m_toggle_checked` / `unchecked` | 纯文字 Toggle 状态控件 |

---

#### 10. 物品渲染

| 组件名 | 用途 |
|--------|------|
| `ModName_common.M_item_renderer` | 物品图标渲染器（支持集合绑定） |
| `ModName_common.Quest_Items` | 物品格子（自动切换图标/物品渲染器） |
| `ModName_common.Quest_Gif_Items` | 带数量/颜色/按钮的物品格子 |

---

#### 11. Grid / Stack_Grid 封装

| 组件名 | 用途 | 关键变量 |
|--------|------|---------|
| `ModName_common._Grid` | 封装后的 Grid | `$Grid_Collection_Name` / `$Grid_Count` / `$Grid_Item_Template` |
| `ModName_common._Stack_Grid` | 封装后的 Stack_Grid | 同上 + `$Stack_Grid_Orientation` |
| `ModName_common._Grid_Panel` | 自动切换 Grid/Stack_Grid 的容器 | `$is_stack_grid`（true=Stack_Grid） |
| `ModName_common.M_Scroll_View_Grid_Panel` | 带滚动视图的 Grid 容器 | 同上 |

---

#### 12. 背景/工具类

| 组件名 | 用途 |
|--------|------|
| `ModName_common.BG` | 全屏背景渲染器（`background_renderer`） |
| `ModName_common.Help_pass` | 带背景图的行文字（可配色） |
| `ModName_common.M_edit_box` | 预配置好的文本输入框 |

---

### 使用原则

1. **优先复用**：创建按钮先看 `newbutt2`，创建滑动条先看 `M_slider`，创建弹窗先看 `M_Popup`
2. **继承覆盖**：使用 `@ModName_common.组件名` 继承，只传入需要修改的 `$变量`，其余保持默认
3. **贴图路径**：所有贴图使用 `"($Miao_ModUiTexturesPath + '/贴图名')"` 格式，不硬编码
4. **Python 侧工具类**：`M_Popup`、`M_CUSBOX_PANEL`、`M_CountContPanel`、滚动视图等复杂组件已在 `utils.py` 中封装为 `Popup`、`CusBoxUi`、`count_controls` 类，直接调用即可，不需要重复绑定逻辑

# JsonUI 实战陷阱与最佳实践（深度补充）

> 本次开发踩坑后总结，请合并到 `c:\Users\cat\.kiro\steering\minecraft_jsonui.md` 的末尾（作为新章节十六）。
> 部分内容超出官方文档范围，按"问题 + 正确写法"成对列出。

---

## 16.1 Collection 内按钮如何拿到 index（最大坑）

**场景**：grid/stack_grid 内每行有按钮，点击需要知道是第几行。

**正确做法**：

JSON 端 — 让 button 通过 `collection_details` 类型 binding 继承所属 collection 的上下文：

```json
"my_btn@common.newbutt2": {
    "$pressed_button_name": "#row_action_btn",
    "bindings": [
        {
            "binding_collection_name": "my_collection",
            "binding_type": "collection_details",
            "binding_condition": "always_when_visible"
        }
    ]
}
```

注意：
- `binding_type` 必须是 **`"collection_details"`**，不是 `"collection"`
- 这条 binding **没有** `binding_name`（不是数据 binding，只为传递 collection 上下文）

Python 端 — 用普通 `@ViewBinder.binding`（**不是** `binding_collection`），从 args 取 **`#collection_index`**（带 `#` 前缀！）：

```python
@ViewBinder.binding(ViewBinder.BF_ButtonClickUp, '#row_action_btn')
def row_action_btn(self, args):
    index = args.get('#collection_index', -1)   # ← 带 # 前缀
```

**典型错误**：

| 错误 | 后果 |
|------|------|
| `binding_type: "collection"` | 按钮可能被 collection 隔离但 args 不带 index |
| Python 用 `@binding_collection` 装饰 button | 按钮事件不触发 |
| 取 `args['index']` | 总是 -1 |
| 自造 `$pressed_button_binding_type` 之类 newbutt2 不识别的变量 | 完全不生效，不报错 |

---

## 16.2 Toggle 回调 args 字段名

| 类型 | 字段 | 含义 |
|------|------|------|
| 普通 toggle | `args['state']` | bool，是否选中（**不是** `'isOn'`）|
| collection 内 toggle | `args['index']` | int，下标（**不带 `#`**）|
| collection 内 toggle | `args['state']` | 选中态 |

**特别注意**：collection 内 button 的 index 在 `args['#collection_index']`（带 `#`），collection 内 toggle 的 index 在 `args['index']`（不带 `#`）。两者不同。

---

## 16.3 Grid / Stack_Grid 行数动态绑定（`$Grid_Count`）

**痛点**：grid 默认按 `grid_dimensions` 静态显示固定行数；stack_grid 默认按 `#StackGridItemsCount` 静态值显示。Python 改了数据后行数不更新。

**正确做法**：使用项目封装的公共组件，传 `$Grid_Count` 变量：

```json
"my_grid@common.M_Scroll_View_Grid_Panel": {
    "$Grid_Collection_Name": "my_coll",
    "$Grid_Items_Maximum": 36,
    "$Grid_Count": "#my_count",
    "$is_stack_grid": true,
    "$Stack_Grid_Orientation": "vertical"
}
```

```python
@ViewBinder.binding(ViewBinder.BF_BindInt, '#my_count')
def my_count(self):
    return len(self.my_data_list)
```

公共组件内部会把 `$Grid_Count` 自动绑到：
- 普通 grid 的 `#maximum_grid_items`
- stack_grid 的 `#StackGridItemsCount`

---

## 16.4 Binding 在 visible 切换后的缓存坑

**症状**：弹窗第一次打开正常，关闭后再打开变成空白或显示旧数据。

**根因**：`always_when_visible` 在 visible:false 时停止 binding。再次 visible:true 时引擎可能：
- 先用 cache 渲染一帧
- grid 的 `#StackGridItemsCount` 已设定后不会立即重拉

**修复**（按优先级）：

1. JSON 把驱动 grid 数量的 binding 改成 `"always"`（每帧都算）：
   ```json
   "$Grid_Binding_Condition": "always"
   ```

2. Python 打开弹窗时显式 forceUpdate：
   ```python
   try:
       self.UpdateScreen(True)
   except TypeError:
       self.UpdateScreen()  # 兼容老版本
   ```

3. 数据准备完毕后再 SetVisible(True)。

---

## 16.5 ScreenNode 不能直接用 `clientApi.ListenForEvent`

**错误写法**：
```python
class MyScreen(ScreenNode):
    def Create(self):
        clientApi.ListenForEvent(...)   # ← AttributeError!
```

`ListenForEvent` 是 `ClientSystem` 的实例方法，`clientApi` 模块没有。

**正确写法**：通过持有的 client system 调：
```python
class MyScreen(ScreenNode):
    def __init__(self, namespace, name, param):
        self.mclienSystem = param["cs"]
    def Create(self):
        self.mclienSystem.ListenForEvent(
            clientApi.GetEngineNamespace(),
            clientApi.GetEngineSystemName(),
            "InventoryItemChangedClientEvent",
            self,
            self.OnInventoryItemChanged
        )
```

`UnListenForEvent` 同理。

---

## 16.6 公共组件子控件必须先 Register

**症状**：调 `ShowTipsPanel(text)` → `'NoneType' object has no attribute 'asLabel'`

**根因**：`M_Tips_Panel` / `M_Popup` / `M_ITEMS_TIPS_PANEL` / `M_CountContPanel` 等公共组件不会自动出现，需要在 ScreenNode `Create()` 里先 register：

```python
def Create(self):
    self.mclienSystem.RegisterContPanel(self, self.base_paths)        # M_CountContPanel
    self.mclienSystem.ResiPopup(self, self.base_paths)                # M_Popup
    self.mclienSystem.RegisterTipsPanel(self, self.base_paths)        # M_Tips_Panel
    self.mclienSystem.RegisterItemsTipsPanel(self, self.base_paths)   # M_ITEMS_TIPS_PANEL
```

每个 register 内部检查 `if 'M_xxx' not in uinode.GetChildrenName(...)` 防重复。

---

## 16.7 物品合并 key 必须三段拼接

`miao_lid.make_nbt_hash` **只 hash userData 字典**，不含 `newItemName` / `newAuxValue`！

```python
def make_nbt_hash(itemDict, isuserdata=False):
    if not isuserdata:
        userData = itemDict.get('userData')
        if not userData:
            return None
    return hashlib.md5(repr(normalize(userData))).hexdigest()
```

如果只用它当 key，会把 `钻石(name=diamond, userData={})` 和 `铁锭(name=iron, userData={})` 当成同一物品（都返回 `None`）。

**正确合并 key**：
```python
def make_combine_key(item_dict):
    name = item_dict.get('newItemName', '')
    aux = item_dict.get('newAuxValue', 0)
    user_hash = make_nbt_hash(item_dict) or 'none'
    return '%s#%d#%s' % (name, int(aux or 0), user_hash)
```

---

## 16.8 取出物品的三段兜底（防丢失）

`SpawnItemToPlayerInv` 在背包满时返回 `False`，原始物品**可能丢失**。

**安全模式**（仓库类 mod 推荐）：

```
1. 仓库扣减 (WL.take_item)
2. 尝试 SpawnItemToPlayerInv(item, playerid, -1) 进背包
3. 失败 → CreateEngineItemEntity(item, dim, pos) 在玩家脚下生成掉落物
4. 都失败 → WL.put_item(wh, item, count) 回滚仓库
```

注意：
- **不存在 `SpawnItemToLevel` API**（容易拼错）
- 正确"在世界生成物品实体"接口是 **`serverApi.CreateEngineItemEntity(itemDict, dim, pos)`**，返回实体 id

---

## 16.9 ExtraData 节流保存模式

避免每次小操作都立即落盘（性能差），但又要保证数据不丢失。

**标准模式**：
```python
class DataMgr:
    def __init__(self):
        self.data = compdata.GetExtraData('xx_key') or {}
        self._dirty_at = None
        CF.CreateGame(LevelID).AddRepeatedTimer(1.0, self._SaveTick)

    def MarkDirty(self):
        if self._dirty_at is None:
            self._dirty_at = time.time()

    def _SaveTick(self):
        if self._dirty_at and time.time() - self._dirty_at >= 5.0:
            compdata.SetExtraData('xx_key', self.data, False)  # 不立即落盘
            compdata.SaveExtraData()                            # 真正写入磁盘
            self._dirty_at = None

    def FlushSave(self):
        """玩家离线/服务器关闭时强制立即保存"""
        if self._dirty_at:
            self._SaveTick()
            self._dirty_at = None
```

**关键点**：
- `SetExtraData(key, value, autoSave=False)` 不立即落盘
- `SaveExtraData()` 真正写入磁盘
- 监听 `DelServerPlayerEvent` → `FlushSave()` 防玩家离线丢数据

---

## 16.10 多选 + Toggle 选中态视觉

让 grid 内格子显示"已选中"状态：

```python
self.selected_keys = set()  # 选中集合

@ViewBinder.binding_collection(ViewBinder.BF_BindBool, 'my_grid', '#xxx_toggle_state_nr')
def xxx_toggle_state_nr(self, index):
    cell = self._GetItem(index)
    return cell and cell['key'] in self.selected_keys
```

切换选中：toggle 回调里加入/移除 `selected_keys`，UI 自动刷新。

---

## 16.11 数量选择器默认值

`utils.count_controls.Open(maxs, back, default=None)` 中 `default` 参数：
- 不传 / `None` → 默认值 = `maxs`（多数情况想要最大）
- 传具体值 → 钳制到 `[1, maxs]`

**典型用法**：
```python
self.OpenContPanel(item.count, back)                       # 默认最大
self.OpenContPanel(MAX_SLOT, back, default=DEFAULT_SLOT)   # 显式指定默认
```

---

## 16.12 大数字显示（K/M 简写）

`miao_lid.format_game_number(num)` 自动按区间简写：

| 输入 | 输出 |
|------|------|
| 0~999 | 原样 |
| 1000~999999 | `1K` ~ `999.9K` |
| 1000000~999999999 | `1M` ~ `999.9M` |
| ≥ 10亿 | `1B` ~ `nB` |

UI 中显示物品数量、金币等大数时统一使用，避免 label 被超长数字撑爆。

---

## 16.13 客户端 / 服务端通信框架（TS / TC + lx 路由）

适合中等复杂度 mod 的请求-响应模式：

**客户端 → 服务端**（`TS`）：
```python
def TS(self, data, back=None, eventsuid=''):
    """data 必含 'lx' 字段，对应服务端 AnyEvent.lx 同名方法"""
```

**服务端 AnyEvent 主路由**（按 lx 派发）：
```python
def AnyEvent(self, args):
    data = args['data']
    handler = getattr(self, data['lx'], None)
    if handler:
        try:
            backdata = handler(playerid, data)
        except Exception as e:
            print '[lx 处理异常]', e
            backdata = {'state': False, 'msg': '服务端异常'}
    else:
        backdata = {'state': False, 'msg': '未知请求类型'}
    if args.get('back'):
        self._Mser.NotifyToClient(playerid, 'AnyEvent',
            {'back': args['back'], 'backdata': backdata})
```

**约定**：所有响应必含 `state: bool`，失败附 `msg: str`，主路由 try/except 兜底。

---

## 16.14 ScreenNode 状态跨 UI 实例保持

**痛点**：ScreenNode 每次 `PushScreen` 都重建实例，UI 内部状态丢失。

**解决**：把跨实例状态放到 ClientSystem 上：
```python
# ClientSystem.__init__
self.warehouse_mode = 0   # 0=查看 1=转移

# ScreenNode.__init__
self.current_mode = getattr(self.mclienSystem, 'warehouse_mode', 0)

# ScreenNode 切换时
def OnModeToggle(self, args):
    self.current_mode = ...
    self.mclienSystem.warehouse_mode = self.current_mode  # 写回
```

**作用范围**：游戏会话内有效（玩家退出再进会重置）。需要持久化用 `compConfigClient.SetConfigData()`。

---

## 16.15 ToggleFilter 与 toggle 状态自动复位

`ViewBinder.ToggleFilter | BF_ToggleChanged` 表示**只在状态变 ON 时触发**回调（变 OFF 不触发）。

如果想要"点击格子触发一次操作但不希望保留选中状态"，让 toggle_state binding 永远返回 False：

```python
@ViewBinder.binding_collection(ViewBinder.BF_BindBool, 'xxx', '#toggle_state')
def toggle_state(self, index):
    return False    # 永远返回 OFF
```

效果：每次点击 OFF→ON（触发回调）→ 下一帧 binding 把状态拉回 OFF。视觉上可能闪一帧"checked"，无功能问题。

---

## 16.16 常见 args 字段速查

| 事件类型 | args 关键字段 |
|---------|------------|
| `BF_ButtonClickUp`（普通按钮） | `args['ButtonPath']` |
| `BF_ButtonClickUp`（collection 内按钮） | `args['#collection_index']`（带 `#` 前缀！）|
| `BF_ToggleChanged`（普通 toggle） | `args['state']` |
| `BF_ToggleChanged`（collection 内 toggle） | `args['index']`（不带 `#`）+ `args['state']` |
| `InventoryItemChangedClientEvent` | `args['playerId']`, `args['slot']`, `args['oldItemDict']`, `args['newItemDict']` |
| `AddServerPlayerEvent` | `args['id']`, `args['uid']`, `args['isReconnect']` |

---

## 16.17 网易 ModSDK 易混淆 API

| 错误名 | 正确名 | 说明 |
|--------|--------|------|
| `SpawnItemToLevel` | `serverApi.CreateEngineItemEntity(itemDict, dim, pos)` | 在世界生成掉落物实体 |
| `clientApi.ListenForEvent` | ClientSystem 实例方法 | 必须 `self.mclienSystem.ListenForEvent` |
| `args['index']`（button）| `args['#collection_index']` | collection 内按钮取 index 必须带 `#` |
| `args['isOn']` | `args['state']` | toggle 选中态字段名 |

---

## 16.18 闭包按 key 重定位（防异步并发）

弹窗回调过程中，列表数据可能被其他操作改动（如用户在等数量框时点了 [×] 删除其他行），导致 index 失效。

**正确做法**：闭包捕获 key（不变身份标识），回调时按 key 在最新列表里重定位 index：

```python
def _OnRowEditClick(self, index):
    cell = self._GetRow(index)
    captured_key = cell['key']   # 闭包捕获不变 ID
    def on_count(c):
        # 不能直接用 captured_index，因为期间列表可能改动
        target_idx = -1
        for i, b in enumerate(self.batch_list):
            if b['key'] == captured_key:
                target_idx = i
                break
        if target_idx >= 0:
            self.batch_list[target_idx]['count'] = c
    self.mclienSystem.OpenContPanel(max_cnt, on_count)
```

---

## 16.19 `binding_type: "collection_details"` 与 `"collection"` 的区别

| 类型 | 用途 | 是否需要 binding_name |
|------|------|---------------------|
| `"collection"` | 数据绑定（如 BindString/BindInt 取 collection 内某行的属性值）| 必填 |
| `"collection_details"` | 仅传递 collection 上下文（让控件知道自己处于哪个 collection、哪一行）| 不填 |

`collection_details` 主要给**按钮事件**用：让按钮触发的 button event 在 args 里携带 `#collection_index`，告诉 Python 是第几行。

---

## 16.20 完整的 row 模板示例（实战参考）

带物品图标 + 名字 + 各种数量调整按钮的标准行模板：

```json
"my_row": {
    "type": "panel",
    "size": ["100%+0px", 22.0],
    "layer": 1,
    "controls": [
        // 物品图标（M_item_renderer 接收 collection 内的 id_aux 等）
        {
            "icon@common.M_item_renderer": {
                "$items_info_collection_name": "my_coll",
                "$items_id_aux_name": "#row_id_aux",
                "$items_custom_color_name": "#row_color",
                "$items_trim_materialr_name": "#row_trim",
                "anchor_from": "left_middle",
                "anchor_to": "left_middle",
                "offset": [2, 0],
                "size": [18, 18]
            }
        },
        // 物品名（collection binding）
        {
            "name_text@common.text": {
                "anchor_from": "left_middle",
                "anchor_to": "left_middle",
                "offset": [24, 0],
                "bindings": [{
                    "binding_collection_name": "my_coll",
                    "binding_name": "#row_name_text",
                    "binding_type": "collection",
                    "binding_condition": "always_when_visible"
                }],
                "text": "#row_name_text"
            }
        },
        // 行内按钮（newbutt2 + collection_details）
        {
            "action_btn@common.newbutt2": {
                "$label_text": "改",
                "$pressed_button_name": "#row_action_btn",
                "anchor_from": "right_middle",
                "anchor_to": "right_middle",
                "offset": [-2, 0],
                "size": [18, 14],
                "bindings": [{
                    "binding_collection_name": "my_coll",
                    "binding_type": "collection_details",
                    "binding_condition": "always_when_visible"
                }]
            }
        }
    ]
}
```

Python 端：
```python
@ViewBinder.binding_collection(BF_BindString, 'my_coll', '#row_name_text')
def row_name_text(self, index):
    return self.my_list[index]['name']

@ViewBinder.binding(BF_ButtonClickUp, '#row_action_btn')
def row_action_btn(self, args):
    index = args.get('#collection_index', -1)   # 关键
    # 操作 self.my_list[index]
```
