# 公共 SliderControl

2026-09-13 核对：ClientSystem 的 `API_RegisterSliderControl` 和完整用例、`utils.py` 的 `SliderControl`、公共 JSON 的 `M_slider`。通过前置系统调用，不在业务端复制滑块换算与 EditBox 同步逻辑。

## 注册与绑定

`API_RegisterSliderControl(ui_node, slider_id, options=None, **kwargs)` 在 **PushScreen 的 ScreenNode.Create()** 调用。kwargs 覆盖 options；相同 ID 复用控制器并更新配置。失败返回 None，查找用 `API_GetSliderControl(ui_node, slider_id)`。

slider_id 只含字母、数字、下划线，不能以数字开头；规范化为大写，同屏唯一。用 `API_GetSliderBindingNames(slider_id)` 取得名称，不复用默认 `#slider_value` / `#slider_steps`。只改事件名不能隔离数值和步数绑定；调色板已使用独立的 `#RCM_SDK_PALETTE_SLIDER_VALUE` / `#RCM_SDK_PALETTE_SLIDER_STEPS`。

ID 为 `NPC_ALPHA` 时，JSON 实例可按源码写成：

```json
{
  "alpha_slider@DAGUOMIAO_API_MOD_common.M_slider": {
    "$slider_name": "#M_SLIDER_NPC_ALPHA_STATE",
    "$slider_value_binding_name": "#M_SLIDER_NPC_ALPHA_VALUE",
    "$slider_steps_binding_name": "#M_SLIDER_NPC_ALPHA_STEPS",
    "$slider_binding_condition": "none",
    "$slider_steps_binding_condition": "none",
    "$slider_enabled_binding_type": "global",
    "$slider_enabled_binding_condition": "none",
    "$slider_enabled_binding_name": "#M_SLIDER_NPC_ALPHA_ENABLED"
  }
}
```

显示文字绑定为 `#M_SLIDER_NPC_ALPHA_TEXT`；整个实例显隐需显式将 `#M_SLIDER_NPC_ALPHA_VISIBLE` 映射到 `#visible`。绑定条件按控制器源码用例使用 `none`，不能机械改成 `always`。

配套 `M_edit_box` 使用 `$text_box_name: #M_SLIDER_NPC_ALPHA_EDIT_CHANGED` 与 `$text_edit_box_content_binding_name: #M_SLIDER_NPC_ALPHA_EDIT_TEXT`。控制器在输入中保留原始文本，结束输入再规范化；不要在每次输入时强制 SetText，破坏空值或 `0.x` 的输入过程。

## 业务值与引擎刻度

| 参数 | 契约 |
|---|---|
| min_value / max_value | 业务数值范围，max_value 必须大于 min_value |
| value / default_value | 当前值 / Reset 使用的默认值 |
| value_type | float 或 int |
| step / precision | 业务吸附步进及精度；未指定 precision 时按 step 推导 |
| engine_steps | 默认 1，最大 1000；大于 1 使用固定格并增加分隔线控件。连续值保持 1，由 step 吸附 |
| unit / text_format / formatter | text_format 支持 `{value}`、`{unit}`、`{raw}`；formatter(value) 优先 |
| on_changed(value) | 拖动或有效编辑，适合实时预览 |
| on_finished(value) | 松手或结束编辑，适合保存和网络同步 |
| enabled / visible | 控制 ENABLED / VISIBLE 绑定；visible 需 JSON 消费对应绑定 |

`GetValue()` 返回业务值。`SetValue(value)` 默认不触发业务回调；`SetValue(value, True, True)` 触发 changed/finished。另有 `Reset`、`SetRange`、`SetEnabled`、`SetVisible`、`SetCallbacks`、`SetFormatter`、`GetBindingNames`，完整签名查实现。

CreateUI/HUD 不能照搬 PushScreen 的 Create 动态绑定流程，应在类注册前声明静态绑定。不要声称此控制器已自动解决 HUD 注册问题。验证时覆盖拖动、结束输入、外部 SetValue、Reset、禁用以及与调色板/数量面板同屏共存；静态检查不代替游戏验证。
