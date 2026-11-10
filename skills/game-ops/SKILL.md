---
name: game-ops
description: >
  启动和操作网易 Minecraft 基岩版测试游戏：用大果喵工具箱启动存档、多开客户端联机测试，
  在游戏里执行代码、看日志、热重载、查 UI 树、截图、键鼠输入、控制玩家移动/放方块/打怪、性能分析。
  当用户提到启动游戏、进存档、多开、联机测试、连接游戏、执行游戏内代码、热重载、
  看游戏日志、调试 UI、截图、操作玩家、实机测试/回归、查存档数据或模组、导入建筑/地形时使用。
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
| 只停在主菜单 | `launch_client(mode: blank / debug / profile)`，profile 模式配合 `list_projects`（旧版叫 `list_launch_profiles`）的配置 ID |
| 要一份干净副本再测（会改坏存档的测试） | `clone_world(instanceId, requestId, worldId, name, confirmed: true)`，只能复制已停止的存档，模组源码不复制 |
| 导入外部存档 | 先 `inspect_world_source(source)` 只读检查，再 `import_world(..., mode: copy, confirmed: true)`；`linked` 会直接用原目录，用户明确要才用 |
| 改了贴图、JSON 资源后启动前自查 | `validate_world_assets(worldId)`：扫描坏 PNG、空资源路径和引用，不启动、不改文件 |

启动后等就绪：
- **优先 `wait_client_ready(sessionId, generation, timeoutMs: 60000)`**：在期限内等到可执行世界状态再返回，不会重启或重载。超时就再调一次，最多等 2~3 轮；不清楚卡在哪用 `client_readiness` 看分层状态。
- 房主：就绪（`state: game_ready`）才算可操作。
- 来宾：还要 `list_clients` 看 `autoJoin.phase: joined` 才算入房成功；`needs_attention` 要用户手动处理，**不要换 requestId 重开**。
- `waiting_assertion`（引擎断言弹窗）：`list_client_assertions` 读弹窗内容报给用户；用户同意后才 `resolve_client_assertion(action: ignore, confirmed: true)` 忽略，一次一个。忽略不等于问题修好了，之后看日志。

等待时间（实测）：房主和来宾各约 30 秒；同时开的游戏越多越慢。

来宾 `phase: failed` 且 `state: ended`（客户端已自动关闭）时：
1. 先 `client_logs` 看失败原因。常见的是「原生游戏菜单未就绪」，多开、机器负载高时菜单 20 秒内没加载出来。
2. 偶发原因用**新的 requestId**（上一次已结束，不算同一次启动）、相同 playerName 和 hostSessionId 重开一次。
3. 再失败就停下，把日志原因告诉用户，不要反复重开。

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
| 重载 | `reload_client(action)`：`scripts` 只热更新 Python；`world` / `addons` 需 `confirmed: true`，`addons` 连资源一起刷新。按下方「重载策略」选 |
| UI 树、截图、键鼠、性能、只看报错 | 先 `list_client_mcdk_tools` 看该客户端支持什么，再 `call_client_mcdk_tool(name, arguments)` |

重载策略（用户偏好：默认重载游戏，更安全）：
- **默认**：改完代码用 `reload_client(action: addons, confirmed: true)` 重载游戏，脚本、资源和初始化流程都重新走一遍。
- **只有小代码才热更新**：只改了函数内部几行逻辑，且没碰注册、事件监听、`__init__`、模块级变量、存档读写时，才用 `scripts` 热更新。拿不准就按默认重载。
- **只改 UI JSON**：可以用 `jsonui_debugger` 的 `/reload-ui`；涉及 Python 绑定一起改时按默认重载。
- **新增/删除模组、改 manifest 或启动配置的模组列表**：`reload_client` 会拒绝，请用户在工具箱保存后重启。
- 多开时源码目录共用（看 `sharedSources`），重载前确认要刷新的是哪些客户端，逐个重载。
- 重载后重新 `list_clients` 拿新 `generation`，再看日志和执行代码确认改动生效。

`call_client_mcdk_tool` 常用工具：
- `jsonui_debugger`：`{"cmd": "/screens"}` 列屏幕（只有 HUD 时返回空列表，属正常），`/tree <screen> <path> --depth=3` 看树，`/node ... --fields=text` 看属性，`/reload-ui` 只重载 UI JSON（约 2 秒，改 JSON 优先用它，不重启）。
- `get_latest_error_logs`：只看报错。
- 截图**只在必须看画面时用**，优先日志和 UI 树。首选工具箱的 `capture_client_window(sessionId, generation)`：窗口被挡住也能截、不抢焦点、原始分辨率 PNG；MCDK 的 `capture_game_window` 是 480p 备用。要固定位置/角度/时间/天气拍图用 `capture_scene`（会暂停昼夜和天气，需 `confirmed: true`）。
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
- **限制：modpc 固定连本机 14520 端口，只能控制一个游戏。** 实测多开时它连的是**最先启动的房主**，后开的房主和来宾都控制不了。同时开了多个客户端时，先用工具箱 `execute_client_code` 读坐标，和 modpc 的 `get_position()` 对照，确认连的是目标客户端再操作；对不上就改用工具箱的 `execute_client_code` 或 `mc_input` 操作目标客户端。

## 5. 存档数据、维度和地形

| 要做的事 | 工具 | 注意 |
|---|---|---|
| 看存档里装了哪些模组、启用状态、UUID/版本/依赖问题 | `inspect_world_packs(worldId)` | 只读静态诊断，只看存档内置的包；启动配置挂载的开发模组不在这里（看 `read_project`），没有内置包时返回 `missing-list` 属正常。不代表游戏实际加载成功；改动让用户在工具箱存档模组窗口确认 |
| 离线查存档里保存的对象和业务数据 | `scan_world_data(worldId, requestId, scope: all/gameplay/world/entities)` → `world_data_scan_state(requestId)` 查进度或取消 → `read_world_data(requestId, view: objects/relations/fields)` 分页看 | 只读、不用开游戏，最长 120 秒；`not-found` 不代表不存在 |
| 对比两次存档数据（改动前后、重进存档前后） | `compare_world_data(left, right)`，传两次扫描的 requestId | `partial` 表示扫描不完整，不能据此断言对象被删 |
| 查维度实际高度范围 | `probe_dimension_runtime(..., confirmed: true)` | 指定维度时会传送过去再恢复位置 |
| 测某个 Y 能否放方块 | `probe_build_height(..., candidateY, confirmed: true)` | 只能在 isolated 会话用；会写入测试方块再恢复 |
| 导入 Java/基岩建筑或地形 | `terrain_prepare` → 需要从运行中的来源取区域时 `terrain_capture_source` → `terrain_preview` → `terrain_apply` → 不满意 `terrain_rollback`；随时 `terrain_status` 看进度 | **会写入目标存档**：先 `clone_world` 备份或在测试存档里做，预览给用户确认后才 apply；结果不确定时不自动重放 |

扫描和读取都要自定 `requestId`，之后查状态、读结果、对比都用它。

## 6. 收尾和安全

- 关客户端：直接 `close_client(sessionId, confirmed: true)`，不用先手动保存游戏（用户偏好）；它只关指定客户端。多开时先关来宾再关房主，关完 `list_clients` 确认 `running: false`。
- 已结束的客户端可用 `remove_client` 从列表移除（保留日志和存档）。
- **执行代码、重载、输入超时 = 结果未知，禁止自动重试**，先看日志确认状态。
- 多客户端共享桌面焦点：`mc_input` 和 modpc 的动作一次只对一个客户端串行进行。
- 不要删存档。启动配置（`update_project`）、游戏设置（`update_game_options`）、工具箱设置（`update_settings`）只在用户明确要求时改，改前先 `read_project` / `read_game_options` / `read_settings` 拿 `revision`；它们不影响已运行的游戏，改完要重启对应客户端才生效。

## 7. 验收

用日志、`execute_client_code` 读到的数据或 UI 树确认结果，必要时再截图。涉及存档保存的改动，关游戏后用 `scan_world_data` + `compare_world_data` 对比前后数据。只报告实际验证过的行为；没测到的（联机同步、重进存档、发布包）明确列为待实测。
