"""MoviePilot and Telegram ports for ordinary, source-bound notifications."""
from urllib.parse import urljoin, urlsplit, urlunsplit


def field(value, key, default=None):
    return value.get(key, default) if isinstance(value, dict) else getattr(value, key, default)


def enabled(value):
    return str(value).strip().lower() not in {"false", "0", "no", "off", "none", ""}


def notification_configs():
    """Read host notification configs across supported MoviePilot SDK layouts."""
    try:
        from app.runtime.extensions.service import ServiceConfigHelper
        return ServiceConfigHelper.get_notification_configs() or []
    except (ImportError, AttributeError):
        pass
    try:
        from app.sdk.services import ServiceConfigHelper
        return ServiceConfigHelper.get_notification_configs() or []
    except (ImportError, AttributeError):
        pass
    from app.db.oper.systemconfig import SystemConfigOper
    from app.schemas.types import SystemConfigKey
    return SystemConfigOper().get(SystemConfigKey.Notifications) or []


def notification_targets(mtype):
    configs = notification_configs()
    kind = str(field(mtype, "value", mtype))
    targets = []
    for conf in configs:
        name = str(field(conf, "name", "") or "").strip()
        if not name or not enabled(field(conf, "enabled", False)):
            continue
        switches = field(conf, "switchs", []) or []
        if isinstance(switches, str):
            switches = [part.strip() for part in switches.split(",")]
        if kind not in {str(field(item, "value", item)) for item in switches}:
            continue
        config = field(conf, "config", {}) or {}
        channel = str(field(conf, "type", "") or "").lower()
        chat = str(field(config, "TELEGRAM_CHAT_ID", "") or "").strip()
        admins = {part.strip() for part in str(field(config, "TELEGRAM_ADMINS", "") or "").split(",") if part.strip().isdigit()}
        if chat.isdigit() and int(chat) > 0:
            admins.add(chat)
        targets.append({"source": name, "type": channel, "chat_id": chat, "admins": admins,
                        "token": str(field(config, "TELEGRAM_TOKEN", "") or "").strip(),
                        "api_url": str(field(config, "API_URL", "") or "").strip()})
    return targets


def can_interact(target):
    return (target.get("type") == "telegram" and bool(target.get("token"))
            and bool(target.get("admins")) and bool(target.get("chat_id")))


def enqueue_notice(owner, nonce):
    """Use the host's notification time windows before first delivery/reminders."""
    try:
        from app.application.messaging.message import MessageQueueManager
        queue = MessageQueueManager()
        bind = getattr(queue, "bind", None)
        if not callable(bind):
            return False
        bind(owner._notice_publish).send_message(nonce)
        return True
    except (ImportError, AttributeError):
        return False


def telegram_message(owner, target, text, buttons, message_id=None):
    method = "editMessageText" if message_id else "sendMessage"
    payload = {"chat_id": target["chat_id"], "text": text,
               "reply_markup": {"inline_keyboard": buttons}, "link_preview_options": {"is_disabled": True}}
    if message_id:
        payload["message_id"] = int(message_id)
    response, session = None, None
    try:
        api_url = target.get("api_url")
        if api_url:
            if urlsplit(api_url).scheme not in {"http", "https"} or not urlsplit(api_url).netloc:
                raise RuntimeError("Telegram API 地址无效")
            import requests
            session = requests.Session()
            session.trust_env = False
            response = session.post(urljoin(api_url, f"/bot{target['token']}/{method}"), json=payload,
                                    timeout=15, proxies=None)
        else:
            response = owner._telegram_http_post_json(f"https://api.telegram.org/bot{target['token']}/{method}", payload, timeout=15)
        data = response.json() if response is not None else {}
        if data.get("ok"):
            result = data.get("result") or {}
            return int(result.get("message_id") or message_id or 0)
        description = str(data.get("description") or "").lower()
        if message_id and "message is not modified" in description:
            return int(message_id)
        # A missing old message can safely receive one replacement result.
        if message_id and ("message to edit not found" in description or "message can't be edited" in description):
            return telegram_message(owner, target, text, buttons)
        raise RuntimeError("Telegram 未接受通知，请检查通知通道")
    except Exception:
        # requests exceptions contain the Bot URL; never propagate it to users/logs.
        raise RuntimeError("Telegram 通知发送或更新失败") from None
    finally:
        close = getattr(response, "close", None)
        if callable(close):
            close()
        if session is not None:
            session.close()


def plugin_manager_class():
    """Resolve the host PluginManager across supported MoviePilot SDK layouts."""
    try:
        from app.sdk.plugins import PluginManager
        return PluginManager
    except ImportError:
        pass
    try:
        from app.sdk.plugin.manager import PluginManager
        return PluginManager
    except ImportError:
        from app.runtime.extensions.plugin.manager import PluginManager
        return PluginManager


def installed_plugin_versions():
    return {str(item.id): str(item.plugin_version) for item in plugin_manager_class()().get_local_plugins() or []}


def moviepilot_update_available():
    try:
        from app.application.messaging.update import update_interaction_manager
        from app.chain.system import SystemChain
        return callable(getattr(update_interaction_manager, "create_or_replace", None)) and callable(getattr(SystemChain, "handle_update_callback_interaction", None))
    except (ImportError, AttributeError):
        return False


def start_moviepilot_update(context):
    from app.application.messaging.update import update_interaction_manager
    from app.chain.system import SystemChain
    from app.schemas.types import NotificationChannel
    channel = NotificationChannel.Telegram
    request = update_interaction_manager.create_or_replace(
        user_id=context["userid"], command="/update", channel=channel,
        source=context["source"], username=None)
    return SystemChain().handle_update_callback_interaction(
        callback_data=f"update:{request.request_id}:refresh", channel=channel,
        source=context["source"], userid=context["userid"], username=None,
        original_message_id=context["original_message_id"], original_chat_id=context["original_chat_id"])


def moviepilot_auto_anchor(owner):
    """Pick the Telegram admin used to anchor the host update interaction."""
    mtype = owner._notification_type(getattr(owner, "_mp_update_notify_type", "Plugin"))
    for target in notification_targets(mtype):
        if target.get("type") != "telegram":
            continue
        admins = sorted(str(item) for item in (target.get("admins") or []) if str(item).strip())
        if admins and target.get("chat_id"):
            return target, admins[0]
    return None, ""


def start_moviepilot_release_download(owner):
    """Start the host's official release download.

    Installation and restart stay user-confirmed: the host exposes progress only
    inside its own interaction session, so Signal cannot safely confirm readiness.
    Returns (started, message); any failure degrades to the manual flow.
    """
    if not moviepilot_update_available():
        return False, "当前宿主未提供插件可用的更新交互入口，已改为通知后手动更新"
    target, userid = moviepilot_auto_anchor(owner)
    if not target or not userid:
        return False, "未找到可用的 Telegram 管理员，无法自动开始下载"
    try:
        from app.application.messaging.update import update_interaction_manager
        from app.chain.system import SystemChain
        from app.schemas.types import NotificationChannel
        channel = NotificationChannel.Telegram
        request = update_interaction_manager.create_or_replace(
            user_id=userid, command="/update", channel=channel,
            source=target["source"], username=None)
        chain = SystemChain()
        payload = {"channel": channel, "source": target["source"], "userid": userid,
                   "username": None, "original_message_id": None, "original_chat_id": None}
        chain.handle_update_callback_interaction(
            callback_data=f"update:{request.request_id}:refresh", **payload)
        chain.handle_update_callback_interaction(
            callback_data=f"update:{request.request_id}:download", **payload)
        return True, "已自动开始下载更新包，下载完成后请在通知里确认重启"
    except Exception:
        return False, "当前宿主自动更新入口不可用，已改为通知后手动更新"


def moviepilot_url():
    try:
        from app.sdk.config import settings
        value = str(settings.MP_DOMAIN("#/settings"))
        parsed = urlsplit(value)
        if parsed.scheme in {"http", "https"} and parsed.netloc and not parsed.username and not parsed.password:
            return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", "/settings"))
        return ""
    except Exception:
        return ""
