# 网易 ModSDK 自定义指令规范

## 官方来源

- [自定义指令教程](https://mc.163.com/dev/mcmanual/mc-dev/mcguide/20-%E7%8E%A9%E6%B3%95%E5%BC%80%E5%8F%91/15-%E8%87%AA%E5%AE%9A%E4%B9%89%E6%B8%B8%E6%88%8F%E5%86%85%E5%AE%B9/9-%E8%87%AA%E5%AE%9A%E4%B9%89%E6%8C%87%E4%BB%A4.html?catalog=1)
- [CustomCommandTriggerServerEvent](https://mc.163.com/dev/mcmanual/mc-dev/mcdocs/1-ModAPI/%E4%BA%8B%E4%BB%B6/%E4%B8%96%E7%95%8C.html#customcommandtriggerserverevent)

实现前优先重新核对官方页面，以免字段或事件数据随版本变化。

## 文件位置与命名

在行为包中新建：

```text
netease_commands/
└── 团队名_模组命名空间_指令名称.json
```

文件名推荐只使用英文字母、数字和下划线，不使用中文或特殊字符。文件名只是资源组织方式；事件中的 `command` 对应 JSON 的 `name`。

## 指令 JSON

```json
{
    "format_version": "0.0.1",
    "name": "grant_demo",
    "description": "向目标玩家执行示例操作",
    "permission_level": "game_directors",
    "args": [
        {
            "name": "目标",
            "type": "target"
        },
        {
            "name": "数量",
            "type": "int",
            "default": 1
        }
    ]
}
```

字段说明：

| 字段 | 要求 |
|---|---|
| `format_version` | 当前官方教程要求字符串 `"0.0.1"` |
| `name` | 指令名称，也是事件 `command` 和路由 key |
| `description` | 指令说明，可直接写文本或使用语言文件 |
| `permission_level` | 指令权限，省略时官方默认值为 `game_directors` |
| `args` | 第 0 套参数；每项依次描述一个参数 |
| `args1`…`args9` | 可选参数变体，对应事件 `variant` 1…9 |

不要添加官方 schema 未定义的独立 `namespace` 字段。若项目要求带冒号的指令名，先以该项目已有可运行 JSON 或对应版本官方资料验证支持情况。

## 权限等级

| 值 | 含义 |
|---|---|
| `game_directors` | 操作员和命令方块可执行 |
| `admin` | 操作员可执行，命令方块不可执行 |
| `host` | 服务器主机可执行 |
| `owner` | 仅专用服务器可执行 |
| `any` | 所有人可执行 |

JSON 权限是第一层限制。涉及管理、经济、物品发放或持久化时，仍根据业务规则做服务端授权判断。

## 参数定义与取值

每个参数对象包含：

| 字段 | 说明 |
|---|---|
| `name` | 输入提示名称，也会出现在事件参数字典中 |
| `type` | 参数类型 |
| `default` | 可选；任意 JSON 值，且所有含默认值的参数必须排在尾部 |

事件中的 `args` 是按 JSON 顺序排列的 `list(dict)`。每项结构为：

```python
{
    'name': '数量',
    'type': 'int',
    'value': 1
}
```

固定 schema 下直接取值：

```python
targets = args[0]['value']
amount = args[1]['value']
```

不要把 `args[0]` 本身当作值，也不要为引擎已经验证的固定位置添加 `.get('value', ...)` 或 `if args else ...`。缺少必填参数时指令不会正常触发；省略可选参数时引擎填入 JSON 的 `default`。

## 参数类型映射

| JSON `type` | Python `value` | 形态示例 |
|---|---|---|
| `int` | `int` | `114` |
| `float` | `float` | `5.14` |
| `bool` | `bool` | `True` |
| `str` | `str` | `'text'` |
| `enum` / `enum_short` | `str` | JSON 指定的枚举项 |
| `block` | `str` | `'minecraft:grass'` |
| `item` | `dict` | `{'itemName': 'minecraft:apple'}` |
| `pos` | `tuple` | `(-0.93, 81.25, -5.67)` |
| `target` | `tuple` | 一个或多个目标 `entityId` |
| `entity` | `dict` | `{'entityType': 'minecraft:cow'}` |
| `effect` | `dict` | 名称及 `EffectType` id |
| `dimension` | `dict` | 名称及维度 id |
| `biome` | `dict` | 名称及 `BiomeType` |
| `structure` | `dict` | 名称及 `StructureFeatureType` |
| `enchant` | `dict` | identifier 及 `EnchantType` |

JSON `null` 会转成 Python `None`，JSON array 会转成 Python `tuple`。

## 事件数据

`CustomCommandTriggerServerEvent` 的关键字段：

| 字段 | 类型 | 用途 |
|---|---|---|
| `command` | `str` | 对应 JSON `name` |
| `args` | `list(dict)` | 当前变体解析后的参数 |
| `variant` | `int` | `0` 对应 `args`，1…9 对应 `args1`…`args9` |
| `origin` | `dict` | 指令触发源 |
| `return_failed` | `bool` | 设为 `True` 时以失败样式返回 |
| `return_msg_key` | `str` | 返回文本或语言文件 key |

`origin` 通常包含：

- `entityId`：实体触发者；命令方块触发时不存在。
- `dimension`：触发维度 id。
- `blockPos`：实体或命令方块的整数坐标。

## 路由与 Handler 示例

已有统一分发器时，只增加路由和方法：

```python
class CustomCmd(object):

    def __init__(self, server_system):
        self._Mser = server_system
        self.cmdlist = {
            'grant_demo': self.grant_demo,
        }

    def CustomCmdEvent(self, data):
        command = data['command']
        args = data['args']
        origin = data['origin']
        variant = data['variant']
        if command in self.cmdlist:
            data['return_failed'], data['return_msg_key'] = self.cmdlist[command](
                args, origin, data['return_failed'], data['return_msg_key'], variant)

    def grant_demo(self, args, origin, return_failed, return_msg_key, variant):
        """处理 grant_demo 指令。"""
        targets = args[0]['value']
        amount = args[1]['value']
        try:
            for player_id in targets:
                # 在此调用项目服务端业务接口。
                pass
        except Exception as e:
            print '[CustomCommand] grant_demo failed:', e
            return True, '执行失败'
        return False, '执行成功，数量：%s' % amount
```

事件监听通常由 ServerSystem 统一注册：

```python
self.ListenForEvent(
    serverApi.GetEngineNamespace(),
    serverApi.GetEngineSystemName(),
    'CustomCommandTriggerServerEvent',
    self.CustomCmd,
    self.CustomCmd.CustomCmdEvent)
```

不要为每条指令重复注册事件。

## 参数变体

一条指令最多有 10 套参数：`args` 加 `args1` 至 `args9`。handler 根据整数 `variant` 解释对应位置：

```python
if variant == 0:
    target_pos = args[0]['value']
elif variant == 1:
    target_ids = args[0]['value']
```

各变体的区分位置不能使用会造成歧义的相同类型。例如 `<pos> <float>` 与 `<float> <pos>` 可能无法可靠解析；需要时在前面添加 `enum` 或 `enum_short` 作为显式模式选择。

## 服务端与客户端职责

- 修改世界、玩家数据、经济或持久化内容：服务端执行。
- 打开 UI 或显示客户端专属效果：服务端向目标客户端发送项目既有事件。
- 发送客户端事件时，必须同时实现对应客户端路由；不要发送一个不存在的 `lx` handler。
- 不相信客户端回传的权限或金额等关键数据。

## 验证清单

1. JSON 可解析，文件位置和名称合法。
2. JSON `name`、事件 `command`、路由 key 完全一致。
3. Python 2.7 语法通过，参数按 `args[index]['value']` 获取。
4. 测试所有 `variant`、必填参数、默认参数和无效输入。
5. 分别测试玩家、OP、非 OP、命令方块以及适用的服务器来源。
6. 检查 `return_failed` 与 `return_msg_key` 的游戏内显示。
7. 涉及客户端时验证目标玩家、多人选择器和客户端处理器。
8. 明确区分静态检查与实际游戏验证。

## 删除指令

删除一条指令时同步处理：

1. 删除对应 `netease_commands/*.json`。
2. 删除 `cmdlist` 路由项和 handler。
3. 删除该指令专用的客户端事件处理器。
4. 删除只被该指令使用的 import 或常量。
5. 全仓搜索 JSON `name`、路由 key 和客户端消息标识，确认无残留。

不要因为最后一条指令被删除就自动移除通用事件监听或分发类；除非用户明确要求删除整套命令系统。
