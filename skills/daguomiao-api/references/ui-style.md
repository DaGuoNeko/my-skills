# UI 风格对齐前置

适用于依赖 `DAGUOMIAO_API_MOD` 的项目。**视觉跟前置走，布局由 AI 按内容决定。**
技能里不抄组件参数：控件、参数、贴图一律用下面的脚本从前置当前源码读取，前置更新后自动对齐。

## 查前置当前的组件和贴图

脚本：`../scripts/ui_catalog.py`（相对本文件；前置不在默认路径时加 `--root <前置仓库>`）。

| 要查什么 | 命令 |
|---|---|
| 公共控件清单（可加关键词过滤） | `python ui_catalog.py list [关键词]` |
| 某个控件的 `$` 参数默认值、子控件、贴图 | `python ui_catalog.py show <控件名>`，提示继承时再 `show` 父控件 |
| 控件原始 JSON | `python ui_catalog.py raw <控件名>` |
| 可用贴图（直接输出可粘贴的路径写法） | `python ui_catalog.py textures [关键词]` |
| 前置自带界面（同风格样板） | `python ui_catalog.py screens` |

做 UI 前先跑一次 `list`，输出第一行是前置版本；参数以 `show` 的结果为准，不凭记忆写。

## 样板界面

先找和需求最接近的前置界面，读它的 JSON（`DAGUOMIAO_API_MODR/ui/`）照着组织控件，再按内容调整布局：

| 前置界面 | 版式 |
|---|---|
| `config_book_selector_screen`（奇异宝典） | 标题栏 + 卡片网格 + 底部说明行 |
| `asset_selector_screen`（贴图/音效选择） | 标题栏 + 顶部标签页 + 左侧分组列表 + 右侧可搜索列表 |
| `command_library_screen`、`world_announcement_editor_screen` | 分组列表 + 行编辑 |
| `cross_save_screen` | 数据行列表 + 行内展开 |
| `update_announcement_screen` | 标题列表 + 正文阅读 |

## 元素对照

用 `show` 核对参数后再继承，写法 `"xxx@DAGUOMIAO_API_MOD_common.<控件名>"`：

| 界面元素 | 前置做法 |
|---|---|
| 背景模糊 | `API_AcquireScreenBlur` / `API_ReleaseScreenBlur` 按 ScreenNode 成对调用（见 [ui.md](ui.md)） |
| 面板底板 | 照样板界面的根面板写法；贴图从 `textures` 里选，不自造 |
| 标题栏 | 左侧图标 + `text` 标题，右侧 `newbutt2_close`（参考 `asset_selector_screen` 的 `title_bar`） |
| 按钮 | `newbutt2`（可拖动的用 `newbutt2_movebtn`） |
| 文字 | `text`；说明文字 `Help_Text` |
| 卡片网格、滚动列表 | `M_Scroll_View_Grid_Panel`、`_Grid` / `_Grid_Panel`、`_BASE_GRID_ITEM` |
| 分组/分类列表 | `M_GROUPED_LIST`（接入见 ui.md 的分组列表） |
| 输入框、搜索框 | `M_edit_box` |
| 开关、标签页 | `M_toggle`、`M_Text2_toggle` |
| 收藏、图标选择行 | `sel_ico_items_item`、`sel_ico_favorite_item` |
| 弹窗、提示、加载 | 走 ui.md 的公共入口（`ResiPopup`、`ShowTipsPanel`、`M_loading_panel` 等），不另写 |

表里没有的元素：`list <关键词>` 搜一下前置是否已有，再决定。

## 布局：AI 决定，守住底线

- 按内容选版式：少量入口用卡片网格；条目多用可滚动列表并加搜索；有分类加左侧分组列表或顶部标签页；可组合。
- 标题栏和关闭按钮位置固定；边距、间距、行高、字号沿用最接近的样板界面数值，不自定一套。
- 列表、长文本必须可滚动；长名称考虑截断或换行。
- PC 与手机都要能点：按钮不小于样板界面的按钮尺寸。
- 同类界面优先沿用前置已有版式，让玩家觉得是同一套 UI。

## 禁止

- 不新画贴图、不自定义颜色和字体；前置没有的，先问用户或建议加进前置。
- 不把前置贴图复制进业务资源包；不在业务模组里重建前置已有的公共控件。
- 不直接写颜色数值和贴图尺寸来模仿前置外观，一律继承前置控件。

## 验收

用 game-ops 进游戏，`capture_client_window` 截图，和最接近的前置样板界面对比：底板、标题栏、按钮、字体、配色一致；再用 `jsonui_debugger` 查控件层级没有错位。
