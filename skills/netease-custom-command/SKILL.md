---
name: netease-custom-command
description: 为网易 Minecraft 基岩版 ModSDK 创建、修改、审查或删除自定义指令。用户提到 netease_commands、自定义指令、CustomCommandTriggerServerEvent、指令参数、权限或变体时使用。
---

# 网易 ModSDK 自定义指令

按照网易官方 schema 和目标仓库既有架构实现指令，不把原版命令、聊天文本解析或客户端按键误判为自定义指令。

## 开始前

1. 找到行为包、`netease_commands/`、System 注册入口和现有命令分发器。
2. 完整阅读相关文件，确认 Python 版本、命名空间、事件监听和返回值约定。
3. 创建、修改、审查指令时，必须阅读 [references/custom-command-schema.md](references/custom-command-schema.md)。仅删除已明确定位的指令时可直接按“删除指令”处理。
4. 若官方文档与仓库旧代码冲突，以当前官方文档和用户明确约定为准，并指出兼容影响。

## 实现流程

1. 在行为包 `netease_commands/` 中创建一个指令定义 JSON；Python handler 不能替代 JSON 声明。
2. 让 JSON `name` 与事件 `data['command']` 以及路由表 key 完全一致。不要自行添加文档未定义的 `namespace` 字段。
3. 使用现有的 `CustomCommandTriggerServerEvent` 监听器；已有统一分发器时，只新增路由和 handler，不重复监听事件。
4. handler 按固定签名接收 `args, origin, return_failed, return_msg_key, variant`。
5. 对引擎已按 JSON 校验的固定参数，直接使用 `args[index]['value']`。不要添加冗余的 `.get('value', ...)`、`if args else ...` 或猜测型默认值。
6. 服务端业务直接在 handler 中执行。需要打开 UI 时，通过项目既有服务端到客户端事件发送，并同步实现明确的客户端处理路由。
7. 敏感操作仍需按业务要求校验权限和触发源；命令方块触发时 `origin` 没有 `entityId`。

## 兼容与质量约束

- 保持目标项目的 Python 2.7 语法、方法签名、命令前缀和返回消息风格。
- `variant` 是 `0` 到 `9` 的整数，不是字符串。
- 带 `default` 的参数必须位于该变体参数列表尾部。
- 不直接重命名已经公开的命令、路由 key 或下游调用方法；需要迁移时保留兼容入口。
- 静态 JSON/Python 检查不能替代游戏内测试。验证聊天栏补全、权限、各变体、默认参数、命令方块和失败消息。
- 未经用户明确要求，不提交或推送 Git。

## 删除指令

同时检查并移除：`netease_commands` JSON、路由表项、handler、专用客户端消息处理器和仅由该指令使用的 import。保留仍被其他指令复用的通用分发框架，并全仓搜索残留的指令名。
