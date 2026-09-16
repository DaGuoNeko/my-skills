# 服务端、指令与存档

下列方法来自前置 ServerSystem，客户端入口会单独标注。阅读实际源码确认完整签名，不把名称存在等同于调用成功。

跨存档部分于 2026-09-16 按当前工作树更新。新增或修改 Provider 前先读前置根目录 `CROSS_SAVE_GUIDE.md`（当前未跟踪文件），再核对 CrossSaveManager.py；指南不存在时从实现确认，不能套用旧的延迟全量恢复流程。

## 请求与权限

客户端 `TS(data, back=None, eventsuid='', timeout_seconds=10.0)` 发送带 `lx` 的请求，服务端 `AnyEvent` 派发并返回 `backdata`；服务端 `TC` 为反向请求。保留已有回调字段及超时语义，不随意改两端协议。

服务端处理玩家请求使用事件 `args['__id__']`，不能信任正文上传的 playerId。可调用 `API_IsPlayerOperator(player_id)` 核验管理权限；客户端按钮隐藏仅控制展示。

房主相关权限有三种不同语义：`API_IsPlayerOperator` 检查 OP；`API_IsActualHostPlayer` 只检查实际房主；`API_HasHostPermission` 包含实际房主和被授权玩家。兼容接口 `API_IsHostPlayer` 当前等同 HasHostPermission，不能用于“仅实际房主”的操作。`API_GetHostPlayerId` 统一处理原生房主 ID 与持久化首位玩家回退，不在业务模组复制判断。

权限名单管理使用 `API_GetHostPermissionManagerData`、`API_GrantHostPermissionRequest` / `API_RevokeHostPermissionRequest` 等服务端入口，具体身份和 revision 参数查源码。不要从客户端上传 UID 构造授权身份；`API_RecordVerifiedClientUid` 只适用于已经核验的来源。各业务仍须按自己的权限契约选择 OP 或房主级权限，不能全局互换。

不要假定所有公共 API 自动做权限检查。尤其 `API_RunCommandLibrary(player_id, library_id)` 为服务端入口，不做 OP 检查，调用方应基于业务授权决定能否执行。

## 指令库与配置

- `API_RunCommandLibrary` 返回 `(ok, msg)` 表示入队结果，不代表指令已全部执行。延迟 `delay_ticks` 从上一条实际执行后开始，执行受全局逐刻上限控制。
- `API_TryRunLegacyCommandLibrary` 支持旧业务来源接管；阅读 `CommandLibrary.TryRunLegacyLibrary` 的返回结构，只有 `handled=False` 才回退旧执行逻辑，避免重复执行。
- 实体移除或业务取消时核对 `API_CancelCommandLibraryRunsForExecutor`；诊断队列可用 `API_GetCommandLibraryQueueStatus`。
- 客户端通过 `API_OpenCommandLibraryForSource` 接入来源界面，引用生成用 `API_MakeCommandLibraryReference`，不要自行拼接未核实的引用格式。
- `API_GetGlobalConfig(key=None)` 读取配置；`API_SetGlobalConfig` / `API_ResetGlobalConfig` 返回 `(ok, msg)`。调用方不能把非空 tuple 直接当作成功布尔值。
- `ContData` 与 `GlobalConfig` 是不同数据入口。不要绕过缓存直接写同一 ExtraData 键，也不要把前置的配置键用作业务模组的数据空间。

## 跨存档 Provider 选择

| 数据情况 | 接入方式 |
|---|---|
| 可完整替换、可 JSON 序列化的 ExtraData 数据 | `API_RegisterCrossSaveExtraDataProvider(provider_id, descriptor, callbacks=None)` |
| 有内存权威缓存、复杂关系、特殊合并或恢复规则 | `API_RegisterCrossSaveProvider(provider_id, descriptor, callbacks)` |
| 用户明确需要整个世界 ExtraData 迁移 | 核对内置整体 Provider；普通业务接入不默认使用全量恢复 |

简易 Provider 的 `descriptor['datasets']` 是数据集列表，每项具有 `id` 与非空 `keys` 列表；其他描述字段查 `_NormalizeProviderDescriptor`。键不能重复分配或占用内部保留键，注册返回 `(ok, msg)` 必须检查。可选回调为 `validate_import`、`after_import`、`after_whole_import`、`after_export`，签名与时机查 `ExtraDataCrossSaveProvider`，不要假定注册后自动同步业务缓存。

高级 Provider 至少实现 `export_dataset(dataset_id, context)` 和 `apply_dataset(dataset_id, value, context)`。按需实现校验、commit、rollback_dataset 等回调；`validate_provider` 可对全部 datasets 做关联校验。事务备份、应用、失败回滚与缓存恢复需要一起设计，不能只描述成功写入。

关联数据使用 `atomic_groups`，需要独占迁移的 Provider 使用 `exclusive_selection`；读取现有规范化实现确定格式。保持 provider_id、dataset id 和 schema_version 的含义稳定，导入旧快照时明确版本兼容。

客户端管理界面入口是 `API_OpenCrossSaveManager`。当前 ClientSystem 已无 `API_RegisterCrossSaveLegacyImporter` 等旧格式注册接口，不再指导新代码调用；若需兼容旧包，应单独核对该版本实现。分片、压缩、本地存储及权限交给前置，不另建迁移网络协议。

高级 Provider 的普通 after_import 返回值不判定事务失败，失败应抛异常；简单 Provider 适配层会将 False 或失败结果转换为异常。after_export 在客户端确认保存后执行，其失败形成警告。普通导入有持久化事务备份，异常逆依赖回滚，重启后等待相关 Provider 注册再恢复。

目标缺失的 Provider 及依赖它的 Provider 会被普通导入跳过；至少需一个可用 Provider。import_mode 是描述字段，不能以为填写 merge 就自动合并，实际行为由 apply_dataset 决定。

## 整体 ExtraData 的特殊语义

内置 `DAGUOMIAO_whole_extra_data` / `whole_extra_data` 必须独占选择。**当前工作树会立即替换并保存 ExtraData**，然后按依赖顺序调用已注册 Provider 的 `after_whole_import(context)`。这与旧版本写待恢复状态、重进后应用不同；不能混用两套生命周期。

全量写入快照中的普通键并清理目标独有普通键，同时保护跨存档内部键、旧拆分内部键及当前世界的 world_owner、announcement_identity、admin_book_grants。没有安装相应业务模组时，全量键仍可保留；与普通 Provider 快照的缺失跳过行为不同。

`after_whole_import` 必须按“读取新 ExtraData → 替换内存 → 重建索引/计时器 → 同步客户端”执行，禁止先将旧缓存落盘。全量数据落盘后的刷新失败不会撤销整个导入；检查 refresh_failed_providers、refresh_unsupported_providers、refresh_skipped_providers。存在未刷新项时 requires_world_reload=True，需向用户说明重进补齐缓存。

全量编码支持 tuple、set、frozenset、非字符串 dict 键；普通 Provider 导出仍应返回 JSON 可序列化数据。客户端快照使用 ConfigClient 索引/分片，JSON → zlib → Base64；当前不使用 MD5 锁定正文，但保留结构、版本、长度、分片归属及业务校验。不要把“可编辑快照”理解为可以随意破坏协议字段。

导入会替换或删除数据，执行真实迁移测试需符合用户授权范围并准备可恢复数据。静态检查无法证明跨世界、重启后缓存及落盘恢复正确。
