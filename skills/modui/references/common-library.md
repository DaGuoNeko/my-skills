# ModName_common 公共 UI 组件库（业务模组模板）


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
