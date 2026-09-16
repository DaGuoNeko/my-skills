# 选轮、资源目录与配置入口

2026-09-16 对照前置 HEAD `a46991e` 与本地工作树。入口在 ClientSystem；进一步按需读 `selection_wheel_control.py`、`selection_wheel_screen.py`、`asset_registry.py`、`asset_selector_screen.py`、`config_book_registry.py`，不要默认都在 utils.py。

## 公共八槽选轮

- 独立打开：`API_OpenSelectionWheel(items, callback=None, options=None)`，返回 ScreenNode 或 False，无需业务 JSON。已有未关闭公共选轮时更新数据复用；独立界面的 wheel_id 固定为 `PUBLIC_FULLSCREEN`。
- 嵌入宿主：`API_RegisterSelectionWheel(ui_node, create_path, items=None, callback=None, options=None)`，返回控制器或 None。宿主实例继承 `DAGUOMIAO_API_MOD_common.M_SELECTION_WHEEL`，create_path 指向该控件本身，和分组列表的父挂载点用法不同。
- options.wheel_id 与 JSON `$M_SELECTION_WHEEL_ID` 一致，同屏唯一。合法字符是字母、数字、下划线，非法 ID 会退回 DEFAULT，容易意外撞名；同 ID 不同路径注册失败。
- 最多八项，超出部分截断，缺项或非 dict 项是空槽。条目可含 id/name/icon 及业务字段；选择回调为 `(item, index)`，槽位为 0–7。中心或无选中为 -1。
- 控制器 options 包含 center_text、empty_name、empty_icon、empty_tip、allow_empty、initial_index、on_cancel、on_hover。中心取消回调无参数，悬浮回调为 `(item, index)`；允许空槽时选择回调可能收到 None。
- 可用 SetItems、SetCallback、SetCurrentIndex、GetCurrentIndex、ConfirmSelection 等控制器方法。嵌入式控件的选择不等于关闭宿主；独立屏幕负责自身关闭及数据复用。按源码核对 Update 中的 PollSelection 和关闭流程，不直接操纵内部 wheel 子控件模拟确认。

选轮分支与虚拟工具已进入提交历史：branch/children 提供分支导航，中心在分支内返回、根级关闭，显式点击才进入分支。双端注册、工具状态及服务端校验见 [虚拟工具](virtual-tools.md)。普通八槽选择无需注册工具。当前仍有后续工作树改动，接入时核对实际发布文件。

## 贴图与音效注册

`API_RegisterAssetProvider(provider_id, provider_name, assets)` 替换本客户端会话中该 provider 的全部资源；`API_RegisterAsset` 更新单项。批量注册会跳过无效项并返回 `(True, 提示)`，即使成功也需检查是否有被忽略项，不能理解为全量校验失败就保留旧表。

资源为 dict：至少包含 `id`、`type`（texture/sound）及对应的 `texture` 完整路径或 `sound` 事件名；可提供 name、category_id、category_name、search_tags。category_id 缺失时从分类名取得，完整 resource_id 为 `provider_id:type:category_id:asset_id`。`API_ResolveAsset` 支持完整 ID 或简短 provider_id:asset_id；短 ID 可能歧义，核对解析结果，分类改名也可能影响完整 ID。

业务客户端监听前置 namespace/system 下的 `AssetSelectorRegisterRequest`，收到后直接调用注册 API；`API_RequestAssetRegistration(reason='manual')` 负责广播，不要在响应中再次广播造成循环。热重载时重新发布，注册表不等于磁盘资源扫描，也不提供自动持久化。

## 打开资源选择器

`API_OpenAssetSelector(callback=None, options=None)` 返回 ScreenNode 或 False，`API_GetAssetSelector()` 获取当前未关闭节点。

普通回调：`callback(resource_path, resource_id, asset_id)`；多选回调：`multi_select_callback(resource_path, resource_id, asset_id, selected)`。resource_path 是实际贴图路径或音效事件名，不能与业务 value、资源 ID 混用。贴图可注册同签名 preview_callback；音效由前置试听。

options 按需要选择：

- `types` 限制 texture/sound；`mode` 为 select/view。
- `provider_ids`、`category_ids`、`category_names` 包含筛选；`exclude_provider_ids`、`exclude_category_ids`、`exclude_category_names` 排除筛选。
- `initial_provider_id` / `initial_category_id` 只负责初始定位、置顶和展开，不会隐藏其他资源。
- `category_tips` 按分类名称提供文本或 `{text: 提示文本, delay_time: 秒数}`，默认延迟 0.5 秒；初始自动选中和手动选中都可触发。
- `multi_select_enabled`、`multi_select_mode`、`multi_selected_item_ids` 控制多选，初始勾选使用完整资源 ID。
- `allow_custom_texture_path` 默认 False，仅贴图单选且回调有效时显示；`initial_custom_texture_path` 设置初值。自定义路径回调的后两个 ID 都是空字符串，调用方持久化 resource_path，不能按 ID 解析失败处理。

选择器只返回选择结果，不代表已保存业务配置。UI 注册表及预览不赋予执行资源相关服务端操作的权限。

## 奇异宝典配置入口

监听 `ModSettingRegisterRequest`，使用 `API_RegisterModSettings(provider_id, provider_name, settings)` 发布该模组全部入口，或 `API_RegisterModSetting(provider_id, provider_name, setting_id, setting_name, icon, open_callback, options=None)` 更新单项。open_callback 为无参函数；具体排序、描述和 wheel_enabled 选项查 config_book_registry.py。

用 `API_ResolveModSetting` / `API_OpenRegisteredModSetting` 按 `provider_id:setting_id` 查询或打开；`API_GetConfigBookWheelSlots`、`API_GetConfigBookWheelEntries`、`API_FindConfigBookWheelSlot`、`API_AssignConfigBookWheelSlot` 管理宝典槽位，参数与保存反馈查源码。注册只是发布客户端入口，不能替代服务端业务权限校验，也不要与全局配置持久化 API 混淆。

配置入口现支持字符串 `itemId`，用于资源中心联动，不是 Minecraft 物品名称，也不是资源选择器的 asset_id。按当前注册样例传商城组件 ID；仍须提供可调用的 open_callback，不能用 itemId 替代正常打开入口。
