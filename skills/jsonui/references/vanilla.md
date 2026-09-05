# 原版 JsonUI 补充与源码检索

## 来源和适用范围

根据用户提供的 `bedrock-samples-v1.26.40.27-preview-full/resource_pack/ui/.miao/jsonui/` 专题资料整理，2026-09-05 核对了部分对应原版源码。本文件保留可复用的判断方法，不把专题中的出现次数、属性枚举或性能推测当作完整引擎规范。

本地资料根：`C:/Users/cat/Desktop/bedrock-samples-v1.26.40.27-preview-full/resource_pack/ui/.miao/jsonui`；原版源码是其上两级 `ui/`。路径失效时使用目标版本的资源包源码。以下专题文件名用于按需查找，不要求每次完整加载资料。

这是国际版 **v1.26.40.27-preview** 的源码样本。迁移到网易版前核对实际引擎、加载文件及 ModSDK；某属性在样本中零次出现不能证明引擎不支持。源码中出现一种写法也不能证明所有自建 screen 都拥有其引擎数据源。

## 变量与绑定：先确认谁提供数据

- `$` 用于模板配置、表达式和变量传递，`#` 引用运行时属性或数据绑定，`@` 引用模板或动画。原版数据可以由引擎提供，网易自定义数据还可由 Python ViewBinder 提供；看到 `#xxx` 不代表必须写一个 Python getter。
- `$name|default` 提供可由使用方覆盖的默认值。参数可能传入后代模板；核对中间层是否重定义同名变量，不要将参数定义在无法覆盖目标的子控件上。
- 变量不仅能表示 text 或 size，还能供继承目标、控件名、bindings 数组、property_bag 使用。可在 `ui_common.json` 搜索 `default@$slider_box_layout`、`$dropdown_name@$dropdown_toggle` 和 `$button_bindings` 查看具体上下文。
- `variables` + `requires` 适合在构建界面时选择平台布局；`ignored` 用于排除构建时不需要的控件或绑定。需要游戏过程中切换的状态仍使用运行时绑定，不能为优化而把可切换控件排除掉。
- 动态拼接绑定名称只是在选择名称，并不会自动注册数据源。Python 注册名、集合名、JsonUI 拼接结果必须一致。

原始专题：`04-变量系统.md`、`05-表达式与引擎全局变量.md`、`06-数据绑定基础.md`。

## 跨控件与集合上下文

值绑定与上下文绑定分开排查：

| 需求 | 检索字段 | 排查重点 |
|---|---|---|
| 将数据映射到内置属性 | `binding_name_override` | 源数据类型、目标控件是否支持该属性 |
| 读取另一控件的值 | `binding_type: view`、`source_control_name`、`source_property_name`、`target_property_name` | 源控件真实名称及解析范围；按层级决定 `resolve_sibling_scope` |
| 逐行取数据 | `binding_type: collection`、`binding_collection_name` | 数据源是否存在、集合是否匹配 |
| 携带当前行上下文 | `binding_type: collection_details` | 可不写 binding_name；检查模板是否已传递上下文 |
| 固定选择集合的一项 | `collection_index` | 索引有效性，与动态列表行索引区分 |
| 嵌套集合 | `binding_collection_prefix` | 每层前缀和集合绑定是否对应 |

不要把“原版某屏可绑定的属性”整理成任意控件都能写入的 API。可在 `server_form.json` 搜索 `resolve_sibling_scope`，在 `ui_common.json` 搜索 `collection_details` 阅读真实模板。网易按钮与 Toggle 的回调参数继续按现有 guide 及实际控制器核对。

原始专题：`07-深层绑定.md`、`08-隐藏绑定速查表.md`、`11-集合与列表.md`。

## 工厂和普通动态控件不是同一种入口

原版有 `type: factory` 配合 `control_ids` / `control_name`，也有容器上的 `factory` 对象。工厂标识、可生成的 control id 和数据来源要一起核对；只复制 JSON 或自取一个 factory.name，并不能获得原版引擎行为。

定位示例：

- `server_form.json`：`server_form_factory` 和 `control_ids`，观察引擎表单类型与模板的映射。
- `hud_screen.json`：`hud_tip_text_factory`，观察单模板工厂。
- `chat_screen.json`：`messages_factory`，观察列表工厂和子控件数量限制。
- `coin_purchase_screen.json`：`factory_variables`，观察向生成控件传递参数。

普通业务列表优先使用项目已有 grid / stack_grid / 前置分组列表；只有目标确实接入原版工厂时才复用其机制。工厂生成的子控件所需变量应检查 `factory_variables`，不要未经核对就依赖普通模板的变量传递行为。

原始专题：`10-工厂模式.md`、`11-集合与列表.md`。

## 输入与焦点

同一业务动作可能同时需要指针点击和键盘/手柄确认。查 `ui_common.json` 中 `button.menu_select` 的 pressed 映射与 `button.menu_ok` 的 focused 映射，不要只测试鼠标点击就宣称支持所有输入设备。

导航问题查 `focus_identifier`、`focus_change_*`、`focus_enabled`、`focus_container`；动态列表关注焦点标识是否唯一，以及条目删除、隐藏或禁用后的跳转目标。拖拽抬起事件丢失时查 `button_up_right_of_first_refusal` 和输入作用域，不要给所有按钮无条件追加抢占设置。

原始专题：`12-输入按键与焦点.md`。渲染器、screen 属性与 TTS 查 `14-渲染器-屏幕-TTS.md`，并确认目标版本及引擎支持的数据源。

## 继承、覆盖与性能的边界

- 改原版 UI 前先确认目标文件仍被当前游戏加载；有文件不代表该页面还走这个 JsonUI 实现。
- 优先做满足需求的局部改动，避免复制整个原版文件。专题介绍了 `modifications` 和深层路径覆盖，但它们不来自本批原版源码中的实例；使用前另外核实目标版本语法与加载行为，不能将其称为唯一可用方案。
- 覆盖公共模板会影响所有引用它的实例；只改某个页面时不要为减少路径依赖而扩大修改范围。继承时替换 controls / bindings 前检查原有数组与插槽契约，避免丢失原功能。
- 九宫格可能涉及贴图配套元数据，也可能由项目公共控件暴露参数；不把专题中的“只能写在贴图 JSON”用于否定网易前置现有的 nineslice 参数。
- `ignored`、隐藏、删除空 panel 或减少绑定各有语义成本。空 panel 可能是挂载点；删除前查脚本路径和布局引用。改变 binding_condition 前查数据更新时机，不把重开旧数据一律归咎于绑定条件。
- 性能结论来自测量：区分初次打开、重复打开、切页与数据刷新，记录实际加载的资源和操作。出现次数和静态语法检查不是 FPS 或运行耗时证据。

原始专题：`09-引用与复用.md`、`15-隐藏用法与冷门技巧.md`、`16-覆盖原版UI与性能避坑.md`。

## 其他专题入口

| 查询主题 | 资料文件 |
|---|---|
| 文件结构、符号与注册 | `01-文件体系与核心符号.md` |
| 控件类型及其原版用例 | `02-控件类型总表.md` |
| 布局、尺寸单位与循环依赖 | `03-布局与尺寸单位.md` |
| 动画链与屏幕转场 | `13-动画系统.md` |
| 网易扩展、ViewBinder、集合索引 | `17-网易中国版差异.md`；具体 SDK 用法另行核对 |
| 原版文件到 namespace 的定位 | `18-附录-命名空间对照表.md`；以目标文件 namespace 为准 |

专题中的 JSONC 示例可能带注释或省略号，只作阅读参考；写入项目时使用完整结构及目标项目支持的格式。
