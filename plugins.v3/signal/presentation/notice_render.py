"""Small contextual keyboards; never a Telegram control menu."""
from ..domain.notice_actions import PAGE_SIZE, callback_data, split_text


class NoticeRenderMixin:
    @staticmethod
    def _notice_render(record, **kwargs):
        return render_notice(record, **kwargs)


def render_notice(record, *, native_update=False, host_url=""):
    nonce = record["nonce"]
    def button(text, action, index=None):
        return {"text": text, "callback_data": callback_data(nonce, action, index)}
    text = str(record.get("text") or "")
    status = record.get("status", "ready")
    if status in {"running", "pending", "uncertain", "handed_off"}:
        return split_text(text)[0], []
    if record.get("view") == "details":
        pages = split_text(record.get("detail") or text)
        page = min(max(int(record.get("page", 0)), 0), len(pages) - 1)
        rows = []
        navigation = []
        if page:
            navigation.append(button("上一页", "page", page - 1))
        if page + 1 < len(pages):
            navigation.append(button("下一页", "page", page + 1))
        if navigation:
            rows.append(navigation)
        rows.append([button("返回通知", "back")])
        return f"{pages[page]}\n\n第 {page + 1}/{len(pages)} 页", rows
    kind = record["kind"]
    rows = []
    if kind == "plugin_update" and status == "ready":
        items = record.get("payload", {}).get("plugins", [])
        page = min(max(int(record.get("page", 0)), 0), max(0, (len(items) - 1) // PAGE_SIZE))
        for index in range(page * PAGE_SIZE, min(len(items), (page + 1) * PAGE_SIZE)):
            item = items[index]
            if item.get("completed") or item.get("blocked"):
                continue
            label = str(item.get("name") or item.get("id") or "插件")[:32]
            rows.append([button(f"更新 {label}", "install", index)])
        nav = []
        if page:
            nav.append(button("上一页插件", "page", page - 1))
        if (page + 1) * PAGE_SIZE < len(items):
            nav.append(button("下一页插件", "page", page + 1))
        if nav:
            rows.append(nav)
        if any(not item.get("completed") and not item.get("blocked") for item in items):
            rows.append([button("1 小时后提醒", "remind"), button("忽略这些版本", "ignore")])
    elif kind == "mp_update":
        if native_update and status == "ready":
            rows.append([button("查看并处理更新", "mp")])
        elif host_url:
            rows.append([{"text": "打开 MoviePilot 更新设置", "url": host_url}])
        else:
            text += "\n当前宿主不支持通知内更新，请从 MoviePilot 页面处理。"
    elif kind == "site_stat":
        rows.append([button("刷新数据", "refresh")])
    rows.append([button("查看更新说明" if kind == "plugin_update" else "查看明细", "details")])
    parts = split_text(text)
    if len(parts) > 1:
        text = parts[0] + "\n…完整内容请点查看明细。"
    return text or "暂无数据", rows
