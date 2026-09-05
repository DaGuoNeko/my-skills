# 服务端、指令与存档

下列方法来自前置 ServerSystem，客户端入口会单独标注。阅读实际源码确认完整签名，不把名称存在等同于调用成功。

## 请求与权限

客户端 `TS(data, back=None, eventsuid='', timeout_seconds=10.0)` 发送带 `lx` 的请求，服务端 `AnyEvent` 派发并返回 `backdata`；服务端 `TC` 为反向请求。保留已有回调字段及超时语义，不随意改两端协议。

服务端处理玩家请求使用事件 `args['__id__']`，不能信任正文上传的 playerId。可调用 `API_IsPlayerOperator(player_id)` 核验管理权限；客户端按钮隐藏仅控制展示。

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

简易 Provider 的 `descriptor['datasets']` 是数据集列表，每项具有 `id` 与非空 `keys` 列表；其他描述字段查 `_NormalizeProviderDescriptor`。键不能重复分配或占用内部保留键，注册返回 `(ok, msg)` 必须检查。可选回调包括 `validate_import`、`after_import`、`after_export`，签名与时机查 `ExtraDataCrossSaveProvider`，不要假定注册后自动同步业务缓存。

高级 Provider 至少实现 `export_dataset(dataset_id, context)` 和 `apply_dataset(dataset_id, value, context)`。按需实现校验、commit、rollback_dataset 等回调；`validate_provider` 可对全部 datasets 做关联校验。事务备份、应用、失败回滚与缓存恢复需要一起设计，不能只描述成功写入。

关联数据使用 `atomic_groups`，需要独占迁移的 Provider 使用 `exclusive_selection`；读取现有规范化实现确定格式。保持 provider_id、dataset id 和 schema_version 的含义稳定，导入旧快照时明确版本兼容。

客户端管理界面入口是 `API_OpenCrossSaveManager`；旧格式转换使用 `API_RegisterCrossSaveLegacyImporter`，不另建一套迁移协议。

## 整体 ExtraData 的特殊语义

内置 `DAGUOMIAO_whole_extra_data` 导入先写待恢复状态，不是立即替换全部运行中数据；结果中的 `requires_world_reload` 需要向用户说明重进世界才能应用。

`ApplyPendingWholeExtraDataRestore()` 在服务端启动时先于 `GlobalConfig`、`ContData` 缓存初始化调用。维护此流程时保留快照校验、内部键排除、目标独有键清理、失败回滚和待恢复状态，不把这个启动顺序移动到缓存初始化之后。

导入会替换或删除数据，执行真实迁移测试需符合用户授权范围并准备可恢复数据。静态检查无法证明跨世界、重启后缓存及落盘恢复正确。
