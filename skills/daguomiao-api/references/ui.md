# 公共 UI 接入

源码定位见上级 SKILL.md。下列客户端方法均在前置 ClientSystem 中；具体回调和 options 继续查对应函数及 `utils.py` 实现。

## 能力选择

| 需求 | 优先入口 | 注意点 |
|---|---|---|
| 通用选项面板 | `API_RegisterCusBoxPanel` / `API_OpenCusBoxPanel` | 在 `ScreenNode.Create()` 注册，点击时打开 |
| 旧按钮选择框 | `ResiCusBoxUi` | 保留 boxpath 和 mode 两种调用；二者都有时 boxpath 优先 |
| 一级折叠分组列表 | `API_RegisterGroupedList` / `API_GetGroupedList` | 多实例使用唯一 list_id |
| 确认弹窗 | `ResiPopup` / `OpenPopup` | 后者通过当前顶层 Screen 找控制器 |
| 数量、颜色 | `RegisterContPanel` / `OpenContPanel`、`RegisterColorPicker` / `OpenColorPicker` | 先注册再打开，查返回控制器是否有效 |
| 物品选择或预览 | `RegisterItemPicker` / `OpenItemPicker` | 核对清空、NBT 和返还背包的语义 |
| 提示与物品提示 | `RegisterTipsPanel` / `ShowTipsPanel`、`RegisterItemsTipsPanel` / `ShowItemsTipsPanel` | 复用已有提示与 RPG 联动逻辑 |
| 顶部货币 | `RegisterTopEcoList` | 处理可选经济模组缺失 |
| 实体选择 | `ContAllEntityCusBoxList` + 公共 CusBox | `API_RegisterEntityPicker` / `API_OpenEntityPicker` 已弃用，新功能不用 |
| 事件编辑 | `API_OpenEventEditor` | 先核对签名与回调格式 |
| 数值滑块与输入框联动 | `API_RegisterSliderControl` | 见 [独立滑块](slider.md)，不要共用默认值/步数绑定 |
| 八槽选轮 | `API_RegisterSelectionWheel` / `API_OpenSelectionWheel` | 见 [选轮与资源目录](selectors.md)，区分嵌入和独立屏幕 |
| 贴图/音效选择 | `API_RegisterAssetProvider` / `API_OpenAssetSelector` | 见 [资源注册](selectors.md)，回调有三个参数 |
| 模组配置入口 | `API_RegisterModSettings` / `API_RegisterModSetting` | 注册到奇异宝典；不是服务端 GlobalConfig |
| 效果目录 | `ContAllEffectCusBoxList` | 标准 Effect 与自定义 Buff 合并；配合 CusBox 效果模式 |
| 键盘按键目录 | `API_GetKeyboardKeyOptions` / `API_GetKeyboardKeyName` / `API_GetKeyboardKeyCode` / `API_GetKeyboardKeyMap` | 从公共入口取得名称与键码，具体筛选参数查源码 |

## 注册与资源

前置公共 namespace 为 `DAGUOMIAO_API_MOD_common`。依赖此前置的界面可直接继承其控件及引用其真实贴图，不要为了满足业务 namespace 的旧模板规则复制整套资源。确认行为包与资源包均已加载，业务 screen 本身仍须正确注册。

PushScreen 的动态绑定在 `ScreenNode.Create()` 阶段注册。不要在第一次按钮点击时才创建 CusBox 绑定。`API_RegisterCusBoxPanel(ui_node, create_path, callback=None, force_update=True, dynamic_create=True)` 每个 Screen 复用一个公共面板。

`API_OpenCusBoxPanel(ui_node, create_path, data_list, callback=None, title='请选择', selected_value=None, effect_config=None)` 的选项为 `[[显示名, 业务值, 可选图标路径, 可选分类], ...]`。普通模式回调接收完整选项列表，预选按第二个元素匹配。未注册、空列表或无有效项目时返回 `False`。

`effect_config` 传 dict 时进入效果设置模式，可设置 `time`、`level`、`time_min`、`time_max`、`level_min`、`level_max`。选择后还需在设置区确认，回调改为含 `item`、`value`、`time`、`level` 的 dict；取消设置或关闭公共面板不回调。不要用普通模式的列表下标读取此结果。效果目录可用 `ContAllEffectCusBoxList(callback, force_refresh=False)`，自定义 Buff 变化可调用 `API_InvalidateCustomBuffCache()`；异步返回后先检查界面仍有效且是当前顶层。

部分注册方法支持 `dynamic_create=False`，只绑定 JsonUI 预置控件；不要把“弹窗必须动态创建”作为普遍要求。应逐个确认目标方法签名、控件名称与层级，不能把该参数传给所有方法。注册失败返回 `None` 时处理失败，避免后续调用空控制器。

注册返回值并不统一：例如 `RegisterTipsPanel` 返回 bool，不是控制器。`ShowTipsPanel` 在原版 `hud_screen` 为顶层时自动使用全局 HUD 提示，HUD 重建后可重新挂载；其他界面继续走注册面板。`isdisp=True` 延迟 0.5 秒显示，真正显示时由前置播放统一提示音。不要再复制旧的“只查 GetTopUINode 上 __TipsPanel__”实现。

## 分组列表

- `API_RegisterGroupedList(ui_node, create_path, item_callback=None, options=None)` 的可选配置使用 options 字典。查 `GroupedCollapseList.NormalizeOptions` 与类内默认值，避免猜字段。
- 默认实例使用 `M_GROUPED_LIST`；自定义实例参考公共 JSON 的 `M_GROUPED_LIST_INSTANCE`。JsonUI 的 `$M_GROUPED_LIST_ID` 与 Python `options['list_id']` 一致，每屏唯一，仅使用英文字母、数字、下划线。
- 查 `utils.py` 的多实例用例确认实际挂载层级，不能把实例包装层误作内部列表路径。
- 自定义 list_id 按 `utils.py` 用例在 RegisterUI/PushScreen 或 CreateUI 创建 ScreenNode 前调用 `API_PrepareGroupedListScreen(screen_class, list_ids)`，随后在 `Create()` 注册控制器；默认实例不需要 Prepare。该准备接口没有创建控制器或填充数据。
- `SetData()` 深拷贝输入；仅修改外部 dict 不会自动刷新。数据格式、字段映射和点击回调以 `SetData` 及源码用例为准。
- 多列表同帧填充可用 `API_BeginGroupedListBatch(ui_node)` 与 `API_EndGroupedListBatch(ui_node, refresh=True)` 合并刷新，用 `try/finally` 配对结束。按需延迟页面内容初始化时仍保证动态绑定及时注册。

## 物品与实体

`OpenItemPicker(bbtype=0, back=None, save_nbt=False, lock_mode=False, options=None)` 普通物品回调包含 `count`、`newItemName`、`newAuxValue`、`showInHand`、`userData`。不要因来源或预览模式不同假定字段集合不同。

`options['view_mode']` 是单物品预览布局；`source_item` 可传物品 dict 或 RPG 的 `r(...)` 引用。预览模式不强制保存 NBT，继续核对 `save_nbt` / `force_save_nbt`。清空后确认可回调 `None`，不要当成选择器未响应。

返还背包默认由服务端核验真实玩家的 OP 权限；`allow_return=False` 可禁用，`return_callback(request, finish)` 可接管业务。业务接管时也必须验证权限和物品来源。

实体数据通过 `ContAllEntityCusBoxList(callback)` 获取并交给已注册的公共选择框；检查异步回复时界面是否仍有效，使用前置缓存而非每次开框重新遍历。

## 迁移已有界面

先记录“旧功能 → 旧路径/绑定 → 新控件 → 回调 → 保存字段”，保留原有清空、取消、默认值和权限行为。不能仅按新控件名字推断功能；语义或功能缺口无法由源码确定时询问用户。

迁移完成检查旧路径、孤立控件和旧回调引用，再清理确认无用的部分。验证首次打开、关闭重开、切页、确认/取消与保存回读；性能测试分别测首次和重复操作，静态解析不能证明打开流畅。
