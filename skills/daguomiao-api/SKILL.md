---
name: daguomiao-api
description: >
  接入或维护 DAGUOMIAO_API_MOD 大果喵前置模组。用于依赖此前置的网易 Minecraft
  模组复用公共 UI、HUD 按钮、选轮、虚拟工具、公告、权限、资源选择器、指令库和跨存档 Provider，
  以及修改前置公共接口时检查调用方兼容性。独立模组的通用开发不必加载。
---

# DAGUOMIAO_API_MOD 前置接入

此前置为多个业务模组提供共享能力。先定位现有公共入口，再决定是否需要实现新逻辑；不要从某个业务模组复制一份已由前置提供的组件。

## 源码定位与边界

于 2026-09-16 对照本地 HEAD `a46991e` 及当前未提交工作树更新。虚拟工具、公告等已有提交；全量跨存档即时应用、分组列表注册调整等仍含工作树变化，不代表发布包已包含。接入时核对实际加载版本，特别是旧版跨存档仍可能采用重进世界后恢复的流程。

当前源码位置：`C:/Users/cat/Desktop/DAGUOMIAO_API_MOD/DAGUOMIAO_API_MOD`。其他机器优先使用用户指定的前置仓库；路径不存在时查找实际源码，不能假定所有环境都有该绝对路径。

以下路径均相对此仓库：

- 脚本根：`DAGUOMIAO_API_MODB/DAGUOMIAO_API_MODScripts/`。
- `modMain.py`、`miao_Config.py`：系统注册名、配置键和公共 UI namespace。
- `DAGUOMIAO_API_MODClientSystem/DAGUOMIAO_API_MODClientSystem.py`：客户端公共入口；`utils.py`：控制器实现、参数和用例。
- `DAGUOMIAO_API_MODServerSystem/DAGUOMIAO_API_MODServerSystem.py`：服务端公共入口；同目录 `AnyEvent.py`、`ContData.py`、`GlobalConfig.py`、`CommandLibrary.py`、`CrossSaveManager.py` 分别处理请求、数据、配置、指令队列和迁移。
- `DAGUOMIAO_API_MODR/ui/DAGUOMIAO_API_MOD_common.json`：公共组件；同目录 `_ui_defs.json` 确认实际资源注册。

先检查相关仓库 `AGENTS.md` 和 Git 状态。业务接入通常只改业务模组；只有任务需要扩展共享能力时才改前置，并检查受影响调用方。保留现有未提交改动。

## 获取系统

客户端通过 `clientApi.GetSystem('DAGUOMIAO_API_MOD', 'DAGUOMIAO_API_MODClientSystem')` 获取实例；服务端对应 `serverApi.GetSystem('DAGUOMIAO_API_MOD', 'DAGUOMIAO_API_MODServerSystem')`。

系统尚未注册时可能返回 `None`。按业务生命周期重新获取，并对必需功能给出明确的缺失提示；不要因一次获取失败永久禁用。兼容旧前置时核对所需方法是否存在，不能静默报告成功。

`API_` 是常用公共命名，但 `RegisterItemPicker`、`ResiPopup` 等保留名称也是现有入口。不要改成猜测的 `API_` 名，也不要把这些方法当成 ModSDK 内置方法。优先通过系统实例调用，避免直接依赖 `utils` 内部类或私有属性。

## 按任务读取

- 公共面板、列表、物品/实体选择、UI 迁移：读 [references/ui.md](references/ui.md)。JsonUI 语法与视觉规范可结合技能库中的 `jsonui`、`modui`；公共 API 参数以实际源码为准。
- 独立数值滑块及 EditBox 联动：读 [references/slider.md](references/slider.md)。
- 八槽选轮、贴图/音效选择、配置入口注册：读 [references/selectors.md](references/selectors.md)。这些实现已拆到 `selection_wheel_control.py`、`asset_registry.py` 等文件，不只在 `utils.py` 中。
- 服务端调用、指令接管、配置、跨存档：读 [references/server.md](references/server.md)。
- 奇异宝典虚拟工具的双端注册：读 [references/virtual-tools.md](references/virtual-tools.md)。
- 模组更新公告、服务器公告及权限区别：读 [references/announcements.md](references/announcements.md)。

只读取当前能力对应的方法、实现与调用点，不必每次加载完整 `utils.py`。可用 `rg -n 'def API_|def Register|def Open'` 定位，再阅读函数体、返回值和调用样例。引用中列出的 API 名是检索入口，不代表完整签名。

## 兼容与验证

- Mod 脚本保持 Python 2.7；区分客户端展示、服务端权威状态与可选的 `custom_attr`、`customeconomy` 联动。
- 公共变更保留旧参数位置、关键字、返回结构、回调含义、JsonUI namespace 和存档键；需要迁移时明确旧格式读取与新格式写入策略。
- 不因复用前置而批量删除业务模组旧实现；先确认所有引用、旧版兼容分支和共享路由是否仍在使用。
- 运行与改动相称的静态检查。真实 UI、网络回调、重进世界及存档恢复效果必须在加载正确前置和业务包的 Minecraft 中验证；最终区分已验证与未验证项。
