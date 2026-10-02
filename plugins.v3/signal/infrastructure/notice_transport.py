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


def moviepilot_update_status():
    """Read the same release snapshot shown by the host; never start an update."""
    try:
        from app.adapters.system.update import system_update_manager
        return system_update_manager.get_status().model_dump()
    except (ImportError, AttributeError):
        return {}


def moviepilot_release_ports():
    """当前 V3 宿主移除了通知会话，但保留正式更新状态机与受管重启。"""
    try:
        from app.adapters.system.update import system_update_manager
        from app.sdk.services import SystemHelper
        if all(callable(getattr(system_update_manager, name, None)) for name in
               ("get_status", "check", "start_download", "request_install", "cancel_install")) and all(
                   callable(getattr(SystemHelper, name, None)) for name in ("can_restart", "restart")):
            return system_update_manager, SystemHelper
    except (ImportError, AttributeError):
        pass
    return None


def moviepilot_actor_allowed(context, *, target_source=None):
    """校验目标通道的管理员；融合卡允许同一 Bot 的另一通道转发回调。"""
    if str(context.get("channel") or "").lower() != "telegram":
        return False
    source = str(context.get("source") or "")
    if not source or target_source == "":
        return False
    configs = [conf for conf in notification_configs()
               if str(field(conf, "type", "")).lower() == "telegram" and enabled(field(conf, "enabled", False))]
    incoming = next((conf for conf in configs if str(field(conf, "name", "")) == source), None)
    target = next((conf for conf in configs if str(field(conf, "name", "")) == (target_source or source)), None)
    if incoming is None or target is None:
        return False
    config = field(target, "config", {}) or {}
    if source != (target_source or source):
        # 宿主可由群组通道的轮询器收到同 Bot 私聊回调。通道名称可以不同，
        # Bot 必须相同；权限仍只取卡片目标通道，不能借用来源通道管理员。
        token = str(field(config, "TELEGRAM_TOKEN", "") or "").strip()
        incoming_token = str(field(field(incoming, "config", {}) or {}, "TELEGRAM_TOKEN", "") or "").strip()
        if not token or incoming_token != token:
            return False
    chat = str(field(config, "TELEGRAM_CHAT_ID", "") or "").strip()
    admins = {v.strip() for v in str(field(config, "TELEGRAM_ADMINS", "") or "").split(",") if v.strip()}
    if chat.isdigit() and int(chat) > 0:
        admins.add(chat)
    return str(context.get("userid") or "") in admins and str(context.get("original_chat_id")) == chat


def moviepilot_release_action(step="open", version=""):
    """调用宿主正式状态机；首次打开只检查，安装必须匹配已确认版本。

    沿用宿主 SystemService 的环境校验、包校验和重启失败撤销流程。
    返回状态供卡内交互使用，不发送或替换另一条通知。
    """
    ports = moviepilot_release_ports()
    if not ports:
        raise RuntimeError("当前宿主更新接口不可用")
    manager, control = ports
    with manager._lock:
        status = manager.get_status().model_dump()
        if step in {"open", "check"}:
            if status.get("state") not in {"downloading", "ready", "installing"}:
                status = manager.check().model_dump()
        elif step == "status":
            pass
        elif step in {"download", "install"}:
            if not version or status.get("version") != version:
                return False, "目标版本已变化，请重新查看更新后确认。", status
            if not control.can_restart():
                return False, "当前运行环境不支持宿主受管更新。", status
            if step == "download":
                if status.get("state") != "available" or not status.get("can_update"):
                    return False, "更新状态已变化，请重新检查后确认下载。", status
                status = manager.start_download().model_dump()
            else:
                if status.get("state") != "ready" or not status.get("can_install"):
                    return False, "更新包尚未就绪，请刷新下载状态。", status
                prepared, message = manager.request_install()
                if not prepared:
                    return False, message, manager.get_status().model_dump()
                try:
                    ok, message = control.restart()
                except Exception:
                    manager.cancel_install("重启请求失败，已撤销安装")
                    raise
                if not ok:
                    manager.cancel_install(message or "重启请求失败")
                return bool(ok), message or "已确认重启安装 MoviePilot。", manager.get_status().model_dump()
        else:
            raise ValueError("未知更新操作")
    phase = status.get("state")
    messages = {"available": "发现 MoviePilot 更新，请确认是否下载。",
                "downloading": "更新包下载中，可刷新进度。",
                "ready": "更新包已校验，确认重启后安装。",
                "installing": "正在重启安装 MoviePilot。",
                "idle": "MoviePilot 已是最新版。"}
    if status.get("error") or phase == "failed":
        return False, str(status.get("error") or "更新操作失败，请重试检查。"), status
    return True, messages.get(phase, "已读取 MoviePilot 更新状态。"), status


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
