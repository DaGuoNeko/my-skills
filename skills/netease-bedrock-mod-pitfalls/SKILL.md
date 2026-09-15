---
name: netease-bedrock-mod-pitfalls
description: 网易 Minecraft 基岩版 ModSDK 的实测踩坑与排障指南。开发或审查 Python 模组的实体生命周期、ModAttr、ExtraData、客户端同步和重进存档恢复逻辑时使用；不用于国际版 Script API。
---

# 网易 Minecraft 基岩版模组踩坑指南

只把经过真实游戏复现和验证的网易 ModSDK 行为写成强约束。分析相关问题时，先区分静态代码结论、服务端运行值、客户端运行值以及重进存档后的恢复结果。

## EntityLoadScriptEvent 与 ModAttr

在当前网易 Minecraft 基岩版 1.21.120 环境中已经实测确认：不要在 `EntityLoadScriptEvent` 回调内立即调用 `CreateModAttr(entityId).SetAttr(...)`。

实体加载事件触发时，实体的 ModAttr 恢复和客户端同步链可能尚未准备完成。此时立即写入任意 ModAttr，可能造成该实体的 ModAttr 数据在客户端重进后整体读取不到；服务端仍可能读到值，因此只检查服务端会产生误判。`needRestore=True` 或 `autoSave=True` 不能修复这个生命周期时序问题。

错误写法：

```python
def EntityLoadScriptEvent(self, args):
    entity_id = args[0]
    CF.CreateModAttr(entity_id).SetAttr(
        'example:state', 'ready', True, True)
```

正确做法：

```python
def EntityLoadScriptEvent(self, args):
    entity_id = args[0]
    CF.CreateGame(levelId).AddTimer(
        0.1, self._RestoreEntityModAttr, entity_id)

def _RestoreEntityModAttr(self, entity_id):
    """实体加载链稳定后恢复需要持久化和同步的 ModAttr。"""
    CF.CreateModAttr(entity_id).SetAttr(
        'example:state', 'ready', True, True)
```

实现时遵守以下约束：

- 默认把同一实体在加载阶段需要执行的 ModAttr 写入合并到一个延迟回调中，延迟至少 `0.1` 秒。
- 延迟回调执行时重新确认实体仍然有效，并在回调内重新读取所需的 `ExtraData`；不要依赖事件触发瞬间取得的未恢复数据。
- 如果 `ExtraData` 在 `0.1` 秒后仍未恢复，只允许有限次数重试，不能每 Tick 无限重写 ModAttr。
- `EntityLoadScriptEvent` 可能覆盖大量非目标实体。写入前必须验证实体类型或正式配置，不能先写 ModAttr 再判断是不是目标 NPC。
- 排查同步故障时，同时验证服务端 `GetAttr`、客户端 `GetAttr`、客户端更新回调以及退出重进后的值。只有实时写入成功不能证明恢复正常。

典型故障特征：

- 设置后当前客户端暂时能读取，退出重进后变为未设置。
- 服务端能读取 ModAttr，但客户端同一实体读取不到。
- 写入一个无关字段后，该实体其他 ModAttr 的客户端恢复也异常。
- 只有走过设置魔杖或初始化流程的 NPC 出现问题，新生成但未初始化的实体正常。

遇到这些特征时，优先搜索 `EntityLoadScriptEvent` 调用链中的所有 `SetAttr`，包括经管理器的 `OnEntityLoaded -> SyncEntity` 等间接写入，而不仅搜索事件函数本体。
