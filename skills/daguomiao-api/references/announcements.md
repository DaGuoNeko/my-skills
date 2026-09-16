# 公告接入

2026-09-16 核对客户端 announcement_registry.py、update_announcement_screen.py、ClientSystem，以及服务端 WorldAnnouncementManager.py 的公开入口。模组更新与服务器公告共用界面但数据来源、受众、权限不同。

## 模组更新公告

监听前置客户端 `UpdateAnnouncementRegisterRequest`，然后调用：

- `API_RegisterUpdateAnnouncements(provider_id, provider_name, announcements)` 替换该提供者当前会话的完整公告表。
- `API_RegisterUpdateAnnouncement(provider_id, provider_name, announcement_id, revision, title, options=None)` 新增或覆盖单条。
- `API_UnregisterUpdateAnnouncements(provider_id)` 注销；`API_GetRegisteredUpdateAnnouncements()` 读取副本。

announcement 条目使用 id、revision、title，可提供 detail_title、subtitle、icon、banner、content、detail_callback、sort_order、auto_popup、remember_seen、enabled。revision 使用字符串；id/revision 不含冒号。seen_key 为 `mod:provider_id:announcement_id:revision`，新版本要重新提示时更新 revision，不随机改 ID。

批量注册会跳过无效条目并在成功消息中提示忽略数量，检查 `(state, message)`。公告内容是会话注册数据，不会永久复制成服务端公告；已读状态另行记录。

`API_OpenModUpdateAnnouncementScreen(options=None)` 面向实际房主或 OP；`API_OpenServerAnnouncementScreen(options=None)` 面向全部玩家的世界公告。优先调用这两个明确入口，不用通用打开接口绕过受众判断。

预览模式不写已读；正常新屏在 Create 成功后由前置确认展示状态。不要在请求打开之前自行标记所有公告已读。detail_callback 是无参回调；涉及跳转后的关闭行为继续核对 update_announcement_screen.py。

## 服务器公告草稿与发布

客户端 `API_OpenWorldAnnouncementEditor()` 打开编辑器。服务端维护世界公告，草稿及管理操作采用房主级权限，不能仅靠客户端隐藏按钮。

服务端入口包括 GetWorldAnnouncementData、GetWorldAnnouncementDraft、GetWorldAnnouncementEditorData、CreateWorldAnnouncementDraft、SaveWorldAnnouncementDraft、PublishWorldAnnouncement、RepublishWorldAnnouncement、DisableWorldAnnouncement、DeleteWorldAnnouncement（均带 `API_` 前缀）。

- 保存草稿不触发玩家弹窗；发布或重发才改变发布状态。
- Save/Publish 携带 draft_id、base_revision，重发携带 publish_id、base_notice_revision，按源码处理并发冲突，不用旧 UI 缓存覆盖新修订。
- 重发覆盖同一历史公告并递增全服未读修订；停用通知保留发布历史，删除则指定记录类型及 ID，不能互相替代。
- 世界公告身份由当前世界维护；全量跨存档也保护 announcement_identity，避免沿用源世界已读身份。

实际房主、被授权房主级玩家和 OP 的判断不同，见 [服务端权限](server.md)。
