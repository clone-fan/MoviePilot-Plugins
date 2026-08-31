import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from app.core.config import settings
from app.log import logger
from app.utils.http import RequestUtils


class UpdateGovernanceMixin:
    """MoviePilot version checks, plugin market updates, and auto-update logic."""

    def _build_update_status(self) -> Dict[str, Any]:
        result = {"safe_mode": True, "note": "检查到 MoviePilot 后端或前端有更新时，只触发一次整体升级。", "moviepilot": {}}
        local = self._get_local_versions()
        result["moviepilot"].update(local)
        checks = []
        if "后端" in self._mp_update_types:
            checks.append(self._check_one_release("后端", "https://api.github.com/repos/jxxghp/MoviePilot/releases", local.get("backend_version")))
        if "前端" in self._mp_update_types:
            checks.append(self._check_one_release("前端", "https://api.github.com/repos/jxxghp/MoviePilot-Frontend/releases", local.get("frontend_version")))
        result["moviepilot"]["checks"] = checks
        result["moviepilot"]["has_update"] = any(x.get("has_update") for x in checks)
        return result

    @staticmethod
    def _dispatch_moviepilot_restart(data: Dict[str, Any]) -> None:
        mp = data.setdefault("moviepilot", {})
        try:
            from app.helper.system import SystemHelper
            SystemHelper.restart()
            mp["restart_dispatched"] = True
        except Exception as err:
            mp["restart_error"] = str(err)

    @staticmethod
    def _dispatch_moviepilot_upgrade(data: Dict[str, Any]) -> None:
        mp = data.setdefault("moviepilot", {})
        try:
            from app.helper.system import SystemHelper
            result = SystemHelper.upgrade(mode="release")
            if isinstance(result, tuple):
                ok, message = result
            else:
                ok, message = bool(result), ""
            mp["upgrade_dispatched"] = bool(ok)
            if message:
                mp["upgrade_message"] = str(message)
            if not ok:
                mp["upgrade_error"] = str(message or "MoviePilot 升级请求失败")
        except Exception as err:
            mp["upgrade_error"] = str(err)

    @staticmethod
    def _get_local_versions() -> Dict[str, Any]:
        data = {}
        try:
            from version import APP_VERSION, FRONTEND_VERSION
            data.update({"backend_version": str(APP_VERSION), "frontend_version": str(FRONTEND_VERSION)})
        except Exception as err:
            data["version_error"] = str(err)
        return data

    @staticmethod
    def _version_nums(value: Any) -> List[int]:
        return [int(x) for x in re.findall(r"\d+", str(value or ""))]

    def _check_one_release(self, label: str, url: str, local_version: Any) -> Dict[str, Any]:
        item = {"type": label, "local_version": str(local_version or "未知"), "latest_version": "", "has_update": False, "error": ""}
        try:
            response = RequestUtils(proxies=settings.PROXY, headers=settings.GITHUB_HEADERS).get_res(url)
            if not response:
                item["error"] = "未获取到 release 响应"
                return item
            releases = response.json() or []
            v2 = [r for r in releases if re.match(r"^v2\.", str(r.get("tag_name", "")))]
            if not v2:
                item["error"] = "未找到 v2 release"
                return item
            latest = sorted(v2, key=lambda r: self._version_nums(r.get("tag_name")))[-1]
            latest_version = str(latest.get("tag_name") or "")
            item.update({"latest_version": latest_version, "published_at": latest.get("published_at"), "body": (latest.get("body") or "")[:1000]})
            if self._version_nums(latest_version) > self._version_nums(local_version):
                item["has_update"] = True
        except Exception as err:
            item["error"] = str(err)
        return item

    @staticmethod
    def _format_update_status_text(data: Dict[str, Any]) -> str:
        mp = data.get("moviepilot") or {}
        lines = ["🔄 系统更新检查", f"⦁ 后端本地：{mp.get('backend_version', '未知')}", f"⦁ 前端本地：{mp.get('frontend_version', '未知')}"]
        for item in mp.get("checks") or []:
            status = "有更新" if item.get("has_update") else "无更新"
            if item.get("error"):
                status = f"异常：{item.get('error')}"
            lines.append(f"⦁ {item.get('type')}：{status}｜最新 {item.get('latest_version') or '未知'}")
        if mp.get("upgrade_dispatched"):
            lines.append(f"⦁ 更新执行：已触发 MoviePilot 升级重启{('｜' + str(mp.get('upgrade_message'))) if mp.get('upgrade_message') else ''}")
        elif mp.get("upgrade_error"):
            lines.append(f"⦁ 更新执行：失败｜{mp.get('upgrade_error')}")
        elif mp.get("restart_dispatched"):
            lines.append("⦁ 更新执行：已触发 MoviePilot 重启")
        elif mp.get("restart_error"):
            lines.append(f"⦁ 更新执行：失败｜{mp.get('restart_error')}")
        return "\n".join(lines)

    def _build_market_status(self) -> Dict[str, Any]:
        settings_markets = self._valid_markets_list(settings.PLUGIN_MARKET)
        last = self.get_data("last_market_update") or {}
        return {"status": "已直接接替", "note": "本插件直接同步插件库记录，不依赖原插件库更新推送插件。", "enabled": self._market_update_enabled, "cron": self._market_update_cron, "settings_count": len(settings_markets), "last_update": last.get("time"), "last_wiki_count": len(last.get("wiki_markets") or [])}

    def _build_market_update_status(self, apply: bool = False) -> Dict[str, Any]:
        blacklist = self._market_update_blacklist_list()
        blocked_addresses, blocked_hosts = self._market_blacklist_matchers(blacklist)
        discovered_markets = self._fetch_wiki_markets()
        settings_markets = self._valid_markets_list(settings.PLUGIN_MARKET)
        wiki_markets = [x for x in discovered_markets if not self._market_address_blocked(x, blocked_addresses, blocked_hosts)]
        kept_settings_markets = [x for x in settings_markets if not self._market_address_blocked(x, blocked_addresses, blocked_hosts)]
        blocked_from_settings = [x for x in settings_markets if self._market_address_blocked(x, blocked_addresses, blocked_hosts)]
        blocked_markets = self._dedupe([x for x in discovered_markets if self._market_address_blocked(x, blocked_addresses, blocked_hosts)] + blocked_from_settings)
        other_markets = [x for x in kept_settings_markets if x not in wiki_markets]
        write_markets = self._dedupe(wiki_markets + other_markets)
        last = self.get_data("last_market_update") or {}
        last_wiki = self._valid_markets_list(last.get("wiki_markets") or [])
        new_markets = [x for x in wiki_markets if x not in last_wiki and x not in settings_markets]
        has_update = set(wiki_markets) != set(last_wiki) or bool(new_markets)
        empty_write_blocked = not write_markets and bool(settings_markets)
        result = {"success": not empty_write_blocked, "dry_run": not apply, "has_update": has_update, "strategy": "sync", "legacy_strategy": self._market_update_strategy, "wiki_markets": wiki_markets, "settings_markets": settings_markets, "other_markets": other_markets, "write_markets": write_markets, "new_markets": new_markets, "blacklist": blacklist, "blocked_markets": blocked_markets, "blocked_from_settings": blocked_from_settings, "settings_written": False, "env_written": False}
        if empty_write_blocked:
            result["error"] = "黑名单过滤后插件库目标为空，未写入：为避免清空 MoviePilot 插件市场已中止本次同步"
            logger.error(f"插件库同步中止：黑名单过滤后目标为空，当前配置 {len(settings_markets)} 个库、拦截 {len(blocked_markets)} 个库")
            return result
        if apply:
            if write_markets != settings_markets:
                settings.PLUGIN_MARKET = ",".join(write_markets)
                result["settings_written"] = True
            result["env_written"] = self._write_app_env_key("PLUGIN_MARKET", ",".join(write_markets))
            self.save_data("last_market_update", {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "wiki_markets": wiki_markets, "settings_markets": settings_markets, "new_markets": new_markets, "has_update": has_update, "blacklist": blacklist, "blocked_markets": blocked_markets})
        return result

    def _market_update_blacklist_list(self) -> List[str]:
        return [str(item).strip() for item in (self._market_update_blacklist or []) if str(item).strip()]

    @staticmethod
    def _normalize_market_address(value: Any) -> str:
        text = str(value or "").strip().lower()
        if not text:
            return ""
        text = text.rstrip("/")
        if text.endswith(".git"):
            text = text[: -len(".git")].rstrip("/")
        return text

    @staticmethod
    def _market_blacklist_matchers(blacklist: Any) -> Tuple[Set[str], Set[str]]:
        addresses: Set[str] = set()
        hosts: Set[str] = set()
        for item in (blacklist or []):
            normalized = UpdateGovernanceMixin._normalize_market_address(item)
            if not normalized:
                continue
            addresses.add(normalized)
            bare = normalized.split("://", 1)[-1]
            if "/" not in bare:
                hosts.add(bare)
        return addresses, hosts

    @staticmethod
    def _market_address_blocked(address: Any, addresses: Set[str], hosts: Set[str]) -> bool:
        normalized = UpdateGovernanceMixin._normalize_market_address(address)
        if not normalized:
            return False
        if normalized in addresses:
            return True
        host = normalized.split("://", 1)[-1].split("/", 1)[0]
        return bool(host) and host in hosts

    def _fetch_wiki_markets(self) -> List[str]:
        url = "https://wiki.movie-pilot.org/zh/plugin"
        response = RequestUtils(proxies=settings.PROXY, timeout=15).get_res(url=url)
        if not response or response.status_code != 200:
            raise RuntimeError(f"插件库记录页面获取失败：{getattr(response, 'status_code', 'no_response')}")
        text = response.text or ""
        urls = re.findall(r"https?://[^\s\"'<>]+", text)
        markets = [u for u in urls if ("github" in u.lower() or "gitee" in u.lower() or "gitlab" in u.lower() or u.endswith("/"))]
        return self._valid_markets_list(self._dedupe(markets))

    @staticmethod
    def _valid_markets_list(value: Any) -> List[str]:
        raw = []
        if not value:
            return []
        if isinstance(value, str):
            raw = [x.strip() for x in value.split(",")]
        elif isinstance(value, dict):
            raw = [str(v).strip() for v in value.values()]
        elif isinstance(value, list):
            for item in value:
                raw.extend(UpdateGovernanceMixin._valid_markets_list(item))
        else:
            raw = [str(value).strip()]
        result = []
        for item in raw:
            if not item:
                continue
            result.append(item if item.endswith("/") else item + "/")
        return UpdateGovernanceMixin._dedupe(result)

    @staticmethod
    def _dedupe(items: List[str]) -> List[str]:
        seen = set()
        result = []
        for item in items or []:
            if item and item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @staticmethod
    def _write_app_env_key(key: str, value: str) -> bool:
        env_path = Path(settings.CONFIG_PATH) / "app.env"
        lines = []
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        prefix = key + "="
        replaced = False
        out = []
        for line in lines:
            if line.startswith(prefix):
                out.append(f"{key}={value}")
                replaced = True
            else:
                out.append(line)
        if not replaced:
            out.append(f"{key}={value}")
        rendered = "\n".join(out) + "\n"
        current = env_path.read_text(encoding="utf-8", errors="ignore") if env_path.exists() else ""
        if rendered == current:
            return False
        env_path.write_text(rendered, encoding="utf-8")
        return True

    @staticmethod
    def _format_market_update_text(data: Dict[str, Any]) -> str:
        lines = [
            "🧩 插件库同步",
            f"⦁ Wiki记录：{len(data.get('wiki_markets') or [])} 个",
            f"⦁ 当前配置：{len(data.get('settings_markets') or [])} 个",
            f"⦁ 第三方保留：{len(data.get('other_markets') or [])} 个",
            f"⦁ 新发现：{len(data.get('new_markets') or [])} 个",
            f"⦁ 黑名单拦截：{len(data.get('blocked_markets') or [])} 个",
            f"⦁ 写入当前配置：{'已执行' if data.get('settings_written') else '未执行'}",
            f"⦁ 写入 app.env：{'已执行' if data.get('env_written') else '未执行'}",
        ]
        for url in (data.get('new_markets') or [])[:5]:
            lines.append(f"⦁ 新库：{url}")
        for url in (data.get('blocked_markets') or [])[:5]:
            lines.append(f"⦁ 拦截库：{url}")
        if not data.get("success"):
            lines.append(f"⦁ 同步失败：{data.get('error') or '插件库同步未完成'}")
        return "\n".join(lines)

    @staticmethod
    def _market_update_outcome(data: Dict[str, Any]) -> str:
        writes = int(bool(data.get("settings_written"))) + int(bool(data.get("env_written")))
        blocked = len(data.get("blocked_markets") or [])
        if data.get("success"):
            parts = []
            if writes:
                parts.append(f"同步 {writes} 处插件库配置")
            if blocked:
                parts.append(f"拦截 {blocked} 个插件库")
            return "已" + "，".join(parts) if parts else "插件库检查完成，未执行变更"
        detail = str(data.get("error") or "").strip() or "插件库同步未完成"
        return f"插件库同步失败：{detail}"

    @staticmethod
    def _moviepilot_update_outcome(data: Dict[str, Any], success: bool) -> str:
        mp = data.get("moviepilot") or {}
        if success:
            if mp.get("upgrade_dispatched"):
                return "已触发 MoviePilot 升级并重启"
            if mp.get("has_update"):
                return "检测到更新，但未触发 MoviePilot 整体升级"
            return "检查完成，MoviePilot 已是最新版本"
        detail = str(mp.get("upgrade_error") or mp.get("restart_error") or "更新请求未被接受")[:120]
        return f"MoviePilot 更新触发失败：{detail}"

    def _auto_update_installed_plugins(self, apply: bool = True) -> Dict[str, Any]:
        """检查已安装插件是否有新版（移植自 thsrite/PluginAutoUpdate，适配本插件）。
        开启“自动安装”且 apply 时下载安装新版并重载；否则仅汇总可更新清单供通知。
        全程 try/except，任何失败只反映在结果里，不抛出。"""
        auto_install = bool(self._plugin_auto_install_enabled)
        out: Dict[str, Any] = {"auto_install": auto_install,
                               "updatable": [], "updated": [], "failed": [], "skipped": []}
        try:
            from app.core.plugin import PluginManager
            from app.db.systemconfig_oper import SystemConfigOper
            from app.schemas.types import SystemConfigKey
        except Exception as err:
            out["error"] = f"加载插件管理器失败：{str(err)[:120]}"
            return out
        try:
            installed_ids = SystemConfigOper().get(SystemConfigKey.UserInstalledPlugins) or []
            online = PluginManager().get_online_plugins() or []
            if not online:
                out["error"] = "未获取到在线插件列表"
                return out
            # 每个插件 id 取最大版本
            maxver: Dict[str, Any] = {}
            for p in online:
                if p.id not in maxver or p.plugin_version > maxver[p.id]:
                    maxver[p.id] = p.plugin_version
            online = [p for p in online if p.plugin_version == maxver[p.id]]
            # 已安装版本
            local_ver: Dict[str, Any] = {}
            for p in (PluginManager().get_local_plugins() or []):
                local_ver[p.id] = p.plugin_version
            # 正在运行的插件服务（可选跳过）
            running = set()
            try:
                from app.scheduler import Scheduler
                for s in (Scheduler().list() or []):
                    if getattr(s, "status", "") == "正在运行":
                        running.add(s.id)
            except Exception:
                pass
            scope_mode = str(getattr(self, "_plugin_auto_install_scope_mode", "all") or "all").strip().lower()
            if scope_mode not in {"all", "include", "exclude"}:
                scope_mode = "all"
            exclude = set(self._plugin_auto_install_exclude_ids or []) if scope_mode == "exclude" else set()
            include = set(self._plugin_auto_install_install_ids or []) if scope_mode == "include" else set()
            for p in online:
                pid = str(p.id)
                if pid not in installed_ids:
                    continue
                if not (getattr(p, "has_update", False) or not getattr(p, "installed", True)):
                    continue
                oldv = local_ver.get(p.id)
                if not oldv or str(oldv) == "None":
                    continue
                info = {"id": pid, "name": getattr(p, "plugin_name", pid), "old": str(oldv), "new": str(p.plugin_version)}
                out["updatable"].append(info)
                if not (apply and auto_install):
                    continue
                # 安全：永不自动更新本插件自身；尊重排除/仅选名单；运行中不动
                if pid.lower() in {"signal", "moviepilot", "agentopsassistant"} or pid in exclude:
                    out["skipped"].append({**info, "reason": "排除/本体"})
                    continue
                if scope_mode == "include" and pid not in include:
                    out["skipped"].append({**info, "reason": "不在自动更新列表"})
                    continue
                if pid in running or p.id in running:
                    out["skipped"].append({**info, "reason": "正在运行"})
                    continue
                try:
                    from app.helper.plugin import PluginHelper
                    state, msg = PluginHelper().install(pid=p.id, repo_url=getattr(p, "repo_url", ""))
                except Exception as err:
                    state, msg = False, str(err)
                if not state:
                    out["failed"].append({**info, "msg": str(msg)[:120]})
                    continue
                try:
                    PluginManager().reload_plugin(p.id)
                    # MoviePilot v3 reloads the instance only. The official
                    # registration entrypoint is required to restore commands,
                    # scheduler services, and dynamic plugin API routes.
                    from app.api.endpoints.plugin import register_plugin
                    register_plugin(p.id)
                except Exception as err:
                    message = str(err)[:160]
                    out["failed"].append({**info, "msg": f"重载后重新注册失败：{message}"})
                    logger.warning(f"Signal 重载插件 {pid} 失败：{message}")
                    continue
                hist = ""
                try:
                    for ver, note in (getattr(p, "history", None) or {}).items():
                        if str(ver).replace("v", "") == str(p.plugin_version).replace("v", ""):
                            hist = str(note)
                            break
                except Exception:
                    pass
                out["updated"].append({**info, "history": hist})
            return out
        except Exception as err:
            out["error"] = f"插件自动更新异常：{str(err)[:160]}"
            return out
    def run_update_preview(self) -> bool:
        ok, _ = self._guard_task("系统更新检查", "mp_update")
        if not ok:
            return False
        data = self._build_update_status()
        text = self._format_update_status_text(data)
        self._save_task_result("更新状态预览", True, 0, text)
        return True

    def run_mp_update_scheduled(self) -> bool:
        return self.run_mp_update_check(scheduled=True)

    def run_mp_update_check(self, scheduled: bool = False, result_name: str = "系统更新检查", notify: bool = False) -> bool:
        ok, _ = self._guard_task("系统更新检查", "mp_update")
        if not ok:
            return False
        try:
            data = self._build_update_status()
        except Exception as err:
            if not (notify or (scheduled and not getattr(self, "_fusion_notify_enabled", False))):
                raise
            text = f"系统更新检查失败：{err}"
            if self._task_outcome_notification_enabled(self._mp_update_scheduled_notify):
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._mp_update_notify_type),
                    title="系统更新异常",
                    text=text,
                    outcome=f"系统更新检查失败：{str(err)[:120]}",
                    success=False,
                    component="mp_update",
                    task_key="mp_update",
                    task_group="更新管理",
                    affected_owner="moviepilot",
                    notification_status="error",
                    notification_target="moviepilot",
                    notification_fingerprint=self._notification_error_fingerprint(err),
                    notification_cooldown=True,
                    notification_manual=notify,
                )
            self._save_task_result(result_name, False, -1, text)
            logger.error(f"Signal 系统更新检查失败：{err}")
            return False
        text = self._format_update_status_text(data)
        mp = data.get("moviepilot") or {}
        checks = mp.get("checks") or []
        errors = [f"{item.get('type') or '未知'}：{item.get('error')}" for item in checks if item.get("error")]
        if mp.get("version_error"):
            errors.append(f"本地版本：{mp.get('version_error')}")
        if not errors and mp.get("has_update"):
            self._dispatch_moviepilot_upgrade(data)
            text = self._format_update_status_text(data)
        execution_failed = bool(mp.get("has_update") and not mp.get("upgrade_dispatched"))
        success = bool(checks) and not errors and not execution_failed
        if (scheduled or notify) and self._task_outcome_notification_enabled(self._mp_update_scheduled_notify):
            title = "系统更新" if success else "系统更新异常"
            outcome = errors[0][:120] if errors else self._moviepilot_update_outcome(data, success)
            notification_status = "error" if not success else ("changed" if mp.get("has_update") else "noop")
            error_payload = {
                "checks": sorted([
                    {
                        "type": str(item.get("type") or ""),
                        "latest_version": str(item.get("latest_version") or ""),
                        "error": self._normalize_notification_error_summary(item.get("error")),
                    }
                    for item in checks if item.get("error")
                ], key=lambda item: (item["type"], item["latest_version"], item["error"])),
                "version_error": self._normalize_notification_error_summary(mp.get("version_error")),
                "upgrade_error": self._normalize_notification_error_summary(mp.get("upgrade_error") or mp.get("restart_error")),
            }
            self._notify_fusion_task_outcome(
                mtype=self._notification_type(self._mp_update_notify_type),
                title=title,
                text=text,
                outcome=outcome,
                success=success,
                component="mp_update",
                task_key="mp_update",
                task_group="更新管理",
                affected_owner="moviepilot",
                notification_status=notification_status,
                notification_target="moviepilot",
                notification_fingerprint=(
                    self._notification_outcome_fingerprint(error_payload)
                    if notification_status == "error" else ""
                ),
                notification_cooldown=notification_status == "error",
                notification_manual=notify,
            )
        self._save_task_result(result_name, success, 0 if success else 1, text)
        return success

    def run_mp_update_apply(self, notify: bool = False) -> bool:
        return self.run_mp_update_check(scheduled=False, result_name="主程序更新执行", notify=notify)

    def run_market_update_scheduled(self) -> bool:
        return self.run_market_update(scheduled=True)

    def run_market_update(self, scheduled: bool = False, notify: bool = False) -> bool:
        ok, _ = self._guard_task("插件库同步", "market_update")
        if not ok:
            return False
        try:
            data = self._build_market_update_status(apply=True)
            self._last_market_update_result = dict(data)
            text = self._format_market_update_text(data)
            success = bool(data.get("success"))
            if (scheduled or notify) and self._task_outcome_notification_enabled(self._market_update_scheduled_notify):
                changed = bool(data.get("new_markets") or data.get("settings_written") or data.get("env_written"))
                notification_status = "error" if not success else ("changed" if changed else "noop")
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._market_update_notify_type),
                    title="插件库同步" if success else "插件库同步异常",
                    text=text,
                    outcome=self._market_update_outcome(data),
                    success=success,
                    component="market_update",
                    task_key="market_sync",
                    task_group="更新管理",
                    notification_status=notification_status,
                    notification_target="market_sync",
                    notification_cooldown=notification_status == "error",
                    notification_manual=notify,
                )
            self._save_task_result("插件库同步", bool(data.get("success")), 0 if data.get("success") else 1, text)
            return bool(data.get("success"))
        except Exception as err:
            self._last_market_update_result = {
                "success": False,
                "error": str(err),
                "settings_written": False,
                "env_written": False,
            }
            self._save_task_result("插件库同步", False, -1, str(err))
            if (scheduled or notify) and self._task_outcome_notification_enabled(self._market_update_scheduled_notify):
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._market_update_notify_type),
                    title="插件库同步异常",
                    text=str(err),
                    outcome=f"插件库同步失败：{str(err)[:120]}",
                    success=False,
                    component="market_update",
                    task_key="market_sync",
                    task_group="更新管理",
                    notification_status="error",
                    notification_target="market_sync",
                    notification_fingerprint=self._notification_error_fingerprint(err),
                    notification_cooldown=True,
                    notification_manual=notify,
                )
            logger.error(f"Signal 插件库同步失败：{err}")
            return False

    @staticmethod
    def _format_plugin_update_text(data: Dict[str, Any], title: str = "🔔 插件更新") -> str:
        lines = [title]
        if data.get("error"):
            return "\n".join(lines + [f"⦁ 检查失败：{data['error']}"])
        updatable = data.get("updatable") or []
        updated = data.get("updated") or []
        failed = data.get("failed") or []
        skipped = data.get("skipped") or []
        if data.get("auto_install"):
            lines.append(f"⦁ 自动安装：成功 {len(updated)} 个｜失败 {len(failed)} 个｜跳过 {len(skipped)} 个")
            for item in updated[:8]:
                extra = f"｜{item['history']}" if item.get("history") else ""
                lines.append(f"  ✓ {item['name']}：v{item['old']} → v{item['new']}{extra}")
            for item in failed[:5]:
                lines.append(f"  ✗ {item['name']}：{item.get('msg')}")
            for item in skipped[:5]:
                lines.append(f"  – {item['name']}：跳过（{item.get('reason')}）")
        else:
            lines.append(f"⦁ 发现可更新插件：{len(updatable)} 个")
            for item in updatable[:10]:
                lines.append(f"  - {item['name']}：v{item['old']} → v{item['new']}")
            if not updatable:
                lines.append("⦁ 当前没有可更新插件")
        return "\n".join(lines)

    @staticmethod
    def _plugin_update_outcome(data: Dict[str, Any]) -> str:
        if data.get("error"):
            return f"插件更新检查失败：{str(data['error'])[:120]}"
        if data.get("auto_install"):
            return f"自动安装完成：成功 {len(data.get('updated') or [])} 个，失败 {len(data.get('failed') or [])} 个"
        return f"发现 {len(data.get('updatable') or [])} 个可更新插件"

    def run_plugin_update_reminder_scheduled(self) -> bool:
        return self.run_plugin_update_reminder(scheduled=True)

    def run_plugin_update_reminder(self, scheduled: bool = False, notify: bool = False) -> bool:
        ok, _ = self._guard_task("插件更新", "plugin_update_reminder")
        if not ok:
            return False
        auto_install_enabled = bool(getattr(self, "_plugin_auto_install_enabled", False))
        try:
            data = self._auto_update_installed_plugins(apply=auto_install_enabled)
        except Exception as err:
            if not (notify or (scheduled and not getattr(self, "_fusion_notify_enabled", False))):
                raise
            data = {
                "auto_install": auto_install_enabled,
                "updatable": [],
                "updated": [],
                "failed": [],
                "skipped": [],
                "error": str(err),
            }
            logger.error(f"Signal 插件更新检查失败：{err}")
        data["auto_install"] = auto_install_enabled
        text = self._format_plugin_update_text(data)
        success = not bool(data.get("error") or data.get("failed"))
        install_attempted = bool(data.get("updated") or data.get("failed"))
        notify_check = self._task_outcome_notification_enabled(self._plugin_update_reminder_scheduled_notify)
        notify_install = bool(
            data.get("auto_install")
            and install_attempted
            and self._task_outcome_notification_enabled(self._plugin_auto_install_scheduled_notify)
        )
        if (scheduled or notify) and notify_check:
            check_success = not bool(data.get("error"))
            check_data = {**data, "auto_install": False}
            updatable = list(check_data.get("updatable") or [])
            check_status = "error" if not check_success else ("changed" if updatable else "noop")
            check_fingerprint = ""
            if check_status == "error":
                check_fingerprint = self._notification_error_fingerprint(check_data.get("error"))
            elif check_status == "changed":
                check_fingerprint = self._notification_outcome_fingerprint({
                    "plugins": sorted([
                        {
                            "id": str(item.get("id") or item.get("name") or ""),
                            "target_version": str(item.get("new") or item.get("version") or ""),
                        }
                        for item in updatable
                    ], key=lambda item: (item["id"], item["target_version"])),
                })
            self._notify_fusion_task_outcome(
                mtype=self._notification_type(self._plugin_update_reminder_notify_type),
                title="插件更新检查" if check_success else "插件更新检查异常",
                text=self._format_plugin_update_text(check_data, title="🔔 插件更新检查"),
                outcome=self._plugin_update_outcome(check_data),
                success=check_success,
                component="plugin_update_reminder",
                task_key="plugin_update_reminder",
                task_group="更新管理",
                notification_status=check_status,
                notification_target="available_updates",
                notification_fingerprint=check_fingerprint,
                notification_cooldown=check_status in {"changed", "error"},
                notification_manual=notify,
            )
        if (scheduled or notify) and notify_install:
            install_success = not bool(data.get("error") or data.get("failed"))
            self._notify_fusion_task_outcome(
                mtype=self._notification_type(self._plugin_auto_install_notify_type),
                title="插件自动安装" if install_success else "插件自动安装异常",
                text=self._format_plugin_update_text(data, title="📦 插件自动安装"),
                outcome=self._plugin_update_outcome(data),
                success=install_success,
                component="plugin_update_reminder",
                task_key="plugin_auto_install",
                task_group="更新管理",
                notification_status="changed" if install_success else "error",
                notification_target="plugin_auto_install",
                notification_cooldown=False,
                notification_manual=notify,
            )
        self._save_task_result("插件更新", success, 0 if success else 1, text)
        return success

    def run_plugin_auto_install_scheduled(self) -> bool:
        return self.run_plugin_auto_install(scheduled=True)

    def run_plugin_auto_install(self, scheduled: bool = False, notify: bool = False) -> bool:
        # Compatibility command/API: installation is now part of one plugin
        # update check and must not create a second execution path.
        return self.run_plugin_update_reminder(scheduled=scheduled, notify=notify)

    def _api_run_task(self, name: str, runner, component: Optional[str] = None, **runner_kwargs: Any) -> Dict[str, Any]:
        ok, msg = self._can_run_task(name, component)
        if not ok:
            self._save_task_result(name, False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        try:
            success = bool(runner(**runner_kwargs))
            return {"code": 0 if success else 1, "msg": f"{name}执行{'成功' if success else '失败'}，详情请查看插件日志。"}
        except Exception as err:
            try:
                self._save_task_result(name, False, -1, str(err))
            except Exception:
                pass
            logger.error(f"Signal {name}执行异常：{err}")
            return {"code": 1, "msg": f"{name}执行失败：{err}"}

    def _run_named_task(self, name: str, cmd: List[str], expect: str = "") -> bool:
        result = self._run_command_capture(cmd, timeout=600)
        output = result["output"]
        ok = result["returncode"] == 0 and (not expect or expect in output)
        self._save_task_result(name, ok, result["returncode"], output)
        return ok

    @staticmethod
    def _run_command_capture(cmd: List[str], timeout: int = 600) -> Dict[str, Any]:
        try:
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            result = subprocess.run(cmd, cwd="/config", env=env, capture_output=True, text=True, timeout=timeout, check=False)
            output = "\n".join([result.stdout or "", result.stderr or ""]).strip()
            return {"returncode": result.returncode, "output": output[-4000:]}
        except Exception as err:
            return {"returncode": -1, "output": str(err)}

    def _save_task_result(self, name: str, success: bool, returncode: int, output: str):
        slug = self._slug(name)
        key = f"last_{slug}"
        result = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "returncode": returncode,
            "success": bool(success),
            "output": (output or "")[-2000:],
        }
        if slug == "market_update":
            snapshot = self.get_data(key) or {}
            if isinstance(snapshot, dict):
                result = {**snapshot, **result}
        self.save_data(key, result)
