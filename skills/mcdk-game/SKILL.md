---
name: mcdk-game
description: >
  MCDK 游戏实时连接 — 通过 stdio MCP 桥接器连接运行中的 Minecraft 基岩版游戏，
  执行代码、查看 UI 树、抓日志、热重载。
  当用户提到连接游戏、查看游戏状态、热重载、调试 UI、执行游戏内代码等关键词时触发。
---

# Skill: mcdk-game — MCDK 游戏实时连接

通过 MCDK MCP 桥接器连接运行中的 Minecraft 游戏，用于 UI 调试、代码验证、日志排查。

## 前置条件

1. 游戏通过 MCDK 启动，`.mcdev.json` 中 `mcp_server_config.enabled: true`
2. `mcdk_stdio_bridge.py` 已注册为 MCP Server（名字 `mcdk_game`）
3. 游戏已进入世界（`ClientLoadAddonsFinishServerEvent` 已触发）

## 连接流程

MCP 工具注册后直接调用即可，无需手动建立连接。首次调用工具时桥接器自动初始化会话。

## 可用工具

| 工具 | 用途 | 示例 |
|------|------|------|
| `execute_code` | 在游戏客户端/服务端执行 Python | `{"code": "...", "is_client": true, "direct_return": true}` |
| `jsonui_debugger` | UI 树分析 | `{"cmd": "/screens"}` |
| `reload_game` | 重启游戏 | `{}` 完整重启；`{"reload_addons": true}` 连带 addon |
| `get_latest_logs` | 抓游戏日志 | `{"max_count": 20, "order": "desc"}` |
| `get_latest_error_logs` | 只看 stderr 报错 | `{"max_count": 10}` |
| `capture_game_window` | 截取游戏画面 | `{}` — 480p JPEG |

## execute_code 用法

```python
# 客户端执行
{"code": "import mod.client.extraClientApi as cApi; ui = cApi.GetTopUINode(); _result = ui.__class__.__name__", "is_client": true, "direct_return": true}

# 服务端执行
{"code": "import mod.server.extraServerApi as sApi; pl = sApi.GetPlayerList(); _result = len(pl)", "is_client": false, "direct_return": true}
```

- `_result` 变量的值会作为返回值传回
- `is_client: true` = 客户端，`false` = 服务端
- `direct_return: true` = 直接返回结果，`false` = 异步通过日志返回

## jsonui_debugger 常用命令

| 命令 | 用途 |
|------|------|
| `/screens` | 列出所有打开的屏幕 |
| `/overview --screen=<name>` | 鸟瞰屏幕结构，找根路径 |
| `/tree <screen> <path> --depth=3` | 查看 UI 树 |
| `/node <screen> <path> --fields=text` | 查看节点属性（文字、布局等） |
| `/children <screen> <path>` | 列出子控件 |
| `/mod-ui` | 列出 ModSDK 注册的 UI |
| `/reload-ui` | 仅重载 UI JSON（~2s，不改 Python） |

## 热重载策略

| 改了什么 | 操作 | 耗时 |
|---------|------|------|
| 仅改 JSON UI | `/reload-ui` | ~2s |
| 改了 Python | `reload_game` | ~12s |
| 全改（Python+JSON+资源） | `reload_game({"reload_addons": true})` | ~10s |

**原则**：改 JSON 不要重启游戏，用 `/reload-ui` 秒级刷新。

## 典型工作流

1. 改 JSON/Python → 保存
2. 改 JSON → `/reload-ui`；改 Python → `reload_game`
3. `execute_code` 注入测试数据
4. `jsonui_debugger /tree` 查看 UI 树验证结构
5. `get_latest_error_logs` 排查报错
6. 重复
