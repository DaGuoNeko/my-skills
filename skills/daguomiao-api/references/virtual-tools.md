# 奇异宝典虚拟工具

2026-09-16 核对 ClientSystem、virtual_tool_registry.py、服务端 VirtualToolManager.py 和 ServerSystem。基础功能已提交，后续工作树仍有变更；具体权限与返回结构以实际版本为准。

## 双端注册不可省略

客户端 `API_RegisterVirtualToolProvider(provider_id, provider_name, icon, entries, options=None)` 发布选轮分支，并生成可分配到宝典选轮的配置入口。`API_OpenVirtualToolProvider(provider_id)` 打开该分支；监听 `VirtualToolRegisterRequest` 后发布，不在响应中重复广播。entries 的层级和条目类型查 virtual_tool_registry.py，不能直接当服务端白名单传入。

服务端同名接口签名不同：`API_RegisterVirtualToolProvider(provider_id, tools)`。tools 是列表，每项至少含 id 与 layer_texture，可含 name。provider_id 与工具 id 不能为空或包含冒号，完整 ID 为 provider_id:tool_id。服务端只采用自身注册表中的贴图信息，不信任客户端选择请求上传的贴图。

## 状态与执行

- 客户端 `API_GetActiveVirtualTool()` 读取本地物品镜像，只用于展示。
- 服务端 `API_GetActiveVirtualTool(player_id, provider_id=None)` 读取玩家实际主手优先、副手其次的宝典，检查工具注册状态；业务执行用此结果和可信事件玩家 ID 验证。
- `API_GetVirtualToolState(player_id)` / `API_SetVirtualToolState(player_id, state, provider_id=None)` 管理宝典上的工具状态。state 为 dict，序列化长度有 65536 限制，处理返回失败，不能把大型业务存档放入物品状态。
- `API_ClearActiveVirtualTool(player_id, provider_id=None)` 清理当前工具，`API_ResetEccentricTome(player_id)` 重置宝典；二者语义及权限不同，不用 Reset 替代业务级清理。

前置负责选择与物品状态，不自动实现业务工具效果。事件触发时重新核对实际手持宝典、当前工具及业务权限，不能仅凭客户端回调执行破坏性操作。NBT 中字段可能封装为 __value__，复用公开 API 避免业务各自猜结构。
