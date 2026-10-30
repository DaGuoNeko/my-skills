---
name: game-ops
description: >
  启动和操作网易 Minecraft 基岩版测试游戏：用大果喵工具箱启动存档、多开客户端联机测试，
  在游戏里执行代码、看日志、热重载、查 UI 树、截图、键鼠输入、控制玩家移动/放方块/打怪、性能分析。
  当用户提到启动游戏、进存档、多开、联机测试、连接游戏、执行游戏内代码、热重载、
  看游戏日志、调试 UI、截图、操作玩家、实机测试/回归时使用。
---

# 操作游戏

一句话路由：**启动、管理、调试一律走大果喵工具箱（`daguoneko_toolbox`），按 `sessionId` + `generation` 定位客户端；控制玩家动作用 `modpc`。** 不使用 `mcdk_game` 和 `mc-studio`。

## 1. 开局三步（每次都先做）

1. `toolbox_status`：确认 `online`，记下 `instanceId`。离线时调 `open_toolbox`，再查一次。
2. `list_clients`：只看 `running: true` 的条目，记下目标的 `sessionId`、`generation`、`worldName`、`state`。
   - 已有运行中、存档名和用户要求一致、`state: game_ready` 的客户端 → 直接复用，跳到第 3 节。
   - 多个运行中 → 按 `worldName` / `playerName` 逐个核对，不确定就问用户，**禁止默认选第一个或主游戏**。
3. 需要启动时看第 2 节。

`generation` 变了（重载、重进世界后）→ 重新 `list_clients` 拿新值再操作。

## 2. 启动

| 需求 | 做法 |
|---|---|
| 进某个存档测试 | `list_worlds` 找 `worldId`（用户只说名字时按 `name` 匹配，重名就问）→ `launch_world(instanceId, requestId, worldId)` |
| 本地多人测试 | 先有房主（复用或 `launch_world`）→ `launch_joined_client(instanceId, requestId, playerName, hostSessionId)`，每个来宾一个**不同的 playerName** 和**新的 requestId** |
| 只停在主菜单 | `launch_client(mode: blank / debug / profile)`，profile 模式配合 `list_launch_profiles` 的 `profileId` |

启动后轮询 `list_clients`，等到：
- 房主：`state: game_ready` 才算可操作。
- 来宾：`autoJoin.phase: joined` 才算入房成功；`waiting_assertion` 是断言弹窗等用户关；`needs_attention` 要用户手动处理，**不要换 requestId 重开**。

规则：
- **同一次启动的重试必须复用原 requestId**，超时也不换。
- 同一个存档禁止重复启动。
- 本地同机测试不用联机房间、邀请码、隧道；只有用户明确要远程联机才碰那些。
- `sharedSources` 非空表示和别的运行中存档共用源码目录，改代码会同时影响它们，提醒用户。

## 3. 调试（都在工具箱里，带 sessionId + generation）

| 要做的事 | 工具 |
|---|---|
| 执行 Python 2.7 代码 | `execute_client_code(side: client / server)`，最后一个表达式或 `_result` 作为返回值 |
| 看日志 | `client_logs(sessionId, limit)`，用 `afterId` 增量读 |
| 热重载 | `reload_client(action)`：`scripts` 改了 Python；`world` / `addons` 需 `confirmed: true`（改了 JSON、贴图、音效等资源用 `addons`） |
| UI 树、截图、键鼠、性能、只看报错 | 先 `list_client_mcdk_tools` 看该客户端支持什么，再 `call_client_mcdk_tool(name, arguments)` |

`call_client_mcdk_tool` 常用工具：
- `jsonui_debugger`：`{"cmd": "/screens"}` 列屏幕，`/tree <screen> <path> --depth=3` 看树，`/node ... --fields=text` 看属性，`/reload-ui` 只重载 UI JSON（约 2 秒，改 JSON 优先用它，不重启）。
- `get_latest_error_logs`：只看报错。
- `capture_game_window`：截图，**只在必须看画面时用**，优先日志和 UI 树。
- `mc_input`：键鼠输入，先 `{"op": "/help"}`、`/state`；坐标是 0~1 百分比；返回成功只代表已发送，要用截图或日志确认效果。
- `mc_profiler`：Python/原生性能分析，先 `/help`。按函数的 CPU 热点也可用 `mcdk-mcp-tracy`（`tracy_status` → `tracy_native_capture` → `tracy_get_function_costs`）。

示例：
```python
# 客户端：本地玩家脚下坐标
import mod.client.extraClientApi as c
_result = c.GetEngineCompFactory().CreatePos(c.GetLocalPlayerId()).GetFootPos()
```

## 4. 控制玩家（modpc）

用来让玩家走路、飞行、放/挖方块、攻击、点 UI 按钮、批量执行指令、搭测试场景。
- 每个会话第一次用前必须先调 `get_doc`，否则 `execute_script` 会被拒绝。
- `execute_script` 跑 Python 2.7：不含 `yield` 是同步查询，用 `print` 输出；含 `yield` 是协程，最后一行调用生成器函数。
- 指令用 `yield run_commands([...])` 一次批量发，基岩版语法，不能带 Java 版 NBT。
- **限制：modpc 固定连本机 14520 端口，只能控制一个游戏。** 同时开了多个客户端时，先用工具箱 `execute_client_code` 读坐标，和 modpc 的 `get_position()` 对照，确认连的是目标客户端再操作。

## 5. 收尾和安全

- 关客户端前先保存游戏，再 `close_client(sessionId, confirmed: true)`；它只关指定客户端。
- 已结束的客户端可用 `remove_client` 从列表移除（保留日志和存档）。
- **执行代码、重载、输入超时 = 结果未知，禁止自动重试**，先看日志确认状态。
- 多客户端共享桌面焦点：`mc_input` 和 modpc 的动作一次只对一个客户端串行进行。
- 不要删存档、不要改启动配置模板；需要按新模组列表启动时，让用户在工具箱里保存后重启。

## 6. 验收

用日志、`execute_client_code` 读到的数据或 UI 树确认结果，必要时再截图。只报告实际验证过的行为；没测到的（联机同步、重进存档、发布包）明确列为待实测。
