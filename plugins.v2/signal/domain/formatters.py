"""Pure formatting helpers extracted from the main plugin class.

These are stateless @staticmethod / @classmethod utilities. They live in
``FormattersMixin`` so existing ``self.`` / ``cls.`` / ``Signal.``
call sites resolve unchanged via MRO.
"""

import re
from typing import Any, List, Tuple

from app.schemas import NotificationType

from . import site_helpers, html_utils


class FormattersMixin:
    """Mixin bundling all pure formatting / normalisation helpers."""

    @staticmethod
    def _html_escape(value: Any) -> str:
        return html_utils.html_escape(value)

    @staticmethod
    def _match_text(pattern: str, text: str) -> str:
        return html_utils.match_text(pattern, text)

    @staticmethod
    def _clip_telegram_html(value: str, limit: int = 32768) -> str:
        return html_utils.clip_telegram_html(value, limit)

    @staticmethod
    def _display_width(text: str) -> int:
        width = 0
        for ch in str(text or ""):
            width += 1 if ch == "\u00a0" else (2 if ord(ch) > 127 else 1)
        return width

    @classmethod
    def _pad_display(cls, text: str, width: int) -> str:
        pad = max(0, width - cls._display_width(text))
        full, half = divmod(pad, 2)
        tail = ("　" * full) + ("\u00a0" if half else "")
        return f"{text}{tail}"

    @staticmethod
    def _format_bytes(value: int) -> str:
        size = float(value or 0)
        for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
            if size < 1024 or unit == "PB":
                return f"{int(size)} {unit}" if unit == "B" else f"{size:.2f} {unit}"
            size /= 1024
        return "0 B"

    @staticmethod
    def _format_compact_bytes(size: Any) -> str:
        return site_helpers.format_compact_bytes(size)

    @staticmethod
    def _format_duration(seconds: Any) -> str:
        return site_helpers.format_duration(seconds)

    @staticmethod
    def _format_metric_number(value: Any) -> str:
        return site_helpers.format_metric_number(value)

    @staticmethod
    def _normalize_version(value: Any) -> str:
        text = str(value or "").strip()
        return text[1:] if text.startswith("v") else text

    @staticmethod
    def _normalize_day(value: Any) -> str:
        if value in (None, ""):
            return ""
        try:
            if hasattr(value, "strftime"):
                return value.strftime("%Y-%m-%d")
            text = str(value).strip()
            match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
            if match:
                year, month, day = match.groups()
                return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
            return text[:10]
        except Exception:
            return str(value or "").strip()[:10]

    @staticmethod
    def _normalize_compact_unit(unit: str) -> str:
        return site_helpers.normalize_compact_unit(unit)

    @staticmethod
    def _backend_version_value() -> str:
        try:
            from version import APP_VERSION
            return str(APP_VERSION or "")
        except Exception:
            return ""

    @staticmethod
    def _frontend_backend_version_line() -> str:
        try:
            from version import APP_VERSION, FRONTEND_VERSION
            # 显示格式：前端版本 / 后端版本（后端版本可能有 -1 等构建号后缀）
            return f"{FRONTEND_VERSION} / {APP_VERSION}"
        except Exception as err:
            return f"版本读取失败：{err}"

    @staticmethod
    def _slug(name: str) -> str:
        return {"融合卡刷新": "fusion_card_refresh", "订阅提醒": "subscribe_reminder", "订阅追新": "subscribe_reminder", "健康巡查": "health_check", "站点数据统计": "site_stat", "日志清理": "log_clean", "日志清理预览": "log_clean_preview", "自动备份": "backup", "插件库更新": "market_update", "插件库同步": "market_update", "插件更新": "plugin_update_reminder", "插件更新提醒": "plugin_update_reminder", "插件自动安装": "plugin_auto_install", "更新状态预览": "update_preview", "系统更新检查": "update_preview", "主程序更新检查": "update_preview", "MoviePilot更新检查": "update_preview", "插件治理预览": "plugin_uninstall_preview", "插件卸载预览": "plugin_uninstall_preview", "插件残留治理": "plugin_uninstall", "插件卸载": "plugin_uninstall", "自动删种": "seed_clean", "订阅规则填充": "subfill", "清理填充历史": "subfill_clear_history", "清理已处理": "subfill_clear_handled", "种子打标签": "downloader_helper", "下载器助手": "downloader_helper"}.get(name, "task")

    @staticmethod
    def _parse_csv(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(x).strip() for x in value if str(x).strip()]
        return [x.strip() for x in str(value or "").split(",") if x.strip()]

    @staticmethod
    def _unique_keep_order(items: List[Any]) -> List[str]:
        return site_helpers.unique_keep_order(items)

    @staticmethod
    def _dedupe_pairs(items: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        seen = set()
        result = []
        for label, path in items or []:
            clean = str(path or "").strip()
            if not clean or clean in seen:
                continue
            seen.add(clean)
            result.append((label, clean))
        return result

    @staticmethod
    def _dedupe_directory_entries(items: List[Tuple[str, str, Any]]) -> List[Tuple[str, str, Any]]:
        seen = set()
        result = []
        for label, path, storage in items or []:
            clean = str(path or "").strip()
            if not clean or clean in seen:
                continue
            seen.add(clean)
            result.append((label, clean, storage))
        return result

    @staticmethod
    def _is_local_storage(storage: Any) -> bool:
        name = str(storage or "").strip().lower()
        return name in ("", "local", "本地")

    @staticmethod
    def _episode_ranges(eps: List[int]) -> str:
        ranges = []
        i = 0
        while i < len(eps):
            start = end = eps[i]
            while i + 1 < len(eps) and eps[i + 1] == eps[i] + 1:
                i += 1
                end = eps[i]
            ranges.append(f"E{start:02d}" if start == end else f"E{start:02d}-E{end:02d}")
            i += 1
        return ",".join(ranges)

    @staticmethod
    def _safe_int(value: Any, default: int, minimum: int) -> int:
        try:
            number = int(value)
            return number if number >= minimum else default
        except Exception:
            return default

    @staticmethod
    def _notification_type(value: Any, default: str = "Plugin"):
        aliases = {
            "下载": "Download",
            "资源下载": "Download",
            "整理": "Organize",
            "整理入库": "Organize",
            "订阅": "Subscribe",
            "站点": "SiteMessage",
            "站点消息": "SiteMessage",
            "媒体服务器": "MediaServer",
            "手动": "Manual",
            "手动处理": "Manual",
            "插件": "Plugin",
            "智能体": "Agent",
            "其他": "Other",
            "其它": "Other",
        }
        key = aliases.get(str(value or default or "Plugin").strip(), str(value or default or "Plugin").strip())
        fallback_key = aliases.get(str(default or "Plugin").strip(), str(default or "Plugin").strip()) or "Plugin"
        for candidate in (key, fallback_key, "Plugin"):
            try:
                return NotificationType[candidate]
            except Exception:
                pass
            try:
                return NotificationType.__getitem__(candidate)
            except Exception:
                pass
            try:
                return NotificationType(candidate)
            except Exception:
                pass
            try:
                for item in NotificationType:
                    if getattr(item, "name", "").lower() == candidate.lower() or str(getattr(item, "value", "")) == candidate:
                        return item
            except Exception:
                pass
            if hasattr(NotificationType, candidate):
                return getattr(NotificationType, candidate)
        return getattr(NotificationType, "Plugin", "Plugin")

    @staticmethod
    def _payload_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() not in {"", "0", "false", "no", "off", "否", "关", "关闭"}
        return bool(value)
