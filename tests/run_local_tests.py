#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentOpsAssistant 本地单元测试（无需运行中的 MoviePilot）。

做法：把插件 import 的 `app.*` / `apscheduler` 全部用桩(stub)注入 sys.modules，
再用 importlib 以文件路径加载 plugins.v2/agentopsassistant/__init__.py，
然后对“纯逻辑”方法（删种条件匹配、格式化、聚合等）做断言测试。

运行： python tests/run_local_tests.py
仅用标准库，不依赖 pytest。失败时退出码非 0。
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
import types
import zipfile
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_FILE = ROOT / "plugins.v2" / "agentopsassistant" / "__init__.py"


# ---------------------------------------------------------------- stubs
def _mod(name):
    m = types.ModuleType(name)
    sys.modules[name] = m
    return m


class _Logger:
    def info(self, *a, **k): pass
    def warning(self, *a, **k): pass
    def warn(self, *a, **k): pass
    def error(self, *a, **k): pass
    def debug(self, *a, **k): pass


class _StubPluginBase:
    def __init__(self):
        self._stub_data = {}
        self._stub_messages = []
    def save_data(self, key, value): self._stub_data[key] = value
    def get_data(self, key): return self._stub_data.get(key)
    def post_message(self, **kwargs): self._stub_messages.append(kwargs)
    def update_config(self, conf): self._stub_data["__config__"] = conf


class _StubStringUtils:
    @staticmethod
    def str_filesize(size):
        try:
            return f"{float(size) / (1024 ** 3):.2f}GB"
        except Exception:
            return str(size)
    @staticmethod
    def get_url_sld(url):
        return str(url or "")


class _StubRequestUtils:
    def __init__(self, *a, **k): pass
    def get_res(self, *a, **k): return None


class _StubCronTrigger:
    @staticmethod
    def from_crontab(expr): return ("cron", expr)


class _StubIntervalTrigger:
    def __init__(self, **k): self.kwargs = k


class _StubEventManager:
    def register(self, *a, **k):
        def deco(fn): return fn
        return deco


class _StubNotificationType(Enum):
    Download = "Download"
    Organize = "Organize"
    Subscribe = "Subscribe"
    SiteMessage = "SiteMessage"
    MediaServer = "MediaServer"
    Manual = "Manual"
    Plugin = "Plugin"
    Agent = "Agent"
    Other = "Other"


# 插件自动更新桩：测试通过 _PU 配置 在线/本地/已装/运行中 列表，并记录 install/reload 调用
_PU = {"online": [], "local": [], "installed": [], "running": [], "folders": {},
       "install_result": (True, "ok"), "install_calls": [], "reloaded": [],
       "removed_plugins": [], "removed_jobs": [], "config_deleted": [], "data_deleted": [],
       "system_deleted": [], "notifications": []}


class _StubPluginManager:
    def get_online_plugins(self): return list(_PU["online"])
    def get_local_plugins(self): return list(_PU["local"])
    def reload_plugin(self, pid): _PU["reloaded"].append(pid)
    def remove_plugin(self, pid): _PU["removed_plugins"].append(pid)
    def delete_plugin_config(self, pid): _PU["config_deleted"].append(pid); return True
    def delete_plugin_data(self, pid): _PU["data_deleted"].append(pid); return True
    def get_plugin_apis(self): return []


class _StubPluginHelper:
    def install(self, pid=None, repo_url=None):
        _PU["install_calls"].append((pid, repo_url))
        return _PU["install_result"]


class _StubScheduler:
    def list(self):
        return [types.SimpleNamespace(id=i, status="正在运行") for i in _PU["running"]]
    def update_plugin_job(self, pid): pass
    def remove_plugin_job(self, pid): _PU["removed_jobs"].append(pid)


class _StubSystemConfigOper:
    def get(self, key):
        if key == "UserInstalledPlugins":
            return list(_PU["installed"])
        if key == "PluginFolders":
            return json.loads(json.dumps(_PU["folders"]))
        if key == "Notifications":
            return json.loads(json.dumps(_PU["notifications"]))
        return None
    def set(self, key, value):
        if key == "UserInstalledPlugins":
            _PU["installed"] = list(value or [])
        elif key == "PluginFolders":
            _PU["folders"] = value or {}
        return True
    def delete(self, key):
        _PU["system_deleted"].append(key)
        return True


class _StubDirectoryHelper:
    def get_library_dirs(self):
        return [types.SimpleNamespace(library_path="/media", library_storage="local")]
    def get_download_dirs(self):
        return [types.SimpleNamespace(download_path="/downloads", storage="local")]
    def get_dirs(self):
        return self.get_library_dirs() + self.get_download_dirs()


# 订阅规则填充桩：_SUB 配置下载历史/订阅列表，并记录 update 调用
_SUB = {"history": None, "subs": [], "updates": [], "sub_get": None, "sites": [], "site_latest": [],
        "site_refresh_calls": 0, "site_refresh_result": {}, "site_refresh_error": None,
        "tmdb_episodes": [], "movie_mediainfo": None}


class _StubDownloadHistoryOper:
    def get_by_hash(self, h): return _SUB["history"]


class _StubSubscribeOper:
    def list(self): return list(_SUB["subs"])
    def list_by_tmdbid(self, tmdbid=None, season=None): return list(_SUB["subs"])
    def update(self, sid, payload): _SUB["updates"].append((sid, payload))
    def get(self, sid): return _SUB.get("sub_get")


class _StubSiteOper:
    def list_active(self): return list(_SUB.get("sites", []))
    def get_userdata_latest(self): return list(_SUB.get("site_latest", []))
    def get_userdata_by_date(self, day):
        prev = _SUB.get("site_prev", [])
        if isinstance(prev, dict):
            return list(prev.get(day, []))
        return list(prev)


class _StubSiteChain:
    def refresh_userdatas(self):
        _SUB["site_refresh_calls"] = int(_SUB.get("site_refresh_calls") or 0) + 1
        if _SUB.get("site_refresh_error"):
            raise RuntimeError(_SUB.get("site_refresh_error"))
        return _SUB.get("site_refresh_result")


class _StubTmdbChain:
    def tmdb_episodes(self, *a, **k):
        return list(_SUB.get("tmdb_episodes") or [])


class _StubMediaChain:
    def recognize_media(self, *a, **k):
        return _SUB.get("movie_mediainfo")


def install_stubs():
    """注入插件 import 的全部外部模块桩。"""
    _mod("app")
    _mod("app.core")
    cfg = _mod("app.core.config")
    cfg.settings = types.SimpleNamespace(
        TZ="Asia/Shanghai", PROXY=None, GITHUB_HEADERS={}, PLUGIN_MARKET="",
        CONFIG_PATH="/tmp/agentops-test-config", DB_TYPE="sqlite", TORRENT_TAG="MOVIEPILOT",
        RMT_MEDIAEXT=[], DOWNLOAD_TMPEXT=[], RMT_SUBEXT=[], RMT_AUDIOEXT=[],
    )
    ev = _mod("app.core.event")
    ev.Event = object
    ev.eventmanager = _StubEventManager()
    log = _mod("app.log")
    log.logger = _Logger()
    plugins = _mod("app.plugins")
    plugins._PluginBase = _StubPluginBase
    sch = _mod("app.schemas")
    sch.NotificationType = _StubNotificationType
    sch.ServiceInfo = object
    scht = _mod("app.schemas.types")
    scht.EventType = types.SimpleNamespace(
        PluginAction="PluginAction", MessageAction="MessageAction", WebhookMessage="WebhookMessage",
        SubscribeAdded="SubscribeAdded", DownloadAdded="DownloadAdded",
    )
    scht.SystemConfigKey = types.SimpleNamespace(Storages="Storages", UserInstalledPlugins="UserInstalledPlugins", RssSites="RssSites", Notifications="Notifications")
    http = _mod("app.utils.http")
    http.RequestUtils = _StubRequestUtils
    stru = _mod("app.utils.string")
    stru.StringUtils = _StubStringUtils
    # 插件自动更新相关
    corep = _mod("app.core.plugin")
    corep.PluginManager = _StubPluginManager
    helperp = _mod("app.helper.plugin")
    helperp.PluginHelper = _StubPluginHelper
    schd = _mod("app.scheduler")
    schd.Scheduler = _StubScheduler
    sysoper = _mod("app.db.systemconfig_oper")
    sysoper.SystemConfigOper = _StubSystemConfigOper
    helper_dir = _mod("app.helper.directory")
    helper_dir.DirectoryHelper = _StubDirectoryHelper
    dho = _mod("app.db.downloadhistory_oper")
    dho.DownloadHistoryOper = _StubDownloadHistoryOper
    subo = _mod("app.db.subscribe_oper")
    subo.SubscribeOper = _StubSubscribeOper
    siteo = _mod("app.db.site_oper")
    siteo.SiteOper = _StubSiteOper
    chain = _mod("app.chain")
    chain_site = _mod("app.chain.site")
    chain_site.SiteChain = _StubSiteChain
    chain_tmdb = _mod("app.chain.tmdb")
    chain_tmdb.TmdbChain = _StubTmdbChain
    chain_media = _mod("app.chain.media")
    chain_media.MediaChain = _StubMediaChain
    scht.MediaType = types.SimpleNamespace(MOVIE="电影", TV="电视剧")
    # apscheduler
    _mod("apscheduler")
    _mod("apscheduler.triggers")
    cron = _mod("apscheduler.triggers.cron")
    cron.CronTrigger = _StubCronTrigger
    interval = _mod("apscheduler.triggers.interval")
    interval.IntervalTrigger = _StubIntervalTrigger


def load_plugin():
    spec = importlib.util.spec_from_file_location("agentopsassistant_under_test", str(PLUGIN_FILE))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- fakes
def fake_qb_torrent(**over):
    now = datetime.now().timestamp()
    d = dict(hash="abc123", name="Demo.S01E01", size=int(5 * 1024 ** 3),
             completion_on=int(now - 100000), added_on=int(now - 100000),
             uploaded=int(1 * 1024 ** 3), ratio=3.0, save_path="/downloads/demo",
             tracker="https://tracker.example.com/announce", state="pausedUP", category="tv", tags="")
    d.update(over)
    return types.SimpleNamespace(**d)


def fake_tr_torrent(**over):
    done = datetime.now() - timedelta(hours=30)
    d = dict(hashString="def456", name="Demo.S01E02", total_size=int(5 * 1024 ** 3),
             date_done=done, date_added=done, ratio=3.0, download_dir="/downloads/demo",
             trackers=[{"announce": "https://tracker.example.com/announce", "sitename": "Example"}],
             error_string="")
    d.update(over)
    return types.SimpleNamespace(**d)


class FakeDownloaderInstance:
    def __init__(self, torrents):
        self._torrents = torrents
        self.stopped, self.deleted, self.deleted_with_files, self.tagged = [], [], [], []
    def is_inactive(self): return False
    def get_torrents(self, tags=None): return (self._torrents, False)
    def stop_torrents(self, ids=None): self.stopped.extend(ids or [])
    def delete_torrents(self, delete_file=False, ids=None):
        (self.deleted_with_files if delete_file else self.deleted).extend(ids or [])
    def set_torrents_tag(self, ids=None, tags=None): self.tagged.append(("qb", list(ids or []), list(tags or [])))
    def set_torrent_tag(self, ids=None, tags=None, org_tags=None): self.tagged.append(("tr", ids, list(tags or []), list(org_tags or [])))


def fake_online(pid, ver, has_update=True, repo="https://repo.example/", name=None, history=None):
    return types.SimpleNamespace(id=pid, plugin_version=ver, plugin_name=name or pid,
                                 repo_url=repo, has_update=has_update, installed=True,
                                 history=history or {}, plugin_icon="x.png")


def fake_local(pid, ver):
    return types.SimpleNamespace(id=pid, plugin_version=ver)


def make_plugin(module, **cfg):
    p = module.AgentOpsAssistant()
    base = {"enabled": True}
    base.update(cfg)
    p.init_plugin(base)
    return p


# ---------------------------------------------------------------- test framework
_FAILS = []
def check(cond, msg):
    if cond:
        print(f"  PASS  {msg}")
    else:
        print(f"  FAIL  {msg}")
        _FAILS.append(msg)


def main():
    install_stubs()
    mod = load_plugin()

    print("== 纯函数 ==")
    p = make_plugin(mod)
    check(p._episode_ranges([1, 2, 3, 5]) == "E01-E03,E05", "_episode_ranges 连续/跳号")
    check(p._format_bytes(0) == "0 B", "_format_bytes 0")
    check(p._format_bytes(1536) == "1.50 KB", "_format_bytes KB")
    check(p._parse_csv("a, b ,c") == ["a", "b", "c"], "_parse_csv 字符串")
    check(p._parse_csv(["x", " y "]) == ["x", "y"], "_parse_csv 列表")
    check(p._notification_type("Other").name == "Other", "_notification_type 支持 Other")
    check(p._notification_type("其他").name == "Other", "_notification_type 支持中文“其他”")
    check(p._notification_type("不存在").name == "Plugin", "_notification_type 非法值回退 Plugin")

    print("== 存储行（_append_usage_line）==")
    items = []
    ok = p._append_usage_line(items, "本地", 100, None, 40)  # total=100, free=40 -> used=60
    check(ok is True and len(items) == 1 and "本地：已用 60% ｜ 60B/100B" in items[0] and "🟢" in items[0]
          and "█" not in items[0] and "░" not in items[0] and "[" not in items[0],
          "存储输出使用文字指标格式，避免 Telegram 渲染成黑块")
    check("剩余" not in items[0], "存储输出不重复展示剩余空间")
    items2 = []
    ok2 = p._append_usage_line(items2, "空盘", 0, None, 0)  # total<=0 -> skip
    check(ok2 is False and items2 == [], "total<=0 跳过（不输出“已配置”噪声）")

    print("== 删种条件守卫 ==")
    check(p._seedclean_has_any_condition() is False, "无条件时 has_any_condition=False")
    p._seedclean_size = "1-10"
    check(p._seedclean_has_any_condition() is True, "设了大小后=True")
    p._seedclean_size = ""

    g = make_plugin(mod, fusion_notify_enabled=False, seedclean_enabled=True, seedclean_downloaders=[])
    check(g.run_seed_clean() is False, "无下载器 -> 不执行返回 False")
    check(g._stub_messages and "选择下载器" in g._stub_messages[-1].get("text", ""), "无下载器时按通知配置提醒用户")
    g2 = make_plugin(mod, seedclean_enabled=True, seedclean_downloaders=["qb1"])  # 无任何条件
    check(g2.run_seed_clean() is False, "有下载器但无条件 -> 跳过返回 False")

    print("== 融合通知：控制通知输出，不接管任务调度 ==")
    p_fusion_services = make_plugin(
        mod,
        fusion_notify_enabled=True,
        fusion_notify_schedule_enabled=True,
        subscribe_reminder_enabled=True,
        subscribe_reminder_schedule_enabled=True,
        health_check_enabled=True,
        health_check_schedule_enabled=True,
        backup_enabled=True,
        backup_schedule_enabled=True,
        log_clean_enabled=True,
        log_clean_schedule_enabled=True,
        mp_update_enabled=True,
        mp_update_schedule_enabled=True,
        market_update_enabled=True,
        market_update_schedule_enabled=True,
        seedclean_enabled=True,
        seedclean_schedule_enabled=True,
        seedclean_downloaders=["qb1"],
    )
    service_ids = {s.get("id") for s in p_fusion_services.get_service()}
    expected_service_ids = {
        "AgentOpsAssistant.FusionNotify",
        "AgentOpsAssistant.HealthCheck",
        "AgentOpsAssistant.Backup",
        "AgentOpsAssistant.LogClean",
        "AgentOpsAssistant.MPUpdate",
        "AgentOpsAssistant.MarketUpdate",
        "AgentOpsAssistant.SeedClean",
    }
    check(expected_service_ids <= service_ids
          and "AgentOpsAssistant.SubscribeReminder" not in service_ids,
          "融合通知开启时任务类定时仍注册，订阅追新这类定时通知由融合刷新统一控制")

    _PU["notifications"] = []
    p_tg_status = make_plugin(mod, fusion_notify_enabled=True)
    tg_status = p_tg_status.api_tg_console_status().get("data") or {}
    check(tg_status.get("chat_configured") is False
          and "未找到可用 Telegram 通知渠道" in tg_status.get("config_hint", "")
          and not tg_status.get("last_error"),
          "未配置 Telegram 时状态接口只给中性提示，不在安装后显示错误")
    _PU["notifications"] = []

    print("== QB 条件匹配（命中=返回 dict=删除目标）==")
    p = make_plugin(mod)
    p._seedclean_size = "1-10"
    check(p._seed_match_qb(fake_qb_torrent(size=int(5 * 1024 ** 3))) is not None, "5GB 在 1-10 区间 -> 命中")
    check(p._seed_match_qb(fake_qb_torrent(size=int(20 * 1024 ** 3))) is None, "20GB 超上限 -> 不命中")
    check(p._seed_match_qb(fake_qb_torrent(size=int(0.5 * 1024 ** 3))) is None, "0.5GB 低于下限 -> 不命中")
    p._seedclean_size = ""
    p._seedclean_ratio = "2"
    check(p._seed_match_qb(fake_qb_torrent(ratio=3.0)) is not None, "分享率 3>2 -> 命中")
    check(p._seed_match_qb(fake_qb_torrent(ratio=1.0)) is None, "分享率 1<=2 -> 不命中")
    p._seedclean_ratio = ""
    p._seedclean_time = "10"  # 10 小时
    check(p._seed_match_qb(fake_qb_torrent()) is not None, "做种 ~27h > 10h -> 命中")
    fresh = datetime.now().timestamp() - 600  # 10 分钟
    check(p._seed_match_qb(fake_qb_torrent(completion_on=int(fresh), added_on=int(fresh))) is None, "做种 10min < 10h -> 不命中")
    p._seedclean_time = ""
    p._seedclean_torrentstates = "pausedUP,stalledUP"
    check(p._seed_match_qb(fake_qb_torrent(state="pausedUP")) is not None, "状态在列表 -> 命中")
    check(p._seed_match_qb(fake_qb_torrent(state="downloading")) is None, "状态不在列表 -> 不命中")
    p._seedclean_torrentstates = ""

    print("== TR 条件匹配 ==")
    p = make_plugin(mod)
    p._seedclean_time = "10"
    check(p._seed_match_tr(fake_tr_torrent()) is not None, "TR 做种 30h > 10h -> 命中")
    check(p._seed_match_tr(fake_tr_torrent(date_done=datetime.now(), date_added=datetime.now())) is None, "TR 刚完成 -> 不命中")
    p._seedclean_time = ""
    p._seedclean_trackerkeywords = "example"
    check(p._seed_match_tr(fake_tr_torrent()) is not None, "TR tracker 命中关键词")
    check(p._seed_match_tr(fake_tr_torrent(trackers=[{"announce": "https://other.org/a", "sitename": "O"}])) is None, "TR tracker 不含关键词 -> 不命中")

    print("== run_seed_clean 端到端（假下载器）==")
    inst = FakeDownloaderInstance([fake_qb_torrent(hash="h1", size=int(5 * 1024 ** 3))])
    service = types.SimpleNamespace(instance=inst, config=types.SimpleNamespace(type="qbittorrent"), name="qb1")

    def fake_get_services(name_filters=None):
        return {"qb1": service}

    # patch DownloaderHelper used via lazy import inside _seed_clean_run
    dl_mod = sys.modules["app.helper.downloader"] = types.ModuleType("app.helper.downloader")
    class _DH:
        def get_services(self, name_filters=None): return fake_get_services(name_filters)
        def get_configs(self): return {"qb1": types.SimpleNamespace(name="qb1")}
    dl_mod.DownloaderHelper = _DH

    p = make_plugin(mod, seedclean_enabled=True, seedclean_downloaders=["qb1"], seedclean_size="1-10", seedclean_action="pause")
    res = p.run_seed_clean()
    check(res is True, "pause 动作执行成功返回 True")
    check(inst.stopped == ["h1"], "命中种子被暂停（stop_torrents 收到 h1）")
    check(inst.deleted == [] and inst.deleted_with_files == [], "暂停动作未调用删除")

    inst2 = FakeDownloaderInstance([fake_qb_torrent(hash="h2", size=int(5 * 1024 ** 3))])
    service.instance = inst2
    p2 = make_plugin(mod, seedclean_enabled=True, seedclean_downloaders=["qb1"], seedclean_size="1-10", seedclean_action="delete")
    p2.run_seed_clean()
    check(inst2.deleted == ["h2"], "delete 动作调用 delete_torrents(delete_file=False)")

    inst3 = FakeDownloaderInstance([fake_qb_torrent(hash="h3", size=int(0.1 * 1024 ** 3))])  # 太小，不命中
    service.instance = inst3
    p3 = make_plugin(mod, seedclean_enabled=True, seedclean_downloaders=["qb1"], seedclean_size="1-10", seedclean_action="delete")
    p3.run_seed_clean()
    check(inst3.deleted == [] and inst3.stopped == [], "不命中的种子不被处理（无误删）")

    print("== 下载器助手：按站点批量打标签（幂等）==")
    tinst = FakeDownloaderInstance([
        fake_qb_torrent(hash="ta", tags=""),
        fake_qb_torrent(hash="tb", tags="https://tracker.example.com/announce"),
    ])
    service.instance = tinst
    make_plugin(mod, dltag_enabled=True, dltag_downloaders=["qb1"]).run_downloader_tag()
    qb_tag_hashes = [h for c in tinst.tagged if c[0] == "qb" for h in c[1]]
    check("ta" in qb_tag_hashes and "tb" not in qb_tag_hashes, "未打标签的补打、已打标签的跳过（幂等）")

    print("== 备份 PG 兜底 / 状态文案 ==")
    p = make_plugin(mod)
    check(p._sql_literal(None) == "NULL", "_sql_literal None->NULL")
    check(p._sql_literal(True) == "TRUE" and p._sql_literal(False) == "FALSE", "_sql_literal bool")
    check(p._sql_literal(12) == "12", "_sql_literal int")
    check(p._sql_literal("o'brien") == "'o''brien'", "_sql_literal 单引号转义（防坏 SQL）")
    check(p._sql_literal(b"\x00\x01") == "'\\x0001'", "_sql_literal bytes->hex")
    # 无 pg_dump 且无 app.db 引擎 -> 优雅失败（不抛），返回 (False, 含“未导出”)
    p._find_pg_dump = lambda: ""
    ok_pg, msg_pg = p._dump_postgresql(Path("/tmp/aoa-nonexist-pg.sql"))
    check(ok_pg is False and "未导出" in msg_pg, "无 pg_dump+无引擎 -> (False, 未导出)，不抛异常")
    # 状态文案：只有 PG 提示时显示“成功”+“提示：”，不出现“异常：”
    t_ok = p._format_backup_status_text({"success": True, "back_path": "/x", "keep_count": 3,
                                         "backup_count": 1, "backup_size_text": "1 KB",
                                         "warnings": ["PostgreSQL 未导出：容器内无 pg_dump"], "errors": []})
    check("状态：成功" in t_ok and "提示：" in t_ok and "异常：" not in t_ok, "PG 缺失只提示不报异常")
    t_err = p._format_backup_status_text({"success": False, "back_path": "/x", "keep_count": 3,
                                          "backup_count": 0, "backup_size_text": "0 B", "errors": ["真失败"]})
    check("状态：异常" in t_err and "异常：" in t_err, "真失败仍报异常")

    print("== 备份一键恢复 ==")
    cfg_settings = sys.modules["app.core.config"].settings
    old_config_path, old_db_type = cfg_settings.CONFIG_PATH, cfg_settings.DB_TYPE
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        config_dir = root / "config"
        backup_dir = root / "backups"
        config_dir.mkdir()
        backup_dir.mkdir()
        (config_dir / "category.yaml").write_text("old-category", encoding="utf-8")
        (config_dir / "app.env").write_text("old-env", encoding="utf-8")
        (config_dir / "cookies").mkdir()
        (config_dir / "cookies" / "old.cookie").write_text("old-cookie", encoding="utf-8")
        (config_dir / "user.db").write_text("old-db", encoding="utf-8")
        cfg_settings.CONFIG_PATH = str(config_dir)
        cfg_settings.DB_TYPE = "sqlite"
        valid_zip = backup_dir / "bk_20260621010101.zip"
        with zipfile.ZipFile(valid_zip, "w") as zf:
            zf.writestr("manifest.json", json.dumps({"created_at": "2026-06-21 01:01:01", "db_type": "sqlite"}, ensure_ascii=False))
            zf.writestr("category.yaml", "new-category")
            zf.writestr("app.env", "new-env")
            zf.writestr("cookies/session.cookie", "new-cookie")
            zf.writestr("user.db", "new-db")
        (backup_dir / "not_backup.zip").write_text("skip", encoding="utf-8")
        missing_manifest = backup_dir / "bk_20260621020202.zip"
        with zipfile.ZipFile(missing_manifest, "w") as zf:
            zf.writestr("category.yaml", "no-manifest")
        slip_zip = backup_dir / "bk_20260621030303.zip"
        with zipfile.ZipFile(slip_zip, "w") as zf:
            zf.writestr("manifest.json", "{}")
            zf.writestr("../evil.txt", "bad")
        p_restore = make_plugin(mod, backup_enabled=True, backup_path=str(backup_dir), backup_keep_count=20, backup_notify=False)
        archives = p_restore._list_backup_archives()
        check([x["name"] for x in archives] == ["bk_20260621030303.zip", "bk_20260621020202.zip", "bk_20260621010101.zip"],
              "备份恢复列表只列备份目录内 bk_*.zip")
        preview = p_restore.api_preview_backup_restore({"archive": valid_zip.name, "restore_config": True, "restore_cookies": True, "restore_database": True})
        check(preview.get("code") == 0 and preview.get("data", {}).get("archive", {}).get("name") == valid_zip.name,
              "备份恢复预览读取 manifest 与包内容")
        bad_path = p_restore.api_preview_backup_restore({"archive": "../bk_20260621010101.zip"})
        check(bad_path.get("code") == 1 and "备份目录" in bad_path.get("msg", ""),
              "备份恢复拒绝路径穿越 archive")
        bad_manifest = p_restore.api_preview_backup_restore({"archive": missing_manifest.name})
        check(bad_manifest.get("code") == 1 and "manifest.json" in bad_manifest.get("msg", ""),
              "备份恢复拒绝缺少 manifest 的包")
        bad_slip = p_restore.api_preview_backup_restore({"archive": slip_zip.name})
        check(bad_slip.get("code") == 1 and "非法路径" in bad_slip.get("msg", ""),
              "备份恢复拒绝 zip slip 条目")
        unconfirmed_restore = p_restore.api_run_backup_restore({"archive": valid_zip.name, "restore_config": True, "restore_cookies": True, "restore_database": True})
        check(unconfirmed_restore.get("code") == 1 and "确认" in unconfirmed_restore.get("msg", "")
              and (config_dir / "category.yaml").read_text(encoding="utf-8") == "old-category",
              "备份恢复执行接口缺少 confirm 时拒绝覆盖配置")
        run_restore = p_restore.api_run_backup_restore({"archive": valid_zip.name, "restore_config": True, "restore_cookies": True, "restore_database": True, "confirm": True})
        data_restore = run_restore.get("data", {})
        check(run_restore.get("code") == 0 and data_restore.get("emergency_backup") and Path(data_restore["emergency_backup"]).exists(),
              "执行恢复前强制生成 emergency backup")
        check((config_dir / "category.yaml").read_text(encoding="utf-8") == "new-category"
              and (config_dir / "app.env").read_text(encoding="utf-8") == "new-env",
              "备份恢复覆盖配置文件")
        check((config_dir / "cookies" / "session.cookie").read_text(encoding="utf-8") == "new-cookie"
              and not (config_dir / "cookies" / "old.cookie").exists(),
              "备份恢复替换 cookies 目录")
        check((config_dir / "user.db").read_text(encoding="utf-8") == "new-db",
              "备份恢复覆盖 SQLite user.db")

        pg_zip = backup_dir / "bk_20260621040404.zip"
        with zipfile.ZipFile(pg_zip, "w") as zf:
            zf.writestr("manifest.json", json.dumps({"created_at": "2026-06-21 04:04:04", "db_type": "postgresql"}, ensure_ascii=False))
            zf.writestr("postgresql_backup.sql", "select 1;")
        p_restore._find_psql = lambda: ""
        pg_restore = p_restore.api_run_backup_restore({"archive": pg_zip.name, "restore_config": False, "restore_cookies": False, "restore_database": True, "confirm": True})
        check(pg_restore.get("code") == 1 and "psql" in pg_restore.get("msg", "").lower(),
              "PostgreSQL 恢复缺少 psql 时可读失败且不执行破坏性动作")

        class FakeWebDavClient:
            def __init__(self):
                self.downloads = []

            def list(self):
                return ["bk_20260621010101.zip", "notes.txt", "folder/bk_20260621099999.zip"]

            def info(self, name):
                return {"size": valid_zip.stat().st_size, "modified": "2026-06-21 01:01:01"}

            def download_sync(self, remote_path, local_path):
                self.downloads.append((remote_path, local_path))
                shutil.copyfile(valid_zip, local_path)

        fake_webdav = FakeWebDavClient()
        p_restore._backup_webdav_enabled = True
        p_restore._create_webdav_client = lambda: fake_webdav
        webdav_archives = p_restore.api_webdav_backup_archives()
        check(webdav_archives.get("code") == 0
              and [x["name"] for x in webdav_archives.get("data", [])] == ["bk_20260621010101.zip"],
              "WebDAV 恢复列表只列远端根目录 bk_*.zip")
        webdav_preview = p_restore.api_preview_webdav_backup_restore({"archive": valid_zip.name, "restore_config": True, "restore_cookies": False, "restore_database": False})
        check(webdav_preview.get("code") == 0
              and webdav_preview.get("data", {}).get("source") == "webdav"
              and fake_webdav.downloads[-1][0] == valid_zip.name,
              "WebDAV 恢复预览会下载远端备份并复用本地预览链路")
        before_unconfirmed_webdav_downloads = len(fake_webdav.downloads)
        webdav_unconfirmed = p_restore.api_run_webdav_backup_restore({"archive": valid_zip.name, "restore_config": True, "restore_cookies": False, "restore_database": False})
        check(webdav_unconfirmed.get("code") == 1 and "确认" in webdav_unconfirmed.get("msg", "")
              and len(fake_webdav.downloads) == before_unconfirmed_webdav_downloads,
              "WebDAV 恢复执行接口缺少 confirm 时拒绝下载和覆盖")
        webdav_run = p_restore.api_run_webdav_backup_restore({"archive": valid_zip.name, "restore_config": True, "restore_cookies": False, "restore_database": False, "confirm": True})
        check(webdav_run.get("code") == 0
              and webdav_run.get("data", {}).get("source") == "webdav"
              and webdav_run.get("data", {}).get("remote_archive") == valid_zip.name,
              "WebDAV 恢复执行会下载远端备份并复用本地恢复链路")
        webdav_bad = p_restore.api_preview_webdav_backup_restore({"archive": "folder/bk_20260621010101.zip"})
        check(webdav_bad.get("code") == 1 and "WebDAV" in webdav_bad.get("msg", ""),
              "WebDAV 恢复拒绝子目录或路径穿越 archive")
    cfg_settings.CONFIG_PATH, cfg_settings.DB_TYPE = old_config_path, old_db_type

    print("== 插件卸载（多选 ID 与卸载流程回归）==")
    r1 = make_plugin(mod, plugin_uninstall_ids=["AutoBackup"])._build_plugin_uninstall_status(clean=False)
    check(r1.get("plugin_id") == "AutoBackup" and not r1.get("blocked") and r1.get("success") is True,
          "多选列表被识别（不再因单 ID 为空而 blocked）")
    r2 = make_plugin(mod, plugin_uninstall_ids=[])._build_plugin_uninstall_status(clean=False)
    check(bool(r2.get("blocked")) and r2.get("success") is False, "空目标 -> blocked，不误删")
    api_uninstall_empty = make_plugin(mod, plugin_uninstall_ids=[]).api_preview_plugin_uninstall()
    check(api_uninstall_empty.get("code") == 1 and "选择目标插件" in api_uninstall_empty.get("msg", ""),
          "插件卸载预览无目标时提示用户先选择插件")
    _PU.update({"installed": ["AutoBackup", "OtherPlugin"], "removed_plugins": [], "removed_jobs": [],
                "config_deleted": [], "data_deleted": [], "folders": {"系统": ["AutoBackup", "OtherPlugin"]}})
    p_payload = make_plugin(mod, plugin_uninstall_ids=[], plugin_uninstall_remove_plugin=False,
                            plugin_uninstall_clear_config=True, plugin_uninstall_clear_data=True)
    try:
        api_payload = p_payload.api_run_plugin_uninstall({
            "plugin_uninstall_ids": ["AutoBackup"],
            "plugin_uninstall_remove_plugin": True,
            "plugin_uninstall_clear_config": False,
            "plugin_uninstall_clear_data": False,
        })
        payload_error = ""
    except TypeError as err:
        api_payload = {}
        payload_error = str(err)
    check(not payload_error, "插件卸载执行接口接受当前表单 payload")
    if not payload_error:
        check(api_payload.get("code") == 0 and "AutoBackup" in _PU["removed_plugins"],
              "未保存配置时也按 payload 执行插件卸载")
        check(p_payload._plugin_uninstall_ids == [] and p_payload._plugin_uninstall_remove_plugin is False,
              "本次 payload 不污染实例保存的插件卸载配置")
        check("AutoBackup" not in _PU["config_deleted"] and "AutoBackup" not in _PU["data_deleted"],
              "payload 清理开关仅作用于本次执行")
    r3 = make_plugin(mod, plugin_uninstall_ids=["moviepilot"])._build_plugin_uninstall_status(clean=True)
    check(r3.get("success") is False and any("moviepilot" in e.lower() for e in r3.get("errors", [])),
          "禁止治理 MoviePilot/本体（保护）")
    r4 = make_plugin(mod, plugin_uninstall_ids=["A", "B"])._build_plugin_uninstall_status(clean=False)
    check(r4.get("plugin_id") == "A、B", "多个插件 ID 合并展示")
    _PU.update({"installed": ["AutoBackup", "OtherPlugin"], "removed_plugins": [], "removed_jobs": [],
                "config_deleted": [], "data_deleted": [], "folders": {"系统": ["AutoBackup", "OtherPlugin"]}})
    r5 = make_plugin(mod, plugin_uninstall_ids=["AutoBackup"])._build_plugin_uninstall_status(clean=True)
    check(r5.get("success") is True and "AutoBackup" in _PU["removed_plugins"]
          and "AutoBackup" not in _PU["installed"] and "AutoBackup" in _PU["removed_jobs"],
          "默认执行插件卸载：移出已安装列表、移除调度并卸载运行实例")
    check("AutoBackup" in _PU["config_deleted"] and "AutoBackup" in _PU["data_deleted"],
          "勾选清理配置/数据时调用 MoviePilot 配置与数据清理")
    _PU.update({"installed": ["AutoBackup"], "removed_plugins": [], "removed_jobs": [],
                "config_deleted": [], "data_deleted": [], "folders": {"系统": ["AutoBackup"]}})
    r6 = make_plugin(mod, plugin_uninstall_ids=["AutoBackup"], plugin_uninstall_remove_plugin=False)._build_plugin_uninstall_status(clean=True)
    check(r6.get("success") is True and not _PU["removed_plugins"] and _PU["installed"] == ["AutoBackup"],
          "关闭卸载插件时只做残留清理，不移除已安装插件")
    with tempfile.TemporaryDirectory() as tmpdir:
        outside = Path(tmpdir) / "outside-residue.txt"
        outside.write_text("keep me", encoding="utf-8")
        p_uninstall_guard = make_plugin(mod, plugin_uninstall_ids=["UnsafePlugin"], plugin_uninstall_remove_plugin=False)
        p_uninstall_guard._plugin_uninstall_candidates = lambda pid, **_: [{
            "plugin_id": pid,
            "kind": "local_source",
            "path": str(outside),
            "type": "file",
            "size": 7,
            "size_text": "7 B",
            "mtime": "2026-06-18 00:00:00",
        }]
        p_uninstall_guard._backup_plugin_uninstall_candidates = lambda pid, candidates: ""
        guarded = p_uninstall_guard._build_plugin_uninstall_status(clean=True)
        check(outside.exists() and guarded.get("success") is False and any("越界" in e or "不在允许范围" in e for e in guarded.get("errors", [])),
              "插件卸载删除前校验候选路径必须在允许根目录内")

    print("== 插件库更新增强：自动更新已安装插件 ==")
    def _reset_pu(**kw):
        _PU.update({"online": [], "local": [], "installed": [], "running": [],
                    "install_result": (True, "ok"), "install_calls": [], "reloaded": []})
        _PU.update(kw)
    # 开启自动安装 + 有新版 -> 下载安装 + reload + 记入 updated（带更新记录）
    _reset_pu(online=[fake_online("AutoBackup", "2.0", history={"v2.0": "修复X"})],
              local=[fake_local("AutoBackup", "1.0")], installed=["AutoBackup"])
    r = make_plugin(mod, market_update_auto_install=True)._auto_update_installed_plugins(apply=True)
    check(("AutoBackup", "https://repo.example/") in _PU["install_calls"]
          and any(x["id"] == "AutoBackup" for x in r["updated"]), "有新版+开启自动安装 -> 调 install 并记入 updated")
    check("AutoBackup" in _PU["reloaded"], "安装后 reload_plugin")
    check(r["updated"][0].get("history") == "修复X", "通知带该版本更新记录")
    # 关闭自动安装 -> 仅提醒，不安装
    _reset_pu(online=[fake_online("AutoBackup", "2.0")], local=[fake_local("AutoBackup", "1.0")], installed=["AutoBackup"])
    r = make_plugin(mod, market_update_auto_install=False)._auto_update_installed_plugins(apply=True)
    check(not _PU["install_calls"] and any(x["id"] == "AutoBackup" for x in r["updatable"]) and not r["updated"],
          "关闭自动安装 -> 仅 updatable 提醒，不调 install")
    # 排除名单 -> 跳过
    _reset_pu(online=[fake_online("AutoBackup", "2.0")], local=[fake_local("AutoBackup", "1.0")], installed=["AutoBackup"])
    r = make_plugin(mod, market_update_auto_install=True, market_update_exclude_ids="AutoBackup")._auto_update_installed_plugins(apply=True)
    check(not _PU["install_calls"] and any(x["id"] == "AutoBackup" for x in r["skipped"]), "排除名单 -> 跳过不安装")
    # 本插件自身 -> 永不自动更新
    _reset_pu(online=[fake_online("AgentOpsAssistant", "9.9")], local=[fake_local("AgentOpsAssistant", "1.0")], installed=["AgentOpsAssistant"])
    make_plugin(mod, market_update_auto_install=True)._auto_update_installed_plugins(apply=True)
    check(not _PU["install_calls"], "本插件自身永不自动更新")
    # 正在运行 + 跳过开启 -> 跳过
    _reset_pu(online=[fake_online("AutoBackup", "2.0")], local=[fake_local("AutoBackup", "1.0")],
              installed=["AutoBackup"], running=["AutoBackup"])
    r = make_plugin(mod, market_update_auto_install=True, market_update_skip_running=True)._auto_update_installed_plugins(apply=True)
    check(not _PU["install_calls"] and any(x.get("reason") == "正在运行" for x in r["skipped"]), "正在运行的插件跳过升级")

    print("== 订阅规则自动填充 ==")
    AOA = mod.AgentOpsAssistant
    check(AOA._parse_pix("2160p") == "4K|2160p|x2160", "_parse_pix 4K")
    check(AOA._parse_pix("1080p") == "1080[pi]|x1080", "_parse_pix 1080")
    check(AOA._parse_type("WEB-DL") == "WEB-?DL|WEB-?RIP", "_parse_type WEB-DL")
    check(AOA._parse_type("Remux") == "Remux", "_parse_type Remux")
    p = make_plugin(mod, subfill_enabled=True, subfill_details="分辨率,资源质量,制作组")
    meta = types.SimpleNamespace(resource_pix="2160p", resource_type="WEB-DL", resource_effect=None, resource_team="FRDS", customization=None)
    sub_empty = types.SimpleNamespace(type="电视剧", name="A", resolution=None, quality=None, effect=None, include=None, sites=None)
    upd = p._subfill_build_update(sub_empty, meta, types.SimpleNamespace(site=None))
    check(upd.get("resolution") == "4K|2160p|x2160" and upd.get("quality") == "WEB-?DL|WEB-?RIP" and upd.get("include") == "FRDS",
          "回填 分辨率/资源质量/制作组")
    sub_set = types.SimpleNamespace(type="电视剧", name="B", resolution="1080[pi]|x1080", quality=None, effect=None, include=None, sites=None)
    check("resolution" not in p._subfill_build_update(sub_set, meta, None), "已设置的字段不被覆盖")
    p0 = make_plugin(mod, subfill_enabled=True, subfill_details="")
    check(p0._subfill_build_update(sub_empty, meta, None) == {}, "未选填充项 -> 空")
    # 事件端到端
    _SUB.update({"history": types.SimpleNamespace(type="电视剧", tmdbid=123, seasons="S01"),
                 "subs": [types.SimpleNamespace(id=7, type="电视剧", name="剧X", resolution=None, quality=None, effect=None, include=None, sites=None)],
                 "updates": []})
    ev = types.SimpleNamespace(event_data={"hash": "h1", "context": types.SimpleNamespace(meta_info=meta, torrent_info=types.SimpleNamespace(site=None))})
    pe = make_plugin(mod, subfill_enabled=True, subfill_details="分辨率,制作组")
    pe.on_download_fill_subscribe(ev)
    check(_SUB["updates"] and _SUB["updates"][0][0] == 7 and _SUB["updates"][0][1].get("resolution") == "4K|2160p|x2160",
          "下载事件 -> 调 SubscribeOper.update 回填")
    pe.on_download_fill_subscribe(ev)
    check(len(_SUB["updates"]) == 1, "同一剧集只填充一次（去重）")
    _SUB.update({"history": types.SimpleNamespace(type="电视剧", tmdbid=456, seasons="S01"),
                 "subs": [types.SimpleNamespace(id=8, type="电视剧", name="剧Y", resolution=None, quality=None, effect=None, include=None, sites=None)],
                 "updates": []})
    pf = make_plugin(mod, fusion_notify_enabled=True, subfill_enabled=True, subfill_details="分辨率",
                     daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    subfill_upserts = []
    pf._tg_console_upsert_card = lambda token, chat_id, state: subfill_upserts.append(state) or True
    pf.on_download_fill_subscribe(ev)
    subfill_state = pf.get_data("tg_console_state") or {}
    subscribe_items = (((subfill_state.get("columns") or {}).get("subscribe") or {}).get("items") or [])
    check(subfill_upserts and subscribe_items and "订阅规则自动填充" in subscribe_items[0].get("title", "")
          and not pf._stub_messages,
          "融合通知开启时订阅规则填充结果无视组件通知开关，统一写入订阅融合栏目")
    _SUB.update({"history": types.SimpleNamespace(type="电影", tmdbid=5, seasons=""), "subs": [], "updates": []})
    make_plugin(mod, subfill_enabled=True, subfill_details="分辨率").on_download_fill_subscribe(ev)
    check(not _SUB["updates"], "非电视剧下载 -> 不填充")

    print("== 媒体库服务器通知 ==")
    check(AOA._msg_group_of("playback.start") == "开始播放", "事件归类 playback.start->开始播放")
    check(AOA._msg_group_of("ItemAdded") == "新入库", "ItemAdded->新入库")
    check(AOA._msg_group_of("unknown.x") is None, "未知事件 -> None")
    info = types.SimpleNamespace(event="playback.start", item_type="TV", item_name="入青云 S1E5 纪伯宰亲自为明意上药", user_name="卓",
                                 device_name="AfuseKt", client="", ip="172.17.0.1", percentage=None, overview=None,
                                 item_id="i1", server_name="Emby1", channel="emby", image_url=None)
    pm = make_plugin(mod, msgnotify_enabled=True, msgnotify_types="开始播放,新入库",
                     daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    media_upserts = []
    pm._tg_console_upsert_card = lambda token, chat_id, state: media_upserts.append(sorted((state.get("reports") or {}).keys())) or True
    pm.on_webhook_message(types.SimpleNamespace(event_data=info))
    check(media_upserts == [["media_activity"]] and not pm._stub_messages, "开始播放 -> 只流式写入融合卡，不发独立 MP 通知")
    media_state = pm.get_data("tg_console_state") or {}
    media_text = (((media_state.get("reports") or {}).get("media_activity") or {}).get("text") or "")
    check("卓" in media_text and "AfuseKt" in media_text and "172.17.0.1 本地局域网" in media_text,
          "融合卡媒体活动正文含用户、设备和局域网 IP")
    media_headline = pm._build_fusion_media_headline(media_state)
    check("开始播放剧集 入青云 S1E5 纪伯宰亲自为明意上药" in media_headline
          and "设备：AfuseKt" in media_headline
          and "用户：卓" in media_headline
          and "IP地址：172.17.0.1 本地局域网" in media_headline
          and "───────────────────" not in media_headline
          and media_headline.startswith("<blockquote>")
          and media_headline.endswith("</blockquote>"),
          "融合通知顶部媒体块应在系统行下展示播放状态、设备、用户和 IP，并用引用框隔开")
    media_full_html = pm._build_tg_console_html(media_state)
    system_idx = media_full_html.find("🤖 系统：")
    media_idx = media_full_html.find("开始播放剧集 入青云 S1E5")
    hint_idx = media_full_html.find("请点击下方的横向分类按钮")
    check(0 <= system_idx < media_idx < hint_idx,
          "媒体播放流必须显示在系统行下方、栏目提示语上方")
    pm_fusion_default = make_plugin(mod, msgnotify_enabled=False, msgnotify_types=[],
                                    daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    default_media_upserts = []
    pm_fusion_default._tg_console_upsert_card = lambda token, chat_id, state: default_media_upserts.append(state) or True
    default_info_data = vars(info).copy()
    default_info_data["item_id"] = "i-default"
    pm_fusion_default.on_webhook_message(types.SimpleNamespace(event_data=types.SimpleNamespace(**default_info_data)))
    default_media_state = pm_fusion_default.get_data("tg_console_state") or {}
    check(default_media_upserts
          and "开始播放剧集 入青云 S1E5" in pm_fusion_default._build_tg_console_html(default_media_state)
          and not pm_fusion_default._stub_messages,
          "融合通知开启且媒体栏目启用时，播放 webhook 必须绕过旧媒体通知开关流式更新顶部卡片")
    default_media_state["active_tab"] = "download_media"
    default_media_state["tab_touched"] = True
    download_media_html = pm_fusion_default._build_tg_console_html(default_media_state)
    check(download_media_html.count("开始播放剧集 入青云 S1E5") == 1
          and "<summary>🎬 媒体动态</summary>" not in download_media_html,
          "播放动态只属于顶部实时区，下载与媒体栏目内不重复渲染播放事件")
    stale_stop_state = {
        "reports": {
            "media_activity": {
                "title": "媒体动态",
                "group": "停止播放",
                "raw_title": "停止播放剧集 入青云",
                "text": "停止播放剧集 入青云 S1E5\n设备：AfuseKt\n用户：卓",
                "level": "idle",
                "updated_at": "2000-01-01 00:00:00",
            }
        },
        "columns": {"media": {"items": []}},
    }
    check(pm._build_fusion_media_headline(stale_stop_state) == ""
          and "media_activity" not in (stale_stop_state.get("reports") or {}),
          "停止播放状态超过 5 分钟后必须从融合卡顶部消失")
    media_stats_state = {
        "reports": {
            "media_activity": {
                "title": "媒体动态",
                "text": "⦁ 电影 636 ｜ 电视剧 71 ｜ 剧集 2624 ｜ 用户 6",
                "level": "success",
            }
        },
        "columns": {
            "media": {
                "items": [{
                    "title": "媒体动态",
                    "text": "⦁ 电影 636 ｜ 电视剧 71 ｜ 剧集 2624 ｜ 用户 6",
                    "level": "success",
                }]
            }
        },
    }
    check(pm._build_fusion_media_headline(media_stats_state) == "",
          "融合通知顶部媒体块不能用媒体统计占位，媒体统计只属于日报统计栏目")
    media_stats_html = pm._build_tg_console_html(media_stats_state)
    check("电影 636" not in media_stats_html
          and "media_activity" not in (media_stats_state.get("reports") or {})
          and "media" not in (media_stats_state.get("columns") or {}),
          "融合通知渲染时要主动清理旧状态里的媒体统计占位，避免旧卡继续显示")
    check(not any("电影 636" in line for line in pm._fusion_tab_lines("media", media_stats_state, "🎬 媒体统计\n\n• 电影 636 ｜ 电视剧 71 ｜ 剧集 2624 ｜ 用户 6")),
          "融合通知媒体分类不能从日报媒体统计兜底，媒体通知只展示 webhook 事件")
    pm_other = make_plugin(mod, msgnotify_enabled=True, msgnotify_types="开始播放", msgnotify_notify_type="Other",
                           daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    other_upserts = []
    pm_other._tg_console_upsert_card = lambda token, chat_id, state: other_upserts.append(True) or True
    pm_other.on_webhook_message(types.SimpleNamespace(event_data=info))
    check(other_upserts and not pm_other._stub_messages,
          "融合卡开启后媒体通知不因 MP 消息类型回退")
    pm.on_webhook_message(types.SimpleNamespace(event_data=info))
    check(len(media_upserts) == 1, "同 item 重复事件 30s 内去重")
    pm_media_fail = make_plugin(mod, msgnotify_enabled=True, msgnotify_types="开始播放",
                                daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    pm_media_fail._tg_console_upsert_card = lambda token, chat_id, state: False
    pm_media_fail.on_webhook_message(types.SimpleNamespace(event_data=info))
    check(not pm_media_fail._stub_messages, "媒体活动融合卡更新失败时不准降级 MP 通知")
    pm2 = make_plugin(mod, msgnotify_enabled=True, msgnotify_types="新入库")
    pm2.on_webhook_message(types.SimpleNamespace(event_data=info))
    check(len(pm2._stub_messages) == 0, "未勾选事件类型 -> 不通知")
    pm3 = make_plugin(mod, msgnotify_enabled=False, msgnotify_types="开始播放")
    pm3.on_webhook_message(types.SimpleNamespace(event_data=info))
    check(len(pm3._stub_messages) == 0, "未启用 -> 不通知")
    pm4 = make_plugin(mod, msgnotify_enabled=True, msgnotify_types="开始播放", msgnotify_servers="OtherServer")
    pm4.on_webhook_message(types.SimpleNamespace(event_data=info))
    check(len(pm4._stub_messages) == 0, "服务器不在白名单 -> 不通知")

    print("== 订阅二级分类自定义填充 + 维护 ==")
    confs = "category:国漫,日番#resolution:1080p#quality:WEB-DL#include:简体#savepath:/media/动漫/{name}"
    pc = make_plugin(mod, subfill_category_enabled=True, subfill_category_confs=confs)
    parsed = pc._subfill_confs
    check("国漫" in parsed and "日番" in parsed, "二级分类配置解析：多分类拆分")
    check(parsed["国漫"]["include"] == "简体" and parsed["国漫"]["quality"] == "WEB-DL", "解析 include/quality 正确")
    _SUB.update({"sub_get": types.SimpleNamespace(id=3, name="某番", year="2026", type="电视剧"), "updates": []})
    ev_sub = types.SimpleNamespace(event_data={"subscribe_id": 3, "mediainfo": {"category": "国漫"}})
    pc.on_subscribe_added_fill(ev_sub)
    check(_SUB["updates"] and _SUB["updates"][0][0] == 3, "新增订阅命中分类 -> 调 update")
    upd_c = _SUB["updates"][0][1]
    check(upd_c.get("quality") == "WEB-?DL|WEB-?RIP" and upd_c.get("resolution") == "1080[pi]|x1080", "分类填充经规则正则解析")
    check(upd_c.get("save_path") == "/media/动漫/某番 (2026)", "savepath {name} 变量替换")
    _SUB.update({"sub_get": types.SimpleNamespace(id=4, name="X", year="", type="电视剧"), "updates": []})
    make_plugin(mod, subfill_category_enabled=True, subfill_category_confs=confs).on_subscribe_added_fill(
        types.SimpleNamespace(event_data={"subscribe_id": 4, "mediainfo": {"category": "未配置分类"}}))
    check(not _SUB["updates"], "未配置的分类 -> 不填充")
    ph = make_plugin(mod)
    ph.save_data("subfill_handled", ["电视剧:1"])
    ph.run_subfill_clear_handled()
    check(ph.get_data("subfill_handled") == [], "清理已处理记录 -> 置空")

    print("== 每日汇报聚合中心：逐栏目门控 + 站点状态逐站 ==")
    pr = make_plugin(mod, report_storage=False, report_media_stat=False)
    for name, val in [("_get_site_increment_locked", ["⦁ inc"]), ("_get_site_health_locked", ["⦁ 馒头 | 正常"]),
                      ("_get_transfer_health_locked", ["⦁ t"]), ("_get_today_subscribe_updates_locked", []),
                      ("_get_downloader_health_locked", ["⦁ d"]), ("_get_storage_health_locked", ["⦁ s"]),
                      ("_get_today_downloads_locked", ["⦁ dl"]), ("_get_media_stats_locked", ["⦁ m"]),
                      ("_version_report_lines", ["⦁ v"])]:
        setattr(pr, name, (lambda v=val: v))
    msg = pr._build_heartbeat_message()
    check(msg.startswith("📮 MP 运维日报｜"), "日报标题使用卡片式标题行")
    check("━━━━━━━━━━━━" not in msg, "日报不再使用扎眼的硬分割线")
    check("📡 站点状态" in msg and "📡 站点状态：" not in msg, "栏目标题去掉尾冒号，观感更清爽")
    check("• 馒头：✅ 正常" in msg, "正文项目统一使用更轻的圆点与状态图标")
    check("💾 存储空间" not in msg, "report_storage=False -> 日报不含存储空间")
    check("🎬 媒体统计" not in msg, "report_media_stat=False -> 日报不含媒体统计")
    check("📥 今日下载" in msg and "📡 站点状态" in msg, "默认栏目仍在")
    check("⬇️ 下载器" not in msg and "正在下载" not in msg, "下载器段已与今日下载去重移除")
    pr_preview_api = make_plugin(mod)
    pr_preview_api._build_daily_report_message = lambda *a, **k: "日报预览正文"
    pr_preview_result = pr_preview_api.api_preview_daily_report()
    check(pr_preview_result.get("code") == 0 and pr_preview_result.get("text") == "日报预览正文", "每日汇报 API 预览直接返回完整正文")
    check(not pr_preview_api._stub_messages and "last_daily_report" not in pr_preview_api._stub_data, "每日汇报 API 预览不发消息也不写执行状态")
    preview_data = pr_preview_result.get("data") or {}
    check("feishu_card" not in preview_data and "feishu_streaming_card" not in preview_data,
          "每日汇报 API 预览不返回飞书载荷，飞书流式卡片只作为 TG 富消息呈现参考")
    preview_rich = preview_data.get("telegram_rich_message") or {}
    check("<h2>" in (preview_rich.get("html") or "") and preview_rich.get("skip_entity_detection") is True and "markdown" not in preview_rich,
          "每日汇报 API 预览只返回 Telegram RichMessage HTML 载荷")
    p_fused_card = make_plugin(mod, tg_console_enabled=True, tg_console_suppress_individual_notifications=True)
    fused_state = p_fused_card._tg_console_state(chat_id="chat")
    p_fused_card._tg_console_set_report_section(
        fused_state,
        "daily_report",
        "立即刷新",
        "\n".join([
            "📮 MP 运维日报｜2026-06-22 周一",
            "少爷，今天的系统观察如下。",
            "🕒 2026-06-22 04:12:35",
            "",
            "🤖 MoviePilot",
            "",
            "• 当前版本：前端 1.0 / 后端 2.0",
            "• 最新版本：已是最新",
            "",
            "📡 站点状态",
            "",
            "• 馒头 | 正常",
            "• 红叶 | 异常（Cookie 失效）",
            "",
            "💾 存储空间",
            "",
            "• 本地：66.16 GB/283.75 GB ｜ 已用 23%",
            "• 115网盘：36.32 TB/70.00 TB ｜ 已用 52%",
            "",
            "🎬 媒体统计",
            "",
            "• 电影 643 ｜ 剧集 2581",
        ]),
        level="success",
    )
    p_fused_card._tg_console_set_report_section(fused_state, "health_check", "health", "状态：全部正常\n巡查项目：共 7 项，通过 7 项，异常 0 项", level="success")
    fused_state["notices"] = [{"time": "04:12:35", "title": "站点统计", "text": "已刷新 3 个站点", "level": "success"}]
    fused_html = p_fused_card._build_tg_console_html(fused_state)
    check("📮 MP 运维日报｜🕒" in fused_html
          and "给你送上今天的心跳播报" in fused_html
          and "🤖 系统：" in fused_html
          and "<br><b>🩺 站点：</b>" in fused_html
          and "MP 运维简报" not in fused_html
          and "<summary>今日汇报</summary>" not in fused_html,
          "融合通知不再套旧日报壳，系统/站点头部按两排展示")
    check(fused_html.count(p_fused_card._daily_greeting_locked()) == 1,
          "fusion TG card should render the greeting only once")
    system_line_from_daily = p_fused_card._build_fusion_system_line("", fused_state)
    check("0/0" not in system_line_from_daily and "1/2" in system_line_from_daily,
          "融合通知站点顶栏应优先从日报站点状态统计，避免新卡显示 0/0")
    fused_state_health_fallback = p_fused_card._tg_console_state(chat_id="chat")
    fused_state_health_fallback["reports"] = {
        "health_check": {
            "title": "健康巡查",
            "text": "⦁ 状态：全部正常\n⦁ 巡查项：共 7 项，通过 7 项，异常 0 项\n⦁ 正常项：订阅、站点、下载器、本插件任务、数据库、存储空间、目录权限",
            "level": "success",
        },
        "site_stat": {
            "title": "站点增量",
            "text": "⦁ 馒头：⬆ 10.00 GB ｜ ⬇ 2.00 GB｜📊 3.405｜🪙 18,619.5",
            "level": "success",
        },
    }
    fused_state_health_fallback["columns"] = {
        "site_stats": {
            "items": [{
                "title": "站点增量",
                "text": "⦁ 馒头：⬆ 10.00 GB ｜ ⬇ 2.00 GB｜📊 3.405｜🪙 18,619.5",
                "level": "success",
            }]
        }
    }
    p_fused_card.save_data("last_health_check", {
        "success": True,
        "checks": [{"name": "sites", "ok": True, "detail": "共 7 个，启用 7 个"}],
        "output": "⦁ 状态：全部正常\n⦁ ✅ 站点：共 7 个，启用 7 个",
    })
    system_line_from_health = p_fused_card._build_fusion_system_line("", fused_state_health_fallback)
    check("7/7" in system_line_from_health and "1/1" not in system_line_from_health,
          "融合通知站点顶栏在健康巡查摘要丢失数量时，应读取 last_health_check 的站点数量，不能把站点增量的一条记录当作 1/1")
    p_fused_no_site_health = make_plugin(mod, tg_console_enabled=True, tg_console_suppress_individual_notifications=True)
    fused_state_site_columns = p_fused_no_site_health._tg_console_state(chat_id="chat")
    fused_state_site_columns["reports"] = {"daily_report": {"text": ""}}
    fused_state_site_columns["columns"] = {
        "site_stats": {
            "items": [
                {"title": "馒头", "text": "馒头：⬆ 10.00 GB ｜ ⬇ 2.00 GB", "level": "success"},
                {"title": "红叶", "text": "红叶：⬆ 1.00 GB ｜ ⬇ 500 MB", "level": "success"},
            ]
        }
    }
    system_line_from_site_columns = p_fused_no_site_health._build_fusion_system_line("", fused_state_site_columns)
    check("正常 (2/2)" not in system_line_from_site_columns and "失败 (0/2)" not in system_line_from_site_columns,
          "融合通知站点顶栏没有真实站点状态时不能从站点增量栏目推导在线站点，避免把增量条数误算成站点健康数")
    check("\u5b58\u50a8\u7a7a\u95f4\u76d1\u63a7\u77e9\u9635" not in fused_html
          and "\u7ad9\u70b9\u7ea2\u7eff\u706f\u72b6\u6001\u8231" not in fused_html
          and "\u66f4\u65b0\u8bb0\u5f55" not in fused_html
          and "🆙 更新提醒" not in fused_html,
          "融合通知隐藏旧错误标题，且无更新时不展示更新提醒")
    check("卡片内交互" not in fused_html
          and "/aoa_daily" not in fused_html
          and "/aoa_site" not in fused_html,
          "TG 日报卡不再渲染不可点击的卡片内 slash command 说明")
    check("📊 订阅与站点" not in fused_html
          and "📊 订阅与站点详情" not in fused_html
          and "<summary>📈 站点增量</summary>" in fused_html
          and "<summary>📺 订阅追新</summary>" in fused_html
          and "馒头 | 正常" in fused_html and "红叶 | 异常" in fused_html
          and "站点红绿灯状态舱" not in fused_html,
          "融合通知默认卡取消大分类标题，直接展示站点统计及订阅追新小栏目")
    fused_state_with_increment = p_fused_card._tg_console_state(chat_id="chat")
    fused_state_with_increment["columns"] = {
        "site_stats": {
            "items": [{
                "title": "站点统计",
                "text": "⦁ 馒头：⬆ 10.00 GB ｜ ⬇ 2.00 GB｜📊 3.405｜🪙 18,619.5",
                "level": "success",
                "time": "04:12:35",
                "updated_at": "2026-06-22 04:12:35",
            }]
        },
        "subscribe": {
            "items": [{
                "title": "订阅追新",
                "text": "⦁ 今日暂无订阅追新",
                "level": "success",
                "time": "04:12:35",
                "updated_at": "2026-06-22 04:12:35",
            }]
        },
    }
    fused_increment_html = p_fused_card._build_tg_console_html(fused_state_with_increment)
    fused_increment_visible = fused_increment_html.replace("\u200b", "")
    check("📈 站点增量" in fused_increment_visible
          and "站点统计：⦁" not in fused_increment_visible
          and "订阅追新：⦁" not in fused_increment_visible
          and "<ul>" in fused_increment_visible
          and "<li><b>📈 馒头</b>" in fused_increment_visible
          and "馒头" in fused_increment_visible
          and "3.405" in fused_increment_visible
          and "18,619" in fused_increment_visible,
          "融合通知站点栏目按增量口径展示，使用紧凑行距并去掉重复话术")
    check("<table" not in fused_html and "&nbsp;" not in fused_html and "🕓" not in fused_html,
          "融合通知卡片不再渲染旧 footer 或桌面表格布局")
    p_fused_empty = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    empty_state = p_fused_empty._tg_console_state(chat_id="chat")
    empty_html = p_fused_empty._build_tg_console_html(empty_state)
    check("💡 请点击下方的横向分类按钮，查阅今日具体运行指标。" in empty_html
          and "📊 站点统计详情" not in empty_html
          and "暂无站点统计数据" not in empty_html
          and "暂无站点统计" not in empty_html,
          "新建融合通知卡初始态只显示头部和横向栏目提示，不渲染默认站点空详情")
    reply_markup = p_fused_card._build_tg_console_reply_markup(fused_state)
    tg_button_labels = [btn.get("text") for row in reply_markup.get("inline_keyboard", []) for btn in row]
    tg_callback_data = [btn.get("callback_data") for row in reply_markup.get("inline_keyboard", []) for btn in row]
    expected_fusion_tabs = [f"{x['icon']} {x['label']}"[:20] for x in p_fused_card._fusion_category_registry()]
    check(tg_button_labels == expected_fusion_tabs
          and "立即建卡" not in tg_button_labels
          and "立即刷新" not in tg_button_labels,
          "融合通知 inline keyboard 只展示大分类横向按钮")
    check(len(reply_markup.get("inline_keyboard", [])) == 2
          and [len(row) for row in reply_markup.get("inline_keyboard", [])] == [2, 2],
          "融合通知大分类按钮按两行收束，避免信息过散")
    check(all(str(x or "").startswith("[PLUGIN]AgentOpsAssistant|aoatab:") and not str(x or "").startswith("aoa:tab:") and len(str(x or "").encode("utf-8")) <= 64 for x in tg_callback_data),
          "融合通知大分类 callback_data 使用 MP [PLUGIN] 通道，避免 MoviePilot 报回调数据格式错误")
    p_fused_card._get_local_versions = lambda: {"backend_version": "v2.13.10", "frontend_version": "v2.13.10"}
    update_button_state = p_fused_card._tg_console_state(chat_id="chat")
    update_button_state["reports"] = {
        "updates": {
            "title": "更新检查",
            "text": "MoviePilot：有更新｜后端 v2.13.12 -> v2.13.14",
            "level": "warning",
            "data": {"moviepilot": {"has_update": True, "checks": [
                {"type": "后端", "local_version": "v2.13.10", "latest_version": "v2.13.14", "has_update": True},
            ]}},
        }
    }
    update_reply_markup = p_fused_card._build_tg_console_reply_markup(update_button_state)
    update_button_labels = [btn.get("text") for row in update_reply_markup.get("inline_keyboard", []) for btn in row]
    check("🆙 立即更新" in update_button_labels,
          "融合通知检测到 MoviePilot 有新版时应在 TG 交互按钮中追加立即更新")
    p_fused_card._get_local_versions = lambda: {"backend_version": "v2.13.15", "frontend_version": "v2.13.15"}
    stale_update_state = p_fused_card._tg_console_state(chat_id="chat")
    stale_update_state["reports"] = {
        "updates": {
            "title": "更新检查",
            "text": "MoviePilot：有更新｜后端 v2.13.12 -> v2.13.14",
            "level": "warning",
            "data": {"moviepilot": {"has_update": True, "checks": [
                {"type": "后端", "local_version": "v2.13.12", "latest_version": "v2.13.14", "has_update": True},
            ]}},
        }
    }
    stale_reply_markup = p_fused_card._build_tg_console_reply_markup(stale_update_state)
    stale_button_labels = [btn.get("text") for row in stale_reply_markup.get("inline_keyboard", []) for btn in row]
    stale_html = p_fused_card._build_tg_console_html(stale_update_state)
    check("🆙 立即更新" not in stale_button_labels
          and "待更新" not in stale_html
          and not p_fused_card._fusion_pending_update_label(stale_update_state, ""),
          "融合通知遇到旧更新状态低于当前版本时不能显示待更新或立即更新")
    stale_pending_state = p_fused_card._tg_console_state(chat_id="chat")
    stale_pending_state["reports"] = {
        "updates": {
            "title": "更新检查",
            "text": "MoviePilot：有更新｜后端 v2.13.12 -> v2.13.14",
            "level": "warning",
        }
    }
    stale_pending_state["pending_actions"] = {
        "oldnonce": {"action": "run_mp_update_apply", "label": "🆙 立即更新", "destructive": True},
    }
    stale_pending_html = p_fused_card._build_tg_console_html(stale_pending_state)
    stale_pending_markup = p_fused_card._build_tg_console_reply_markup(stale_pending_state)
    stale_pending_labels = [btn.get("text") for row in stale_pending_markup.get("inline_keyboard", []) for btn in row]
    check("待更新" not in stale_pending_html
          and "🆙 立即更新" not in stale_pending_labels
          and not stale_pending_state.get("pending_actions"),
          "融合通知渲染前必须清理旧文本和旧 pending action，当前真实版本更高时常态隐藏更新入口")
    persisted_stale_update_state = p_fused_card._tg_console_state(chat_id="chat")
    persisted_stale_update_state["reports"] = {
        "updates": {
            "title": "更新检查",
            "text": "MoviePilot：有更新｜后端 v2.13.12 -> v2.13.14",
            "level": "warning",
        }
    }
    persisted_stale_update_state["pending_actions"] = {
        "oldnonce": {"action": "run_mp_update_apply", "label": "🆙 立即更新", "destructive": True},
    }
    p_fused_card.save_data("tg_console_state", persisted_stale_update_state)
    p_fused_card.api_tg_console_status()
    persisted_after_status = p_fused_card.get_data("tg_console_state") or {}
    check("updates" not in (persisted_after_status.get("reports") or {})
          and not persisted_after_status.get("pending_actions"),
          "tg_console_status 应持久化清理旧更新状态和旧 run_mp_update_apply")
    fusion_default = p_fused_card._build_tg_console_html(fused_state)
    check("📮 MP 运维日报｜🕒" in fusion_default
          and "给你送上今天的心跳播报" in fusion_default
          and "💡 请点击下方的横向分类按钮，查阅今日具体运行指标。" in fusion_default
          and "🤖 系统：" in fusion_default
          and "📊 订阅与站点" not in fusion_default
          and "📊 订阅与站点详情" not in fusion_default
          and "<summary>📈 站点增量</summary>" in fusion_default
          and "<summary>📺 订阅追新</summary>" in fusion_default
          and "🩺 站点：" in fusion_default
          and "站点红绿灯状态舱" not in fusion_default
          and "存储空间监控矩阵" not in fusion_default,
          "融合通知默认卡使用订阅与站点小栏目，合并展示站点统计及订阅追新")
    fusion_columns_state = p_fused_card._tg_console_state(chat_id="chat")
    fusion_columns_state["reports"] = {"daily_report": {"text": ""}}
    fusion_columns_state["columns"] = {
        "site_stats": {"items": [{"title": "馒头", "text": "馒头：↑ 3.405GB / ↓ 18,619MB", "level": "success"}]},
        "subscribe": {"items": [{"title": "订阅追新", "text": "凡人修仙传 S01E50 已入库", "level": "success"}]},
        "download_transfer": {"items": [{"title": "今日入库", "text": "成功片 2026 已入库", "level": "success"}]},
        "media": {"items": [{"title": "媒体统计", "text": "⦁ 电影 120 ｜ 电视剧 46 ｜ 剧集 2300 ｜ 用户 3", "level": "success"}]},
        "health": {"items": [{"title": "健康巡查", "text": "状态：全部正常\n巡查项：数据库、存储空间", "level": "success"}]},
        "storage": {"items": [{"title": "存储空间", "text": "配置目录：可用 86GB", "level": "success"}]},
        "maintenance": {"items": [{"title": "维护任务", "text": "备份：最近一次成功", "level": "success"}]},
        "updates": {"items": [{"title": "更新检查", "text": "MoviePilot：当前已是最新", "level": "success"}]},
    }
    fusion_category_expectations = {
        "subscribe_site": ("<summary>📈 站点增量</summary>", "<ul>", "<li><b>📈 馒头</b>", "⬆️ 3.405 GB | ⬇️ 18,619 MB", "<summary>📺 订阅追新</summary>", "<li><b>📺 凡人修仙传"),
        "download_media": ("<summary>📥 今日下载</summary>", "今日暂无今日下载数据", "<summary>📦 入库整理</summary>", "<b>📥 成功片 2026 已入库</b>", "<summary>🎬 媒体统计</summary>", "电影 120"),
        "system_health": ("<summary>🩺 健康巡查</summary>", "<li><b>✅ 状态</b><br>全部正常</li>", "<li><b>🩺 巡查项</b><br>数据库、存储空间</li>"),
        "system_maintenance": ("<summary>💾 存储空间</summary>", "<li><b>💾 配置目录</b><br>可用 86 GB</li>", "<summary>🧰 维护任务</summary>", "<li><b>🧰 备份</b><br>最近一次成功</li>"),
    }
    section_template_html = p_fused_card._fusion_section_html(
        "site_stats",
        "📈 站点增量",
        ["馒头：↑ 28.23 GB ｜ ↓ 7.35 GB ｜ 分享率 6.943 ｜ 魔力 69,686.7"],
    )
    check("<ul>" in section_template_html
          and "<li><b>📈 馒头</b>" in section_template_html
          and "⬆️ 28.23 GB | ⬇️ 7.35 GB | 📊 6.943 | 🪙 69,686.7" in section_template_html
          and "上传：" not in section_template_html
          and "下载：" not in section_template_html
          and "馒头" in section_template_html
          and "<code>" not in section_template_html
          and "核心指标" not in section_template_html
          and "明细" not in section_template_html,
          "融合通知通用模板必须使用图5式列表模板，不再输出代码胶囊或散点日志")
    storage_template_html = p_fused_card._fusion_section_html(
        "storage",
        "💾 存储空间",
        ["媒体库：244.65 GB/931.51 GB ｜ 🟢 已用 26%"],
    )
    check("<li><b>💾 媒体库</b>" in storage_template_html
          and "244.65 GB/931.51 GB" in storage_template_html
          and "[██░░░░░░] 🟢 已用 26%" in storage_template_html
          and "存储：" not in storage_template_html,
          "融合通知存储空间必须恢复进度条样式，展示用量/总量和已用百分比")
    stale_update_column_state = {
        "reports": {},
        "columns": {
            "updates": {"items": [{"title": "更新检查", "text": "MoviePilot：当前已是最新", "level": "success"}]},
        },
        "active_tab": "system_maintenance",
    }
    stale_update_column_html = p_fused_card._build_tg_console_html(stale_update_column_state)
    check("<summary>🆙 更新检查</summary>" not in stale_update_column_html
          and "🆙 更新提醒" not in stale_update_column_html,
          "融合通知必须忽略旧状态里的更新检查栏目，不再回渲染到 TG 卡")
    health_template_html = p_fused_card._fusion_section_html(
        "health",
        "🩺 健康巡查",
        ["状态：全部正常", "巡查项：共 7 项，通过 7 项，异常 0 项", "数据库：PostgreSQL 主库连接正常；SQLite 主库 user.db 连接正常"],
    )
    check("<li><b>✅ 状态</b><br>全部正常</li>" in health_template_html
          and "<li><b>🩺 巡查项</b><br>共 7 项，通过 7 项，异常 0 项</li>" in health_template_html
          and "<li><b>✅ 正常项</b><br>数据库</li>" in health_template_html
          and "PostgreSQL 主库连接正常" not in health_template_html,
          "融合通知健康巡查必须输出摘要文字，正常详情不能直接铺开")
    maintenance_template_html = p_fused_card._fusion_section_html(
        "maintenance",
        "🧰 维护任务",
        ["日志清理：成功｜插件日志清理结果：扫描文件 37 个，候选文件 20 个"],
    )
    check("<li><b>🧰 日志清理</b><br>成功<br>扫描 37 个，候选 20 个</li>" in maintenance_template_html
          and "插件日志清理结果" not in maintenance_template_html,
          "融合通知维护任务必须输出状态和关键数字摘要，不能直接铺日志原文")
    p_media_fallback = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_media_fallback._get_media_stats_locked = lambda: ["⦁ 电影 636 ｜ 电视剧 71 ｜ 剧集 2,624"]
    media_title, media_text, media_level = p_media_fallback._fusion_column_snapshot(
        "media", p_media_fallback._tg_console_state(chat_id="chat")
    )
    check(media_title == "媒体统计"
          and media_level == "success"
          and "电影 636" in media_text
          and "电视剧 71" in media_text
          and "剧集 2,624" in media_text
          and "暂无媒体" not in media_text,
          "下载与媒体栏目无播放动态时必须回退展示 MoviePilot 媒体统计，而不是暂无媒体动态")
    today = datetime.now().date().strftime("%Y-%m-%d")
    _SUB.update({
        "subs": [types.SimpleNamespace(name="完美世界", year="2021", type="电视剧", tmdbid=1001, season=1, episode_group=None)],
        "tmdb_episodes": [types.SimpleNamespace(air_date=today, episode_number=275)],
        "movie_mediainfo": None,
    })
    subscribe_items = p_fused_card._get_today_subscribe_updates_locked()
    check(any("完美世界" in item and "E275" in item for item in subscribe_items),
          "订阅追新必须识别 MoviePilot 日历同口径的今日剧集更新")
    _SUB.update({"subs": [], "tmdb_episodes": [], "movie_mediainfo": None})
    for category_key, fragments in fusion_category_expectations.items():
        fusion_columns_state["active_tab"] = category_key
        category_html = p_fused_card._build_tg_console_html(fusion_columns_state)
        check(all(fragment in category_html for fragment in fragments)
              and "<table" not in category_html
              and "<ul>" in category_html
              and "<li>" in category_html
              and "详情" not in category_html
              and "核心指标" not in category_html
              and "明细" not in category_html
              and not category_html.strip().startswith("<blockquote>"),
              f"融合通知 {category_key} 大分类使用清晰分组、图标行首和移动端友好的换行模板")
    p_fused_card._handle_tg_console_callback({
        "id": "cb-tab",
        "from": {"id": "u1"},
        "message": {"chat": {"id": "chat"}},
        "data": "aoa:tab:storage",
    }, update_id=100)
    switched_state = p_fused_card.get_data("tg_console_state") or {}
    check(switched_state.get("active_tab") == "system_maintenance", "旧三段式子栏目 callback 会兼容切换到所属大分类")
    storage_html = p_fused_card._build_tg_console_html(switched_state)
    check("🧰 系统维护" not in storage_html
          and "<summary>💾 存储空间</summary>" in storage_html
          and "<summary>🧰 维护任务</summary>" in storage_html
          and "<summary>🆙 更新检查</summary>" not in storage_html
          and "💾 存储空间" in storage_html
          and "🩺 健康巡查" not in storage_html,
          "active_tab=system_maintenance 时取消大分类标题，且不再展示更新检查栏目")
    p_fused_card._handle_tg_console_callback({
        "id": "cb-tab-new",
        "from": {"id": "u1"},
        "message": {"chat": {"id": "chat"}},
        "data": "aoatab:health",
    }, update_id=101)
    switched_new_state = p_fused_card.get_data("tg_console_state") or {}
    health_html = p_fused_card._build_tg_console_html(switched_new_state)
    check(switched_new_state.get("active_tab") == "system_health"
          and "<summary>🩺 健康巡查</summary>" in health_html
          and "💾 存储空间" not in health_html,
          "两段式健康子栏目 callback 会兼容切换到独立健康巡查大分类")
    callback_upserts = []
    p_dedupe = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_dedupe._tg_console_upsert_card = lambda token, chat_id, state: callback_upserts.append(state.get("active_tab")) or True
    p_dedupe._tg_console_answer_callback = lambda callback_id, text="": True
    cb = {"id": "cb-repeat", "from": {"id": "u1"}, "message": {"chat": {"id": "chat"}}, "data": "aoatab:system_maintenance"}
    check(p_dedupe._handle_tg_console_callback(cb, update_id=200) is True
          and p_dedupe._handle_tg_console_callback(cb, update_id=201) is True
          and callback_upserts == ["system_maintenance"],
          "重复 callback_query.id 只处理一次，避免横向栏目重复刷新")
    p_callback_refresh = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    refresh_calls = []
    refresh_html = []
    def _fake_refresh_column(key, state):
        refresh_calls.append(key)
        state.setdefault("columns", {})[key] = {
            "items": [{"title": "存储刷新", "text": "容量已更新", "level": "success", "time": "10:00", "updated_at": "2026-06-24 10:00:00"}],
            "updated_at": "2026-06-24 10:00:00",
        }
        return True
    p_callback_refresh._refresh_fusion_column = _fake_refresh_column
    p_callback_refresh._tg_console_upsert_card = lambda token, chat_id, state: refresh_html.append(p_callback_refresh._build_tg_console_html(state)) or True
    p_callback_refresh._tg_console_answer_callback = lambda callback_id, text="": True
    check(p_callback_refresh._handle_tg_console_callback({
        "id": "cb-refresh-tab",
        "from": {"id": "u1"},
        "message": {"chat": {"id": "chat"}},
        "data": "aoatab:system_maintenance",
    }, update_id=203) is True
          and refresh_calls == ["storage", "maintenance"]
          and refresh_html
          and "容量已更新" in refresh_html[-1],
          "点击融合大分类 callback 必须立即刷新所属子栏目数据并编辑同一张卡")
    p_message_action = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    message_action_refreshes = []
    p_message_action._refresh_fusion_column = lambda key, state: message_action_refreshes.append(key) or True
    p_message_action._tg_console_upsert_card = lambda token, chat_id, state: True
    message_action_handler = getattr(p_message_action, "on_message_action", None)
    if callable(message_action_handler):
        message_action_handler(types.SimpleNamespace(event_data={
            "plugin_id": "AgentOpsAssistant",
            "text": "aoatab:download_media",
            "userid": "u1",
            "original_chat_id": "chat",
            "original_message_id": 456,
        }))
    check(callable(message_action_handler)
          and p_message_action.get_data("tg_console_state").get("active_tab") == "download_media"
          and message_action_refreshes == ["download_transfer", "media"],
          "MoviePilot [PLUGIN] MessageAction 回调必须由插件接管并刷新对应大分类")
    invalid_answers = []
    p_invalid_tab = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_invalid_tab._tg_console_answer_callback = lambda callback_id, text="": invalid_answers.append(text) or True
    check(p_invalid_tab._handle_tg_console_callback({
        "id": "cb-bad-tab",
        "from": {"id": "u1"},
        "message": {"chat": {"id": "chat"}},
        "data": "aoa:tab:not_exists",
    }, update_id=202) is False and invalid_answers == ["未知栏目"],
          "未知融合栏目 callback 必须被拒绝并答复未知栏目")
    p_new_card = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    old_state = p_new_card._tg_console_state(chat_id="chat")
    old_state["message_id"] = 123
    old_state["reports"] = {"daily_report": {"text": "旧日报"}}
    p_new_card._save_tg_console_state(old_state)
    sent_payloads = []
    p_new_card._telegram_http_post_json = lambda url, payload, timeout=15: sent_payloads.append((url, payload)) or types.SimpleNamespace(
        ok=True,
        json=lambda: {"ok": True, "result": {"message_id": 456}},
        text='{"ok":true,"result":{"message_id":456}}',
    )
    new_card_res = p_new_card.api_create_tg_console_card()
    new_card_state = p_new_card.get_data("tg_console_state") or {}
    check(new_card_res.get("code") == 0
          and (new_card_res.get("data") or {}).get("code") == 0
          and (new_card_res.get("data") or {}).get("success") is True
          and "456" in ((new_card_res.get("data") or {}).get("msg") or "")
          and new_card_state.get("message_id") == 456
          and "sendRichMessage" in sent_payloads[-1][0]
          and not any("editMessageText" in x[0] for x in sent_payloads)
          and new_card_state.get("columns")
          and new_card_state.get("reports"),
          "立即建卡必须新发融合卡并预先刷新本次站点/订阅等栏目数据")
    leak_card_token = "123456:AAABBBCCCDDDEEEFFFGGGHHHIIIJJJ"
    p_new_card_fail = make_plugin(mod, daily_report_telegram_bot_token=leak_card_token, daily_report_telegram_chat_id="chat")
    p_new_card_fail._refresh_fusion_columns = lambda state: None
    p_new_card_fail._telegram_http_post_json = lambda url, payload, timeout=15: types.SimpleNamespace(
        ok=True,
        json=lambda: {"ok": False, "description": f"Bad Request: rich_message html is invalid for bot{leak_card_token}"},
        text=f'{{"ok":false,"description":"Bad Request: rich_message html is invalid for bot{leak_card_token}"}}',
    )
    failed_card_res = p_new_card_fail.api_create_tg_console_card()
    failed_card_state = p_new_card_fail.get_data("tg_console_state") or {}
    failed_card_text = json.dumps(failed_card_res, ensure_ascii=False) + json.dumps(failed_card_state, ensure_ascii=False)
    check(failed_card_res.get("code") == 1
          and (failed_card_res.get("data") or {}).get("code") == 1
          and (failed_card_res.get("data") or {}).get("success") is False
          and "sendRichMessage" in failed_card_res.get("msg", "")
          and "Bad Request" in failed_card_res.get("msg", "")
          and "Bad Request" in ((failed_card_res.get("data") or {}).get("last_error") or "")
          and leak_card_token not in failed_card_text
          and "bot***" in failed_card_text,
          "立即建卡失败时 API 必须透出 Telegram sendRichMessage 原因并脱敏 Bot Token")
    p_markup_send = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    markup_state = p_markup_send._tg_console_state(chat_id="chat")
    markup_payloads = []
    p_markup_send._build_tg_console_html = lambda state: "<h2>📮 MP 运维日报｜按钮测试</h2>"
    p_markup_send._telegram_http_post_json = lambda url, payload, timeout=15: markup_payloads.append((url, payload)) or types.SimpleNamespace(
        ok=True,
        json=lambda: {"ok": True, "result": {"message_id": 7001}},
        text='{"ok":true,"result":{"message_id":7001}}',
    )
    check(p_markup_send._tg_console_upsert_card("token", "chat", markup_state) is True
          and markup_payloads
          and "sendRichMessage" in markup_payloads[-1][0]
          and "reply_markup" in markup_payloads[-1][1],
          "sendRichMessage 创建日报卡时携带 TG inline keyboard")
    markup_payloads.clear()
    check(p_markup_send._tg_console_upsert_card("token", "chat", markup_state) is True
          and markup_payloads
          and "editMessageText" in markup_payloads[-1][0]
          and "reply_markup" in markup_payloads[-1][1],
          "editMessageText 更新日报卡时继续携带 TG inline keyboard")
    p_fused_defaults = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_fused_defaults._refresh_daily_report_live_data = lambda: {"success": True}
    p_fused_defaults._build_daily_report_message = lambda preview=False: "\U0001f4e6 MP 运维日报｜默认融合卡"
    default_fused_upserts = []
    p_fused_defaults._tg_console_upsert_card = lambda token, chat_id, state: default_fused_upserts.append(sorted((state.get("reports") or {}).keys())) or True
    p_fused_defaults._post_telegram_rich_message = lambda *a, **k: (_ for _ in ()).throw(AssertionError("daily report must not use standalone RichMessage"))
    check(p_fused_defaults._tg_console_enabled is True
          and p_fused_defaults._tg_console_suppress_individual_notifications is True,
          "fused card should be enabled by default and suppress standalone notifications")
    expected_fusion_report_keys = {
        "daily_report", "site_stat", "today_transfer", "subscribe_reminder",
        "storage", "media_stat", "health_check", "maintenance",
    }
    fusion_categories = {item["key"]: item["children"] for item in p_fused_defaults._fusion_category_registry()}
    check(fusion_categories.get("system_health") == ["health"]
          and fusion_categories.get("system_maintenance") == ["storage", "maintenance"]
          and p_fused_defaults._normalize_fusion_tab("health") == "system_health"
          and p_fused_defaults._normalize_fusion_tab("storage") == "system_maintenance",
          "TG 融合卡要拆分系统类目：健康巡查独立，系统维护只放存储空间和维护任务")
    check(p_fused_defaults.run_daily_report() is True
          and default_fused_upserts
          and set(default_fused_upserts[-1]) == expected_fusion_report_keys
          and (p_fused_defaults._stub_data.get("last_daily_report") or {}).get("message") == "OK tg_console_card",
          "daily report without legacy tg_console config should stream into the fused card")
    _PU["notifications"] = [
        {
            "name": "订阅 Telegram",
            "type": "telegram",
            "enabled": True,
            "switchs": ["订阅"],
            "config": {"TELEGRAM_TOKEN": "sub-token", "TELEGRAM_CHAT_ID": "-100sub"},
        },
        {
            "name": "插件 Telegram",
            "type": "telegram",
            "enabled": True,
            "switchs": ["插件"],
            "config": {"TELEGRAM_TOKEN": "plugin-token", "TELEGRAM_CHAT_ID": "-100plugin"},
        },
    ]
    p_fused_sub_channel = make_plugin(mod, fusion_notify_msgtype="Subscribe")
    sub_token, sub_chat, sub_source = p_fused_sub_channel._resolve_daily_report_telegram_config()
    check((sub_token, sub_chat) == ("sub-token", "-100sub") and "复用 MoviePilot 通知渠道：订阅 Telegram" == sub_source,
          "融合通知消息类型选择订阅时，应从 MP 订阅通知通道读取 Telegram 配置")
    p_fused_plugin_channel = make_plugin(mod, fusion_notify_msgtype="Plugin")
    plugin_token, plugin_chat, plugin_source = p_fused_plugin_channel._resolve_daily_report_telegram_config()
    check((plugin_token, plugin_chat) == ("plugin-token", "-100plugin") and "复用 MoviePilot 通知渠道：插件 Telegram" == plugin_source,
          "融合通知消息类型默认插件时，应从 MP 插件通知通道读取 Telegram 配置")
    p_fused_forced = make_plugin(mod, tg_console_enabled=False, tg_console_suppress_individual_notifications=False,
                                 daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    check(p_fused_forced._tg_console_enabled is True
          and p_fused_forced._tg_console_suppress_individual_notifications is True,
          "legacy false fused-card flags should be upgraded to streaming-only mode")
    p_schedule_off = make_plugin(
        mod,
        daily_report_enabled=True,
        daily_report_schedule_enabled=False,
        subscribe_reminder_enabled=True,
        subscribe_reminder_schedule_enabled=False,
        health_check_enabled=True,
        health_check_schedule_enabled=False,
        backup_enabled=True,
        backup_schedule_enabled=False,
        log_clean_enabled=True,
        log_clean_schedule_enabled=False,
        mp_update_enabled=True,
        mp_update_schedule_enabled=False,
        market_update_enabled=True,
        market_update_schedule_enabled=False,
        seedclean_enabled=True,
        seedclean_schedule_enabled=False,
        seedclean_downloaders=["qb"],
    )
    service_ids = {svc.get("id") for svc in p_schedule_off.get_service()}
    check(not any(x in service_ids for x in {
        "AgentOpsAssistant.DailyReport",
        "AgentOpsAssistant.SubscribeReminder",
        "AgentOpsAssistant.HealthCheck",
        "AgentOpsAssistant.Backup",
        "AgentOpsAssistant.LogClean",
        "AgentOpsAssistant.MPUpdate",
        "AgentOpsAssistant.MarketUpdate",
        "AgentOpsAssistant.SeedClean",
    }) and p_schedule_off._can_run_task("每日汇报", "daily_report")[0] is True,
          "独立定时开关关闭时不注册服务，但组件手动动作仍可运行")
    p_fusion_schedule = make_plugin(
        mod,
        fusion_notify_enabled=True,
        fusion_notify_schedule_enabled=True,
        fusion_notify_cron="0 * * * *",
        daily_report_enabled=True,
        daily_report_schedule_enabled=True,
        subscribe_reminder_enabled=True,
        subscribe_reminder_schedule_enabled=True,
        health_check_enabled=True,
        health_check_schedule_enabled=True,
        log_clean_enabled=True,
        log_clean_schedule_enabled=True,
        backup_enabled=True,
        backup_schedule_enabled=True,
        mp_update_enabled=True,
        mp_update_schedule_enabled=True,
        market_update_enabled=True,
        market_update_schedule_enabled=True,
        seedclean_enabled=True,
        seedclean_schedule_enabled=True,
        seedclean_downloaders=["qb"],
    )
    fusion_service_ids = {svc.get("id") for svc in p_fusion_schedule.get_service()}
    fusion_kept_service_ids = {
        "AgentOpsAssistant.HealthCheck",
        "AgentOpsAssistant.LogClean",
        "AgentOpsAssistant.Backup",
        "AgentOpsAssistant.MPUpdate",
        "AgentOpsAssistant.MarketUpdate",
        "AgentOpsAssistant.SeedClean",
    }
    check("AgentOpsAssistant.FusionNotify" in fusion_service_ids
          and "AgentOpsAssistant.DailyReport" not in fusion_service_ids
          and "AgentOpsAssistant.SubscribeReminder" not in fusion_service_ids
          and fusion_kept_service_ids <= fusion_service_ids,
          "融合通知开启时只替代日报和订阅追新这类通知定时，保留任务类定时服务")
    p_full_fusion = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_full_fusion._refresh_daily_report_live_data = lambda: {"success": True}
    p_full_fusion._build_daily_report_message = lambda preview=False: "daily"
    refreshed_columns = []
    p_full_fusion._refresh_fusion_column = lambda key, state: refreshed_columns.append(key) or True
    p_full_fusion._tg_console_upsert_card = lambda token, chat_id, state: True
    check(p_full_fusion.run_daily_report() is True
          and refreshed_columns == ["site_stats", "download_transfer", "subscribe", "storage", "media", "health", "maintenance"],
          "立即刷新融合通知时必须覆盖 7 个融合栏目")
    p_fused_flow = make_plugin(mod, tg_console_enabled=True, tg_console_suppress_individual_notifications=True,
                               daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_fused_flow._refresh_daily_report_live_data = lambda: {"success": True}
    p_fused_flow._build_daily_report_message = lambda preview=False: "\U0001f4e6 MP 运维日报｜单卡\n\n\U0001f4d7 站点状态\n\n• 馒头 | 正常"
    fused_upserts = []
    def _fake_fused_upsert(token, chat_id, state):
        action = "edit" if state.get("message_id") else "send"
        if action == "send":
            state["message_id"] = 9001
        fused_upserts.append((action, state.get("message_id"), sorted((state.get("reports") or {}).keys()), len(state.get("notices") or [])))
        return True
    p_fused_flow._tg_console_upsert_card = _fake_fused_upsert
    check(p_fused_flow.run_daily_report() is True, "fused card initial daily report should create the card")
    p_fused_flow._notify_or_console(title="MP 运维助手 - 健康巡查", text="状态：全部正常\n巡查项目：共 7 项，通过 7 项，异常 0 项")
    check([x[0] for x in fused_upserts] == ["send", "edit"]
          and fused_upserts[0][1] == fused_upserts[1][1] == 9001
          and "daily_report" in fused_upserts[1][2]
          and "health_check" in fused_upserts[1][2]
          and not p_fused_flow._stub_messages,
          "fused card should stream follow-up notifications into the same RichMessage")
    p_fused_no_downgrade = make_plugin(mod, tg_console_enabled=True, tg_console_suppress_individual_notifications=True,
                                        daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_fused_no_downgrade._tg_console_upsert_card = lambda token, chat_id, state: False
    check(p_fused_no_downgrade._notify_or_console(title="MP 运维助手 - 健康巡查", text="状态：全部正常") is False
          and not p_fused_no_downgrade._stub_messages,
          "fused card should not downgrade suppressed notifications to MP messages when stream update fails")
    fused_leak_token = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi"
    p_fused_notice_exception = make_plugin(mod, tg_console_enabled=True, tg_console_suppress_individual_notifications=True,
                                           daily_report_telegram_bot_token=fused_leak_token, daily_report_telegram_chat_id="chat")
    p_fused_notice_exception._tg_console_upsert_card = (
        lambda token, chat_id, state: (_ for _ in ()).throw(
            RuntimeError(f"boom https://api.telegram.org/bot{fused_leak_token}/editMessageText")
        )
    )
    check(p_fused_notice_exception._notify_or_console(title="MP 运维助手 - 健康巡查", text="状态：全部正常") is False
          and not p_fused_notice_exception._stub_messages
          and fused_leak_token not in (p_fused_notice_exception._tg_console_last_error or "")
          and "bot***" in (p_fused_notice_exception._tg_console_last_error or ""),
          "fused card notice update exceptions should be sanitized and must not downgrade to MP messages")
    p_individual_notice = make_plugin(mod, fusion_notify_enabled=False, health_check_enabled=True)
    check(p_individual_notice._tg_console_enabled is False
          and p_individual_notice._tg_console_suppress_individual_notifications is False
          and p_individual_notice._notify_or_console(title="MP 运维助手 - 健康巡查", text="状态：全部正常") is False
          and len(p_individual_notice._stub_messages) == 1,
          "关闭融合通知时才恢复组件自身通知设置")
    pr_pack = make_plugin(mod)
    packed = pr_pack._report_body_lines(["⦁ A", "⦁ B", "⦁ 这是一条比较长的内容，用来确认长信息不会被强行横向挤压而影响阅读"])
    check(packed[0] == "• A ｜ • B" and packed[1].startswith("• 这是一条比较长"), "短信息横向并排，长信息独占一行")
    status_grid = pr_pack._report_body_lines(["⦁ 馒头 | 正常", "⦁ 青蛙 | 正常", "⦁ 红叶 | 异常（连接超时）", "⦁ 柠檬 | 正常"])
    check(len(status_grid) == 2 and pr_pack._display_width(status_grid[0].split(" ｜ ")[0]) == pr_pack._display_width(status_grid[1].split(" ｜ ")[0]),
          "站点状态两列展示时中轴对齐，上下堆叠对称")
    icon_rows = pr_pack._report_body_lines([
        "⦁ 当前版本：前端 1.0 / 后端 2.0",
        "⦁ 失败：片名 - 路径不存在",
        "⦁ 电影 120 ｜ 电视剧 46 ｜ 剧集 2300 ｜ 用户 3",
    ])
    icon_text = "\n".join(icon_rows)
    check("🖥 前端 1.0 ｜ ⚙ 后端 2.0" in icon_text, "版本行改为图标化数据条")
    check("❌ 片名 ｜ 路径不存在" in icon_text, "入库整理只展示失败明细，方便定位")
    check("🎞 电影 120 ｜ 📺 电视剧 46 ｜ 🎞 剧集 2300 ｜ 👤 用户 3" in icon_text, "媒体统计改为图标化横向数据条")
    _SUB.update({"site_latest": [types.SimpleNamespace(name="馒头", domain="m.x", err_msg="超时", updated_day="")],
                 "sites": [types.SimpleNamespace(domain="m.x")]})
    sh = make_plugin(mod)._get_site_health_locked()
    check(any("馒头 | 异常" in x for x in sh), "站点状态逐站：异常格式 “馒头 | 异常（…）”")
    _today = datetime.now().strftime("%Y-%m-%d")
    _SUB.update({"site_latest": [types.SimpleNamespace(name="馒头", domain="m.x", err_msg="", updated_day=f"{_today} 08:30:00")],
                 "sites": [types.SimpleNamespace(domain="m.x")]})
    sh_today_time = make_plugin(mod)._get_site_health_locked()
    check(sh_today_time == ["⦁ 全部 1 个站点正常"], "站点状态：全正常时压缩为一行摘要，updated_day 带时间也识别为今日正常")

    p_summary_layout = make_plugin(mod)
    for name, val in [("_get_site_increment_locked", []), ("_get_site_health_locked", []),
                      ("_get_transfer_health_locked", []), ("_get_today_subscribe_updates_locked", []),
                      ("_get_downloader_health_locked", []), ("_get_storage_health_locked", []),
                      ("_get_today_downloads_locked", []), ("_get_media_stats_locked", []),
                      ("_version_report_lines", [])]:
        setattr(p_summary_layout, name, (lambda v=val: v))
    p_summary_layout._get_health_report_locked = lambda *a, **k: []
    summary_msg = p_summary_layout._build_heartbeat_message()
    check("\n🧾 今日摘要\n\n" in summary_msg and "• ✅ 今日摘要 ｜" not in summary_msg,
          "今日摘要作为独立小节展示，不再把标题和正文拼成同一行")
    p_card = make_plugin(mod, report_storage=False, report_media_stat=False)
    for name, val in [("_get_site_increment_locked", ["⦁ 馒头：⬆ 10.00 GB ｜ ⬇ 2.00 GB｜📊 3.405"]),
                      ("_get_site_health_locked", ["⦁ 馒头 | 正常"]),
                      ("_get_transfer_health_locked", ["⦁ 无"]),
                      ("_get_today_subscribe_updates_locked", []),
                      ("_get_downloader_health_locked", ["⦁ 在线 2 个"]),
                      ("_get_storage_health_locked", ["⦁ 本地：💽 76.34 GB/283.75 GB ｜ 🟢 已用 27%"]),
                      ("_get_today_downloads_locked", ["⦁ 无"]),
                      ("_get_media_stats_locked", ["⦁ 电影 120 ｜ 电视剧 46 ｜ 剧集 2300 ｜ 用户 3"]),
                      ("_version_report_lines", ["⦁ 当前版本：前端 1.0 / 后端 2.0"])]:
        setattr(p_card, name, (lambda v=val: v))
    p_card._get_health_report_locked = lambda *a, **k: ["⦁ 状态：全部正常", "⦁ 巡查项：共 7 项，通过 7 项，异常 0 项"]
    tg_rich = p_card._build_daily_report_telegram_rich_message(preview=True)
    tg_html = tg_rich.get("html", "")
    check(tg_rich.get("skip_entity_detection") is True and "markdown" not in tg_rich,
          "Telegram RichMessage 使用 html 且关闭实体猜测，不同时设置 markdown")
    check("📌 今日结论" in tg_html and "<th>看板</th>" not in tg_html and "站点：1 个，全部正常" in tg_html and "增量：↑ 10.00 GB / ↓ 2.00 GB" in tg_html,
          "Telegram RichMessage 首屏使用结论摘要，不再把总览做成后台表格")
    check("<details><summary>📈 站点增量</summary>" in tg_html and "<table>" not in tg_html and "<th" not in tg_html and "<b>📈 馒头</b><br>流量：↑" in tg_html and "<br>指标：分享" in tg_html and "<h3>📈 站点增量</h3>" not in tg_html and "<details><summary>📡 站点状态（1 个正常）</summary>" in tg_html and "<details><summary>📥 今日下载</summary>" in tg_html,
          "Telegram RichMessage 明细保留折叠，但移动端/桌面端都不能依赖宽表格布局")
    check("<li>无</li>" not in tg_html and tg_html.count("<li>📭 无</li>") >= 2,
          "Telegram RichMessage 通用折叠明细的空状态也必须图标化，不能退成裸文本“无”")
    check("🧾 今日摘要" not in tg_html and "系统正常" not in tg_html,
          "Telegram RichMessage 已有首屏结论时不再重复渲染底部今日摘要块")
    p_site_summary_count = make_plugin(mod, report_version=False, report_site_status=True, report_site_increment=False,
                                       report_today_download=False, report_transfer=False, report_subscribe=False,
                                       report_storage=False, report_media_stat=False, report_health=False, report_summary=False)
    _SUB.update({
        "sites": [types.SimpleNamespace(domain=f"s{i}.example") for i in range(1, 8)],
        "site_latest": [
            types.SimpleNamespace(name=name, domain=f"s{i}.example", err_msg="", updated_day=f"{_today} 08:30:00")
            for i, name in enumerate(["馒头", "青蛙", "红叶", "柠檬", "观众", "织梦", "麒麟"], start=1)
        ],
    })
    site_summary_html = p_site_summary_count._build_daily_report_telegram_html(preview=True)
    check("站点：7 个，全部正常" in site_summary_html and "📡 站点状态（7 个正常）" in site_summary_html and "站点：1 个" not in site_summary_html and "全部 1 个站点正常" not in site_summary_html and "📡 站点状态</b><br>全部 7 个站点正常" not in site_summary_html,
          "Telegram RichMessage 总览和站点折叠标题都正确解析压缩站点摘要里的真实站点数量，且不重复渲染站点摘要块")
    check("<li>✅ 馒头：正常</li>" in site_summary_html and "<li>✅ 麒麟：正常</li>" in site_summary_html and "<li>全部 7 个站点正常</li>" not in site_summary_html,
          "Telegram RichMessage 站点状态折叠明细必须带状态图标列出全正常站点名，不能只放压缩摘要")
    p_risk = make_plugin(mod, report_site_increment=False, report_today_download=False,
                         report_transfer=False, report_subscribe=False, report_storage=False,
                         report_media_stat=False, report_health=False, report_summary=False)
    p_risk._get_site_health_locked = lambda: ["⦁ 馒头 | 正常", "⦁ 红叶 | 异常（Cookie 失效）"]
    p_risk._version_report_lines = lambda: []
    risk_html = p_risk._build_daily_report_telegram_html(preview=True)
    check("🚨 站点风险</b>" in risk_html and "⚠️ 红叶：异常（Cookie 失效）" in risk_html and "<details><summary>📡 站点状态</summary>" in risk_html,
          "Telegram RichMessage 关键异常前置展示，同时保留完整折叠明细")
    p_cols_off = make_plugin(mod, report_version=False, report_site_status=False, report_site_increment=False,
                             report_today_download=False, report_transfer=False, report_subscribe=False,
                             report_storage=False, report_media_stat=False, report_health=False, report_summary=False)
    for name, val in [("_get_site_increment_locked", ["⦁ 馒头：⬆ 10.00 GB ｜ ⬇ 2.00 GB｜📊 3.405"]),
                      ("_get_site_health_locked", ["⦁ 馒头 | 正常"]),
                      ("_get_transfer_health_locked", ["⦁ 失败片 ｜ 硬链接失败"]),
                      ("_get_today_subscribe_updates_locked", ["今日新增订阅：2"]),
                      ("_get_downloader_health_locked", ["⦁ 在线 2 个"]),
                      ("_get_storage_health_locked", ["⦁ 本地：💽 76.34 GB/283.75 GB ｜ 🟢 已用 27%"]),
                      ("_get_today_downloads_locked", ["⦁ 星际穿越"]),
                      ("_get_media_stats_locked", ["⦁ 电影 120 ｜ 电视剧 46 ｜ 剧集 2300 ｜ 用户 3"]),
                      ("_version_report_lines", ["⦁ 当前版本：前端 1.0 / 后端 2.0"])]:
        setattr(p_cols_off, name, (lambda v=val: v))
    p_cols_off._get_health_report_locked = lambda *a, **k: ["⦁ 状态：发现 1 项异常"]
    cols_off_html = p_cols_off._build_daily_report_telegram_html(preview=True)
    check("📌 今日结论" not in cols_off_html and "📈 站点增量" not in cols_off_html and "📥 今日下载" not in cols_off_html and "🩺 健康巡查" not in cols_off_html,
          "Telegram RichMessage 必须尊重每日汇报栏目开关，关闭的栏目不能在总览或明细里残留")
    p_site_only = make_plugin(mod, report_version=False, report_site_status=True, report_site_increment=False,
                              report_today_download=False, report_transfer=False, report_subscribe=False,
                              report_storage=False, report_media_stat=False, report_health=False, report_summary=False)
    p_site_only._get_site_health_locked = lambda: ["⦁ 馒头 | 正常"]
    p_site_only._get_site_increment_locked = lambda: ["⦁ 馒头：⬆ 10.00 GB ｜ ⬇ 2.00 GB｜📊 3.405"]
    p_site_only._get_today_downloads_locked = lambda: ["⦁ 星际穿越"]
    site_only_html = p_site_only._build_daily_report_telegram_html(preview=True)
    check("📌 今日结论" in site_only_html and "站点：" in site_only_html and "增量：" not in site_only_html and "下载：" not in site_only_html and "健康：" not in site_only_html,
          "Telegram RichMessage 总览只汇总已开启栏目，不用关闭栏目凑版面")
    p_sub_live = make_plugin(mod)
    p_sub_live._load_subscribereminder_today_locked = lambda: ["早上缓存 S01E01"]
    p_sub_live._load_subscribereminder_today_realtime_locked = lambda: (True, ["当前实时 S01E02"])
    check(p_sub_live._get_today_subscribe_updates_locked() == ["当前实时 S01E02"],
          "每日汇报订阅追新优先实时计算，不能用当天早些时候的缓存覆盖当前数据")
    p_sub_empty = make_plugin(mod)
    p_sub_empty._load_subscribereminder_today_locked = lambda: ["早上缓存 S01E01"]
    p_sub_empty._load_subscribereminder_today_realtime_locked = lambda: (True, [])
    check(p_sub_empty._get_today_subscribe_updates_locked() == [],
          "每日汇报订阅追新实时结果为空时不能回填早些时候缓存")
    p_sub_error = make_plugin(mod)
    p_sub_error._load_subscribereminder_today_locked = lambda: ["缓存兜底 S01E03"]
    p_sub_error._load_subscribereminder_today_realtime_locked = lambda: (False, [])
    check(p_sub_error._get_today_subscribe_updates_locked() == ["缓存兜底 S01E03"],
          "每日汇报订阅追新仅在实时计算失败时才允许回退当天缓存")
    p_tg_http = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                            daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="12345")
    tg_calls = []
    cfg_settings = sys.modules["app.core.config"].settings
    proxy_conf = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
    cfg_settings.PROXY = proxy_conf
    old_requests = sys.modules.get("requests")
    def _tg_post(url, json=None, timeout=None, proxies=None):
        tg_calls.append((url, json, timeout, proxies))
        return types.SimpleNamespace(ok=True, status_code=200, text='{"ok":true}', json=lambda: {"ok": True})
    sys.modules["requests"] = types.SimpleNamespace(
        post=_tg_post
    )
    try:
        tg_http_ok = p_tg_http._post_telegram_rich_message({"html": "<h2>终态</h2>", "skip_entity_detection": True})
    finally:
        cfg_settings.PROXY = None
        if old_requests is None:
            sys.modules.pop("requests", None)
        else:
            sys.modules["requests"] = old_requests
    check(tg_http_ok and len(tg_calls) == 2 and tg_calls[0][0].endswith("/sendRichMessageDraft") and tg_calls[1][0].endswith("/sendRichMessage"),
          "Telegram 新机制先发送 30 秒 RichMessage 草稿预览，再发送终态 sendRichMessage")
    check(all(call[3] == proxy_conf for call in tg_calls),
          "Telegram RichMessage HTTP 请求必须复用 MoviePilot 全局代理 settings.PROXY")
    check(tg_calls[0][1].get("draft_id") and "<tg-thinking>" in tg_calls[0][1].get("rich_message", {}).get("html", ""),
          "Telegram RichMessageDraft 使用非零 draft_id 和 tg-thinking 占位")
    p_card._get_site_health_locked = lambda: ["⦁ A&B站 | 异常（<token>）"]
    escaped_tg_html = p_card._build_daily_report_telegram_html(preview=True)
    check("A&amp;B站" in escaped_tg_html and "&lt;token&gt;" in escaped_tg_html and "<token>" not in escaped_tg_html,
          "Telegram RichMessage 动态内容必须 HTML escape，避免站点名/错误详情破坏结构")
    long_cell = "VeryLongStorageNameWithoutNaturalBreakpoints1234567890ABCDEFGHIJK"
    long_storage_html = p_card._telegram_storage_table("", [f"⦁ {long_cell}：💽 /config/plugins/AgentOpsAssistant/Backup/weekly/archive/2026/06/20 ｜ 🟢 已用 26% <safe>"])
    media_html = p_card._telegram_media_table("", ["⦁ 电影 120 ｜ 电视剧 46 ｜ 剧集 2300 ｜ 用户 3"])
    health_icon_html = p_card._telegram_health_list_html(["状态：全部正常", "巡查项：共 7 项，通过 7 项，异常 0 项", "正常项：订阅、站点"])
    check("\u200b" in long_storage_html and long_cell not in long_storage_html and "&lt;safe&gt;" in long_storage_html and "<table>" not in long_storage_html and "<table>" not in media_html and "<b>💾" in long_storage_html and "<b>🎬 电影</b>" in media_html and "<b>👤 用户</b>" in media_html and "✅ 状态：全部正常" in health_icon_html,
          "Telegram RichMessage 长文本明细使用可换行的移动端友好块，同时为存储/媒体/健康明细补齐图标并保留 HTML escape")
    _SUB["site_refresh_error"] = None
    _SUB["site_refresh_result"] = {"馒头": object()}
    p_tg_send = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                            daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    fused_send_payloads = []
    p_tg_send._tg_console_upsert_card = lambda token, chat_id, state: fused_send_payloads.append(sorted((state.get("reports") or {}).keys())) or True
    p_tg_send._post_telegram_rich_message = lambda *a, **k: (_ for _ in ()).throw(AssertionError("daily report must use fused card"))
    check(p_tg_send.run_daily_report() is True and fused_send_payloads and set(fused_send_payloads[-1]) == expected_fusion_report_keys and not p_tg_send._stub_messages,
          "每日汇报只发送 Telegram RichMessage，不再发飞书或 MP 纯文本通知")
    check((p_tg_send._stub_data.get("last_daily_report") or {}).get("message") == "OK tg_console_card",
          "每日汇报成功状态明确记录融合通知卡已刷新")
    _SUB["site_refresh_calls"] = 0
    _SUB["site_refresh_result"] = {"馒头": object()}
    p_live_report = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                                daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    build_order = []
    health_order = []
    p_live_report._build_health_summary = lambda persist=True: health_order.append(_SUB["site_refresh_calls"]) or {
        "success": True, "checks": [], "total": 0, "pass": 0, "fail": 0
    }
    p_live_report._build_daily_report_message = lambda preview=False: build_order.append(_SUB["site_refresh_calls"]) or "📮 MP 运维日报｜刷新后\n\n📡 站点状态\n\n• 全部 1 个站点正常"
    p_live_report._tg_console_upsert_card = lambda token, chat_id, state: True
    check(p_live_report.run_daily_report() is True and _SUB["site_refresh_calls"] == 1 and health_order == [1] and build_order == [1],
          "手动/定时每日汇报必须先刷新当时站点用户数据和健康巡查，再生成日报内容")
    _SUB["site_refresh_calls"] = 0
    p_live_preview = make_plugin(mod)
    preview_health_order = []
    p_live_preview._build_health_summary = lambda persist=True: preview_health_order.append("health") or {}
    p_live_preview._build_daily_report_message = lambda preview=False: "📮 MP 运维日报｜预览"
    check(p_live_preview.run_daily_report_preview() is True and _SUB["site_refresh_calls"] == 0 and preview_health_order == [],
          "每日汇报预览保持只读，不触发站点数据/健康巡查刷新副作用")
    _SUB["site_refresh_calls"] = 0
    _SUB["site_refresh_result"] = None
    p_refresh_stopped = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                                    daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    stopped_sent = []
    p_refresh_stopped._build_daily_report_message = lambda preview=False: stopped_sent.append("built") or "不应生成"
    p_refresh_stopped._post_telegram_rich_message = lambda rich, token=None, chat_id=None: stopped_sent.append(rich) or True
    stopped_ok = p_refresh_stopped.run_daily_report()
    stopped_last = p_refresh_stopped._stub_data.get("last_daily_report") or {}
    check(stopped_ok is False and _SUB["site_refresh_calls"] == 1 and not stopped_sent
          and stopped_last.get("sent") is False and "旧快照" in (stopped_last.get("error") or ""),
          "站点数据刷新被停止时，每日汇报必须取消发送，不能继续用旧快照误报")
    _SUB["site_refresh_calls"] = 0
    _SUB["site_refresh_result"] = {"馒头": object()}
    _SUB["site_refresh_error"] = "Cookie 失效"
    p_refresh_error = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                                  daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    error_sent = []
    p_refresh_error._build_daily_report_message = lambda preview=False: error_sent.append("built") or "不应生成"
    p_refresh_error._post_telegram_rich_message = lambda rich, token=None, chat_id=None: error_sent.append(rich) or True
    error_ok = p_refresh_error.run_daily_report()
    error_last = p_refresh_error._stub_data.get("last_daily_report") or {}
    check(error_ok is False and _SUB["site_refresh_calls"] == 1 and not error_sent
          and "Cookie 失效" in (error_last.get("error") or ""),
          "站点数据刷新异常时，每日汇报必须取消发送并记录真实错误")
    _SUB["site_refresh_error"] = None
    _SUB["site_refresh_result"] = {"馒头": object()}
    _SUB["site_refresh_calls"] = 0
    p_summary_site_refresh = make_plugin(mod, report_site_status=False, report_site_increment=False,
                                         report_summary=True, report_health=False,
                                         daily_report_telegram_rich_enabled=True,
                                         daily_report_telegram_bot_token="token",
                                         daily_report_telegram_chat_id="chat")
    p_summary_site_refresh._build_daily_report_message = lambda preview=False: "📮 MP 运维日报｜摘要"
    p_summary_site_refresh._tg_console_upsert_card = lambda token, chat_id, state: True
    check(p_summary_site_refresh.run_daily_report() is True and _SUB["site_refresh_calls"] == 1,
          "即使关闭站点栏目，只要日报摘要会读取站点状态，也必须先刷新当时站点数据")
    p_tg_fallback = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                                daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_tg_fallback._tg_console_upsert_card = lambda token, chat_id, state: False
    check(p_tg_fallback.run_daily_report() is False and not p_tg_fallback._stub_messages,
          "Telegram RichMessage 发送失败时日报任务失败，不回退 MP post_message 纯文本")
    check((p_tg_fallback._stub_data.get("last_daily_report") or {}).get("success") is False,
          "Telegram RichMessage 失败会保存失败状态供仪表盘展示")
    _PU["notifications"] = [{
        "name": "主 Telegram",
        "type": "telegram",
        "enabled": True,
        "config": {"TELEGRAM_TOKEN": "global-token", "TELEGRAM_CHAT_ID": "-100123"},
        "switchs": ["插件", "其它"],
    }]
    p_tg_global = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                              daily_report_telegram_bot_token="", daily_report_telegram_chat_id="")
    global_send = {}
    p_tg_global._tg_console_upsert_card = (
        lambda token, chat_id, state: global_send.update(token=token, chat_id=chat_id) or True
    )
    check(p_tg_global.run_daily_report() is True
          and global_send == {"token": "global-token", "chat_id": "-100123"},
          "旧配置未填写 TG 字段时，日报复用 MoviePilot 全局 Telegram 通知配置")
    p_tg_explicit = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                                daily_report_telegram_bot_token="plugin-token", daily_report_telegram_chat_id="67890")
    explicit_send = {}
    p_tg_explicit._tg_console_upsert_card = (
        lambda token, chat_id, state: explicit_send.update(token=token, chat_id=chat_id) or True
    )
    check(p_tg_explicit.run_daily_report() is True
          and explicit_send == {"token": "plugin-token", "chat_id": "67890"},
          "插件内显式 TG 配置优先于 MoviePilot 全局 Telegram")
    _PU["notifications"] = []
    p_tg_missing = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                               daily_report_telegram_bot_token="", daily_report_telegram_chat_id="")
    check(p_tg_missing.run_daily_report() is False
          and "Telegram" in ((p_tg_missing._stub_data.get("last_daily_report") or {}).get("error") or "")
          and "未配置" in ((p_tg_missing._stub_data.get("last_daily_report") or {}).get("error") or ""),
          "缺少插件 TG 且无全局 Telegram 时，日报失败原因要明确落盘")
    p_tg_detail = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                              daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_tg_detail._tg_console_upsert_card = (
        lambda token, chat_id, state:
        setattr(p_tg_detail, "_tg_console_last_error", "Telegram RichMessage 返回失败：Bad Request") or False
    )
    check(p_tg_detail.run_daily_report() is False
          and "Bad Request" in ((p_tg_detail._stub_data.get("last_daily_report") or {}).get("error") or ""),
          "Telegram API 返回的具体错误要写入 last_daily_report")
    leak_token = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi"
    p_tg_leak = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                            daily_report_telegram_bot_token=leak_token, daily_report_telegram_chat_id="12345")
    old_requests = sys.modules.get("requests")
    def _raise_leaky_error(url, **kwargs):
        raise RuntimeError(f"boom https://api.telegram.org/bot{leak_token}/sendRichMessage")
    sys.modules["requests"] = types.SimpleNamespace(post=_raise_leaky_error)
    try:
        check(p_tg_leak.run_daily_report() is False, "Telegram 请求异常时日报任务失败")
    finally:
        if old_requests is None:
            sys.modules.pop("requests", None)
        else:
            sys.modules["requests"] = old_requests
    leak_error = ((p_tg_leak._stub_data.get("last_daily_report") or {}).get("error") or "")
    check(leak_token not in leak_error and f"bot{leak_token}" not in leak_error and "bot***" in leak_error,
          "Telegram 请求异常写入 last_daily_report 前必须脱敏 Bot Token")
    p_tg_http_error = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                                  daily_report_telegram_bot_token=leak_token, daily_report_telegram_chat_id="12345")
    leaky_response = types.SimpleNamespace(
        ok=False,
        status_code=400,
        text=f'{{"ok":false,"description":"Bad /bot{leak_token}/sendRichMessage"}}',
        json=lambda: {"ok": False, "description": f"Bad /bot{leak_token}/sendRichMessage"},
    )
    check(p_tg_http_error._telegram_response_ok(leaky_response, "RichMessage") is False
          and leak_token not in p_tg_http_error._daily_report_telegram_last_error
          and "bot***" in p_tg_http_error._daily_report_telegram_last_error,
          "Telegram API 错误详情写入 last_daily_report 前必须脱敏 Bot Token")
    p_tg_console_leak = make_plugin(mod, tg_console_enabled=True,
                                    daily_report_telegram_bot_token=leak_token, daily_report_telegram_chat_id="12345")
    p_tg_console_leak._build_daily_report_message = lambda preview=False: "daily report"
    p_tg_console_leak._tg_console_upsert_card = (
        lambda token, chat_id, state: (_ for _ in ()).throw(
            RuntimeError(f"boom https://api.telegram.org/bot{leak_token}/editMessageText")
        )
    )
    check(p_tg_console_leak.run_daily_report() is False,
          "TG 控制台卡片异常时日报任务失败")
    console_leak_last = p_tg_console_leak._stub_data.get("last_daily_report") or {}
    console_leak_error = (console_leak_last.get("error") or "") + (console_leak_last.get("message") or "")
    check(leak_token not in console_leak_error and f"bot{leak_token}" not in console_leak_error and "bot***" in console_leak_error,
          "TG 控制台卡片异常写入 last_daily_report 前必须脱敏 Bot Token")
    config_vue = (ROOT / "plugins.v2" / "agentopsassistant" / "src" / "components" / "Config.vue").read_text(encoding="utf-8")
    check('label="Bot Token"' not in config_vue and 'label="Chat ID"' not in config_vue
          and 'label="Telegram RichMessage"' not in config_vue,
          "日报设置页不暴露插件私有 TG Bot Token/Chat ID，默认复用 MoviePilot 全局 Telegram 通知配置")
    check("preview_daily_report" not in config_vue and "预览完整日报" not in config_vue,
          "配置页不再暴露误导性的完整日报预览入口")
    check("quickCardActions" not in config_vue
          and "aoa-quick-card-actions" not in config_vue
          and "立即发送汇报" not in config_vue
          and "预览融合卡" not in config_vue
          and "立即健康巡查" not in config_vue,
          "配置页保持通用模板，不再渲染立即建卡/立即刷新快捷条")
    check("tg_console_status" in config_vue
          and "tgConsoleStatus" in config_vue
          and "最后更新" in config_vue
          and "最近错误" in config_vue,
          "Telegram 日报卡配置页要展示当前卡片状态、更新时间和错误")
    page_vue = (ROOT / "plugins.v2" / "agentopsassistant" / "src" / "components" / "Page.vue").read_text(encoding="utf-8")
    check("{ path: 'create_tg_console_card', component: '', label: '立即建卡'" in page_vue
          and "{ path: 'run_daily_report', component: 'daily_report', label: '立即刷新'" in page_vue
          and "{ path: 'run_daily_report', label: '每日汇报'" not in page_vue,
          "仪表盘提供立即建卡，并把手动日报按钮改为立即刷新")
    check("actionComponentEnabled" in page_vue
          and "actionComponentDisabledMessage" in page_vue
          and "{ path: 'run_site_stat', component: 'site_stat'" in page_vue
          and "{ path: 'run_seed_clean', component: 'seed_clean'" in page_vue
          and "{ path: 'run_downloader_tag', component: 'downloader_tag'" in page_vue,
          "Page 仪表盘命令面板按组件启用状态禁用手动动作")
    dashboard_vue = (ROOT / "plugins.v2" / "agentopsassistant" / "src" / "components" / "Dashboard.vue").read_text(encoding="utf-8")
    site_widget_vue = (ROOT / "plugins.v2" / "agentopsassistant" / "src" / "components" / "dashboard" / "SiteStatsWidget.vue").read_text(encoding="utf-8")
    actions_widget_vue = (ROOT / "plugins.v2" / "agentopsassistant" / "src" / "components" / "dashboard" / "ActionsWidget.vue").read_text(encoding="utf-8")
    check("{ path: 'create_tg_console_card', component: '', label: '立即建卡'" in dashboard_vue
          and "{ path: 'run_daily_report', component: 'daily_report', label: '立即刷新'" in dashboard_vue
          and "{ path: 'run_daily_report', component: 'daily_report', label: '每日汇报'" not in dashboard_vue,
          "独立 Dashboard 动作组件也提供立即建卡，并把每日汇报按钮改为立即刷新")
    theme_sources = {
        "Dashboard.vue": dashboard_vue,
        "Page.vue": page_vue,
        "Config.vue": config_vue,
        "SiteStatsWidget.vue": site_widget_vue,
        "ActionsWidget.vue": actions_widget_vue,
    }
    check(all("var(--app-surface-radius" in src for src in theme_sources.values()),
          "插件配置页、侧导航仪表盘和 MP 自由组件统一使用 MP 官方 --app-surface-radius")
    check(all("var(--app-surface-shadow" in src for src in theme_sources.values()),
          "插件配置页、侧导航仪表盘和 MP 自由组件统一使用 MP 官方 --app-surface-shadow")
    check(all("var(--app-surface-border" in src for src in theme_sources.values()),
          "插件配置页、侧导航仪表盘和 MP 自由组件统一使用 MP 官方 --app-surface-border")
    check(all('html[data-theme="transparent"]' in src and "--transparent-opacity" in src and "--transparent-blur" in src
              for src in theme_sources.values()),
          "插件所有入口跟随 MP 透明主题的 --transparent-opacity / --transparent-blur")
    banned_theme_fragments = [
        "--mp-widget-radius: 16px",
        "blur(18px) saturate(145%)",
        "blur(24px) saturate(150%)",
        "ensureDialogBackdropStyle",
        "dialogBackdropStyleId",
    ]
    check(not any(fragment in src for src in theme_sources.values() for fragment in banned_theme_fragments),
          "插件前端不再使用重自定义玻璃、固定圆角或自注入遮罩覆盖 MP 原生主题")
    check(".dashboard-shell--sidebar .top-button" in page_vue
          and ".dashboard-shell--sidebar .top-button:hover" in page_vue
          and ".dashboard-shell--sidebar .top-button :deep(.v-btn__overlay)" in page_vue
          and ".dashboard-shell--sidebar .top-button :deep(.v-btn__underlay)" in page_vue
          and '[class~="v-btn__overlay"]' in page_vue
          and '[class~="v-btn__underlay"]' in page_vue
          and "background: transparent !important;" in page_vue
          and "box-shadow: none !important;" in page_vue,
          "侧边栏仪表盘顶部按钮禁用 hover 隐形方框和 Vuetify overlay")
    check("MoviePilot 版本" not in config_vue
          and "今日摘要" not in config_vue
          and "fusion_notify_columns" in config_vue
          and "fusion_notify_msgtype" in config_vue
          and "融合通知消息类型" in config_vue
          and "下载器管理 > 下载入库" not in config_vue
          and "健康巡查 > 存储空间" not in config_vue
          and "对应插件" in config_vue
          and "数据范围" in config_vue
          and "媒体通知" in config_vue,
          "配置页融合通知栏目合并二级路径后按通用模板展示，并暴露融合通知消息类型")
    check("notificationLockedByFusion" in config_vue
          and 'label="启用定时追新" :disabled="!form.subscribe_reminder_enabled || notificationLockedByFusion"' in config_vue
          and 'label="执行更新结果通知" :disabled="!form.mp_update_enabled || notificationLockedByFusion"' in config_vue
          and 'label="消息类型" :disabled="!form.mp_update_enabled || !form.mp_update_notify || notificationLockedByFusion"' in config_vue,
          "融合通知开启时所有通知类设置锁定，订阅追新这类定时通知也由融合刷新控制")
    check("融合通知开启：插件内部通知统一写入 TG 融合卡；关闭后各组件通知渠道恢复生效。" in config_vue
          and "组件定时任务仍按各自设置执行" not in config_vue
          and "当前融合卡使用：" in config_vue
          and "已配置 ·" not in config_vue,
          "配置页只在融合通知位置说明通知边界，并避免表现成插件自带 Telegram 配置")
    _PU["notifications"] = [{
        "name": "默认 Telegram",
        "type": "telegram",
        "enabled": True,
        "config": {"TELEGRAM_TOKEN": "global-token", "TELEGRAM_CHAT_ID": "-100123"},
        "switchs": ["插件"],
    }]
    p_tg_disabled_legacy = make_plugin(mod, daily_report_telegram_rich_enabled=False,
                                       daily_report_telegram_bot_token="", daily_report_telegram_chat_id="")
    legacy_send = {}
    p_tg_disabled_legacy._tg_console_upsert_card = (
        lambda token, chat_id, state: legacy_send.update(token=token, chat_id=chat_id) or True
    )
    check(p_tg_disabled_legacy.run_daily_report() is True
          and legacy_send == {"token": "global-token", "chat_id": "-100123"},
          "旧配置里 RichMessage 开关为 False 时也必须迁移为默认 TG RichMessage，不让隐藏旧值打断日报")
    _PU["notifications"] = []

    print("== 日报下载与入库展示口径 ==")
    p_report = make_plugin(mod)
    p_report._today_transfer_rows_locked = lambda: []
    check(p_report._get_today_downloads_locked() == ["⦁ 无"], "今日下载无记录时只写无")
    check(p_report._get_transfer_health_locked() == ["⦁ 无"], "入库整理无失败时只写无")
    p_report._today_transfer_rows_locked = lambda: [
        types.SimpleNamespace(status=True, title="成功片", year="2026", type="电影"),
        types.SimpleNamespace(status=False, title="失败片", errmsg="硬链接失败"),
    ]
    downloads = p_report._get_today_downloads_locked()
    transfers = p_report._get_transfer_health_locked()
    check(all("今日下载：" not in x for x in downloads) and any("成功片" in x for x in downloads), "今日下载有内容时直接列片名，不展示数量摘要")
    check(transfers == ["⦁ 失败：失败片 - 硬链接失败"], "入库整理只列失败明细")
    p_today_transfer = make_plugin(mod, daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_today_transfer._today_transfer_rows_locked = lambda: [
        types.SimpleNamespace(status=True, title="成功片", year="2026", type="电影"),
        types.SimpleNamespace(status=False, title="失败片", errmsg="硬链接失败"),
    ]
    transfer_reports = []
    p_today_transfer._emit_console_report = lambda key, title, text, level="info": transfer_reports.append((key, title, text, level)) or True
    transfer_result = p_today_transfer.api_run_today_transfer()
    check(transfer_result.get("code") == 0
          and transfer_reports
          and transfer_reports[-1][0] == "today_transfer"
          and transfer_reports[-1][1] == "今日入库"
          and "成功片" in transfer_reports[-1][2]
          and "失败片" in transfer_reports[-1][2],
          "今日入库 TG 按钮/API 立即读取当前入库历史并写入同一张日报卡")

    print("== 站点数据统计饼图数据 ==")
    _today = datetime.now().strftime("%Y-%m-%d")
    _SUB.update({
        "sites": [types.SimpleNamespace(domain="m.x"), types.SimpleNamespace(domain="q.x")],
        "site_latest": [
            types.SimpleNamespace(name="馒头", domain="m.x", err_msg="", updated_day=_today, upload=100 * 1024 ** 3, download=10 * 1024 ** 3, ratio="3.405", bonus=18619.5),
            types.SimpleNamespace(name="青蛙", domain="q.x", err_msg="", updated_day=_today, upload=30 * 1024 ** 3, download=0),
        ],
        "site_prev": [
            types.SimpleNamespace(name="馒头", err_msg="", upload=90 * 1024 ** 3, download=8 * 1024 ** 3),
            types.SimpleNamespace(name="青蛙", err_msg="", upload=29 * 1024 ** 3, download=0),
        ],
    })
    chart = make_plugin(mod).api_site_stat_chart()
    cd = chart.get("data", {})
    check(chart.get("code") == 0 and cd.get("upload_total") == 11 * 1024 ** 3, "饼图：今日上传合计=各站增量之和(10+1 GB)")
    check(cd.get("download_total") == 2 * 1024 ** 3 and len(cd.get("sites", [])) == 2, "饼图：下载合计与站点数正确")
    check(cd.get("active_count") == 2 and cd.get("visible_count") == 2,
          "站点统计图返回 active_count/visible_count，供前端区分空态与真实站点数")
    inc_text = "\n".join(make_plugin(mod)._get_site_increment_locked())
    check("📊 3.405" in inc_text and "⬆" in inc_text and "⬇" in inc_text and "🪙 18,619.5" in inc_text,
          "站点增量使用图标展示分享率/上传/下载/魔力")
    _SUB.update({
        "sites": [],
        "site_latest": [
            types.SimpleNamespace(name="回退站", domain="fallback.x", err_msg="", updated_day=_today, upload=42 * 1024 ** 3, download=9 * 1024 ** 3),
        ],
        "site_prev": [
            types.SimpleNamespace(name="回退站", domain="fallback.x", err_msg="", upload=40 * 1024 ** 3, download=8 * 1024 ** 3),
        ],
    })
    active_empty_chart = make_plugin(mod).api_site_stat_chart().get("data", {})
    check(active_empty_chart.get("visible_count") == 1
          and len(active_empty_chart.get("sites") or []) == 1
          and active_empty_chart.get("upload_total") == 2 * 1024 ** 3,
          "list_active 为空时站点统计回退使用最新快照，不能把在线站点过滤成 0")
    _SUB.update({
        "sites": [types.SimpleNamespace(domain="real.x")],
        "site_latest": [
            types.SimpleNamespace(name="同名站", domain="real.x", err_msg="", updated_day=_today, upload=100 * 1024 ** 3, download=50 * 1024 ** 3),
        ],
        "site_prev": [
            types.SimpleNamespace(name="同名站", domain="real.x", err_msg="", upload=80 * 1024 ** 3, download=45 * 1024 ** 3),
            types.SimpleNamespace(name="同名站", domain="other.x", err_msg="", upload=99 * 1024 ** 3, download=49 * 1024 ** 3),
        ],
    })
    same_name_text = "\n".join(make_plugin(mod)._get_site_increment_locked())
    same_name_chart = make_plugin(mod).api_site_stat_chart().get("data", {})
    check("同名站：⬆ 20.00 GB ｜ ⬇ 5.00 GB" in same_name_text,
          "日报站点增量优先按 domain 匹配昨日快照，避免同名站点拿错基准")
    check(same_name_chart.get("upload_total") == 20 * 1024 ** 3 and same_name_chart.get("download_total") == 5 * 1024 ** 3,
          "仪表盘站点增量同样优先按 domain 匹配昨日快照")
    _SUB.update({
        "sites": [types.SimpleNamespace(domain="zero.x")],
        "site_latest": [
            types.SimpleNamespace(name="零基准站", domain="zero.x", err_msg="", updated_day=_today, upload=6 * 1024 ** 4, download=800 * 1024 ** 3),
        ],
        "site_prev": [
            types.SimpleNamespace(name="零基准站", domain="zero.x", err_msg="", upload=0, download=0),
        ],
    })
    zero_base_text = "\n".join(make_plugin(mod)._get_site_increment_locked())
    zero_base_chart = make_plugin(mod).api_site_stat_chart().get("data", {})
    check("零基准站" not in zero_base_text and zero_base_chart.get("upload_total") == 0 and zero_base_chart.get("download_total") == 0,
          "站点增量遇到昨日 0 基准时不把当前累计量误报为每日增量")
    _SUB.update({
        "sites": [types.SimpleNamespace(domain="missing.x")],
        "site_latest": [
            types.SimpleNamespace(name="缺字段站", domain="missing.x", err_msg="", updated_day=_today, upload=7 * 1024 ** 4, download=900 * 1024 ** 3),
        ],
        "site_prev": [
            types.SimpleNamespace(name="缺字段站", domain="missing.x", err_msg=""),
        ],
    })
    missing_base_text = "\n".join(make_plugin(mod)._get_site_increment_locked())
    missing_base_chart = make_plugin(mod).api_site_stat_chart().get("data", {})
    check("缺字段站" not in missing_base_text and missing_base_chart.get("upload_total") == 0 and missing_base_chart.get("download_total") == 0,
          "站点增量遇到昨日累计字段缺失时不把当前累计量误报为每日增量")
    _SUB.update({
        "sites": [types.SimpleNamespace(domain="nobase.x")],
        "site_latest": [
            types.SimpleNamespace(name="无基线站", domain="nobase.x", err_msg="", updated_day=_today, upload=6 * 1024 ** 4, download=800 * 1024 ** 3),
        ],
        "site_prev": [],
    })
    nobase_text = "\n".join(make_plugin(mod)._get_site_increment_locked())
    nobase_chart = make_plugin(mod).api_site_stat_chart().get("data", {})
    check("基线不足" in nobase_text and "6.00 TB" not in nobase_text and "800.00 GB" not in nobase_text,
          "站点增量没有历史基线时明确提示基线不足，绝不展示当前累计上传/下载")
    check(nobase_chart.get("baseline_ready") is False and nobase_chart.get("upload_total") == 0 and nobase_chart.get("download_total") == 0,
          "站点增量图表没有历史基线时标记 baseline_ready=False，合计保持 0")
    _latest_day = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    _prev_day = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    _SUB.update({
        "sites": [types.SimpleNamespace(domain="m.x")],
        "site_latest": [
            types.SimpleNamespace(name="馒头", domain="m.x", err_msg="", updated_day=f"{_latest_day} 23:55:00", upload=120 * 1024 ** 3, download=15 * 1024 ** 3),
        ],
        "site_prev": {
            _prev_day: [types.SimpleNamespace(name="馒头", err_msg="", upload=100 * 1024 ** 3, download=11 * 1024 ** 3)],
        },
    })
    fallback_chart = make_plugin(mod).api_site_stat_chart()
    fallback_data = fallback_chart.get("data", {})
    check(fallback_data.get("date") == _latest_day and fallback_data.get("basis") == "latest",
          "饼图：过零点无今日快照时使用最近有效快照")
    check(fallback_data.get("upload_total") == 20 * 1024 ** 3 and fallback_data.get("download_total") == 4 * 1024 ** 3,
          "饼图：最近快照按其前一有效日期计算增量")
    _stale_day = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    _SUB.update({
        "sites": [types.SimpleNamespace(domain="stale.x")],
        "site_latest": [
            types.SimpleNamespace(name="过期站", domain="stale.x", err_msg="", updated_day=_stale_day, upload=120 * 1024 ** 3, download=15 * 1024 ** 3),
        ],
        "site_prev": {
            (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"): [
                types.SimpleNamespace(name="过期站", domain="stale.x", err_msg="", upload=100 * 1024 ** 3, download=11 * 1024 ** 3)
            ],
        },
    })
    stale_inc_text = "\n".join(make_plugin(mod)._get_site_increment_locked())
    stale_chart = make_plugin(mod).api_site_stat_chart().get("data", {})
    check("站点快照过期" in stale_inc_text and "20.00 GB" not in stale_inc_text,
          "日报站点增量遇到过期快照必须明确提示时效性，不把历史增量当今日增量")
    check(stale_chart.get("basis") == "latest" and stale_chart.get("stale") is True and stale_chart.get("latest_date") == _stale_day,
          "站点统计图使用最近快照时必须显式标记 stale/latest_date，避免用户误判为今日数据")
    _SUB.update({
        "sites": [types.SimpleNamespace(domain="ok.x"), types.SimpleNamespace(domain="old.x")],
        "site_latest": [
            types.SimpleNamespace(name="今日站", domain="ok.x", err_msg="", updated_day=_today, upload=120 * 1024 ** 3, download=15 * 1024 ** 3),
            types.SimpleNamespace(name="旧站", domain="old.x", err_msg="", updated_day=_stale_day, upload=88 * 1024 ** 3, download=1 * 1024 ** 3),
        ],
        "site_prev": [
            types.SimpleNamespace(name="今日站", domain="ok.x", err_msg="", upload=100 * 1024 ** 3, download=11 * 1024 ** 3),
            types.SimpleNamespace(name="旧站", domain="old.x", err_msg="", upload=80 * 1024 ** 3, download=0),
        ],
    })
    mixed_inc_text = "\n".join(make_plugin(mod)._get_site_increment_locked())
    check("今日站：⬆ 20.00 GB ｜ ⬇ 4.00 GB" in mixed_inc_text and "另 1 个站点快照过期" in mixed_inc_text,
          "日报站点增量有部分站点过期时，正常站点照常展示，同时提示未计入的过期站点")
    _SUB.update({
        "sites": [types.SimpleNamespace(domain="bad.x")],
        "site_latest": [
            types.SimpleNamespace(name="坏站", domain="bad.x", err_msg="Cookie 失效", updated_day=_today, upload=120 * 1024 ** 3, download=15 * 1024 ** 3),
        ],
        "site_prev": [],
    })
    bad_chart = make_plugin(mod).api_site_stat_chart().get("data", {})
    check(bad_chart.get("error_count") == 1 and bad_chart.get("data_valid") is False,
          "站点统计图遇到站点抓取错误时必须标记 data_valid=False，而不是静默返回空增量")
    p_site_fail = make_plugin(mod)
    p_site_fail.api_site_stat_chart = lambda: {"code": 1, "msg": "站点接口异常", "data": {"sites": [], "upload_total": 0, "download_total": 0}}
    site_fail = p_site_fail.api_run_site_stat()
    check(site_fail.get("code") == 1 and "站点接口异常" in site_fail.get("msg", ""), "站点统计刷新透传图表接口失败，不误报成功")
    check((p_site_fail.get_data("last_site_stat") or {}).get("success") is False, "站点统计刷新失败时记录失败任务状态")

    print("== 订阅追新：cron 统一 + 独立推送服务 ==")
    p_old = make_plugin(mod, subscribe_reminder_time="9")
    check(p_old._subscribe_reminder_cron == "0 9 * * *", "无 cron 时由小时 9 迁移为 '0 9 * * *'")
    p_cron = make_plugin(mod, subscribe_reminder_cron="30 8 * * *", subscribe_reminder_time="9")
    check(p_cron._subscribe_reminder_cron == "30 8 * * *", "显式 cron 优先于小时")
    p_sr = make_plugin(mod, fusion_notify_enabled=False, enabled=True, subscribe_reminder_enabled=True, subscribe_reminder_cron="0 9 * * *")
    sr_ids = [s.get("id") for s in (p_sr.get_service() or [])]
    check("AgentOpsAssistant.SubscribeReminder" in sr_ids, "启用后注册独立订阅追新定时服务")
    p_sr._get_today_subscribe_updates_locked = lambda: ["凡人修仙传 S01E50"]
    sr_sent = {}
    p_sr.post_message = lambda **kw: sr_sent.update(kw)
    ok_sr = p_sr.run_subscribe_reminder()
    check(ok_sr is True and "凡人修仙传" in str(sr_sent.get("text", "")), "run_subscribe_reminder 推送今日追新并返回 True")
    p_sr_other = make_plugin(mod, fusion_notify_enabled=False, subscribe_reminder_msgtype="其他")
    p_sr_other._get_today_subscribe_updates_locked = lambda: ["凡人修仙传 S01E51"]
    sr_other_sent = {}
    p_sr_other.post_message = lambda **kw: sr_other_sent.update(kw)
    p_sr_other.run_subscribe_reminder()
    check(getattr(sr_other_sent.get("mtype"), "name", "") == "Other", "订阅追新消息类型支持 其他")
    p_off = make_plugin(mod, enabled=True, subscribe_reminder_enabled=False)
    check("AgentOpsAssistant.SubscribeReminder" not in [s.get("id") for s in (p_off.get_service() or [])], "关闭时不注册订阅追新服务")

    print("== 通知类型统一 ==")
    p_market = make_plugin(mod, fusion_notify_enabled=False, market_update_enabled=True, market_update_notify=True, market_update_notify_type="Other")
    p_market._build_market_update_status = lambda apply=False: {"success": True, "has_update": True}
    p_market._auto_update_installed_plugins = lambda apply=True: {}
    p_market._format_market_update_text = lambda data: "market update"
    market_sent = {}
    p_market.post_message = lambda **kw: market_sent.update(kw)
    p_market.run_market_update()
    check(getattr(market_sent.get("mtype"), "name", "") == "Other", "插件库更新通知使用所选消息类型")
    p_market_preview_error = make_plugin(mod, market_update_enabled=True)
    p_market_preview_error._build_market_update_status = lambda apply=False: (_ for _ in ()).throw(RuntimeError("插件库记录页面获取失败：no_response"))
    market_preview_error = p_market_preview_error.api_preview_market_update()
    check(market_preview_error.get("code") == 1 and "no_response" in market_preview_error.get("msg", ""), "插件库更新预览失败时返回可读错误而不是抛异常")
    check(not p_market_preview_error._stub_messages and not p_market_preview_error._stub_data, "插件库更新预览失败不发消息也不写状态")
    p_update_preview_error = make_plugin(mod, mp_update_enabled=True)
    p_update_preview_error._build_update_status = lambda: (_ for _ in ()).throw(RuntimeError("release api timeout"))
    update_preview_error = p_update_preview_error.api_preview_updates()
    check(update_preview_error.get("code") == 1 and "release api timeout" in update_preview_error.get("msg", ""), "MP 更新预览失败时返回可读错误而不是抛异常")
    p_log_preview_error = make_plugin(mod, log_clean_enabled=True)
    p_log_preview_error._build_log_preview = lambda: (_ for _ in ()).throw(RuntimeError("log path denied"))
    log_preview_error = p_log_preview_error.api_preview_log_clean()
    check(log_preview_error.get("code") == 1 and "log path denied" in log_preview_error.get("msg", ""), "日志清理预览失败时返回可读错误而不是抛异常")
    p_plugin_preview_error = make_plugin(mod)
    p_plugin_preview_error._build_plugin_uninstall_status = lambda clean=False: (_ for _ in ()).throw(RuntimeError("plugin list broken"))
    plugin_preview_error = p_plugin_preview_error.api_preview_plugin_uninstall()
    check(plugin_preview_error.get("code") == 1 and "plugin list broken" in plugin_preview_error.get("msg", ""), "插件卸载预览失败时返回可读错误而不是抛异常")
    p_api_task_error = make_plugin(mod, subfill_enabled=True)
    p_api_task_error.run_subfill_clear_history = lambda: (_ for _ in ()).throw(RuntimeError("save_data failed"))
    api_task_error = p_api_task_error.api_subfill_clear_history()
    check(api_task_error.get("code") == 1 and "save_data failed" in api_task_error.get("msg", ""), "通用手动任务异常时返回失败信封而不是硬抛")

    print("== 更新检查：通知去重 ==")
    p_update = make_plugin(mod, fusion_notify_enabled=False, enabled=True, mp_update_enabled=True, mp_update_notify=True, mp_update_notify_type="Other")
    p_update._get_local_versions = lambda: {"backend_version": "v2.13.10", "frontend_version": "v2.13.10"}
    p_update._check_one_release = lambda label, url, local: {
        "type": label,
        "local_version": local,
        "latest_version": "v2.13.10" if label == "后端" else "v2.13.11",
        "has_update": label == "前端",
        "error": "",
    }
    p_update._build_market_status = lambda: {"note": "本插件直接检查插件库记录"}
    mp_update_service = next(s for s in p_update.get_service() if s.get("id") == "AgentOpsAssistant.MPUpdate")
    check(mp_update_service["func"]() is True, "MP 更新定时服务执行成功")
    check(not p_update._stub_messages, "MP 更新检查发现新版时不单独推送 TG，只更新状态供融合卡按钮使用")
    update_task = p_update.get_data("last_update_preview") or {}
    check(update_task.get("success") is True and "有更新" in update_task.get("output", ""),
          "MP 更新检查发现新版时仍记录可读状态")

    p_apply_update = make_plugin(mod, fusion_notify_enabled=False, enabled=True, mp_update_enabled=True, mp_update_notify=True, mp_update_notify_type="Other")
    p_apply_update._get_local_versions = p_update._get_local_versions
    p_apply_update._check_one_release = p_update._check_one_release
    p_apply_update._build_market_status = p_update._build_market_status
    upgrade_calls = []
    p_apply_update._dispatch_moviepilot_upgrade = lambda data: (upgrade_calls.append(data), data.setdefault("moviepilot", {}).update({"upgrade_dispatched": True, "upgrade_message": "queued"}))
    check(p_apply_update.run_mp_update_apply() is True and upgrade_calls, "TG 立即更新动作应触发 MoviePilot 升级")
    apply_titles = [m.get("title") for m in p_apply_update._stub_messages]
    check(apply_titles == ["MP 运维助手 - MoviePilot更新执行"]
          and getattr(p_apply_update._stub_messages[0].get("mtype"), "name", "") == "Other",
          "只有执行 MoviePilot 更新后才发送 TG 推送，并使用所选消息类型")

    p_update_preview = make_plugin(mod, enabled=True, mp_update_enabled=True, mp_update_notify=True)
    p_update_preview._get_local_versions = p_update._get_local_versions
    p_update_preview._check_one_release = p_update._check_one_release
    p_update_preview._build_market_status = p_update._build_market_status
    preview_result = p_update_preview.api_preview_updates()
    check(preview_result.get("code") == 0 and not p_update_preview._stub_messages, "MP 更新预览接口不发送通知")
    p_update_restart_preview = make_plugin(mod, enabled=True, mp_update_enabled=True, mp_update_notify=True, mp_update_restart_confirm=True)
    p_update_restart_preview._get_local_versions = p_update._get_local_versions
    p_update_restart_preview._check_one_release = p_update._check_one_release
    p_update_restart_preview._build_market_status = p_update._build_market_status
    restart_preview_result = p_update_restart_preview.api_preview_updates()
    restart_mp = (restart_preview_result.get("data") or {}).get("moviepilot") or {}
    check("restart_dispatched" not in restart_mp and "restart_error" not in restart_mp, "MP 更新预览接口不触发重启副作用")
    p_update_error = make_plugin(mod, enabled=True, mp_update_enabled=True)
    p_update_error._get_local_versions = lambda: {"backend_version": "v2.13.10", "frontend_version": "v2.13.10"}
    p_update_error._check_one_release = lambda label, url, local: {
        "type": label,
        "local_version": local,
        "latest_version": "",
        "has_update": False,
        "error": "release api timeout",
    }
    p_update_error._build_market_status = p_update._build_market_status
    check(p_update_error.run_mp_update_check() is False, "MP 更新检查 release 查询异常时不误报执行成功")
    update_error_task = p_update_error.get_data("last_update_preview") or {}
    check(update_error_task.get("success") is False, "MP 更新检查异常时记录失败任务状态")
    p_update_error_api = make_plugin(mod, enabled=True, mp_update_enabled=True)
    p_update_error_api._get_local_versions = p_update_error._get_local_versions
    p_update_error_api._check_one_release = p_update_error._check_one_release
    p_update_error_api._build_market_status = p_update._build_market_status
    update_error_api = p_update_error_api.api_run_mp_update()
    check(update_error_api.get("code") == 1, "MP 更新检查 API 遇到 release 异常时返回失败信封")

    print("== 命令入口：通知去重 ==")
    p_cmd_notify = make_plugin(mod, fusion_notify_enabled=False, subscribe_reminder_enabled=True, subscribe_reminder_msgtype="Plugin")
    p_cmd_notify._get_today_subscribe_updates_locked = lambda: ["凡人修仙传 S01E52"]
    p_cmd_notify.handle_command(types.SimpleNamespace(event_data={"action": "mpops_subscribe"}))
    cmd_titles = [m.get("title") for m in p_cmd_notify._stub_messages]
    check(cmd_titles == ["MP 运维助手 - 订阅追新"], "命令触发的任务已发送业务通知时，不再补发命令执行结果")

    p_cmd_feedback = make_plugin(mod, fusion_notify_enabled=False, health_check_enabled=True)
    p_cmd_feedback._build_health_summary = lambda: {
        "success": True,
        "checks": [{"name": "database", "ok": True, "detail": "连接正常"}],
        "total": 1,
        "pass": 1,
        "fail": 0,
    }
    p_cmd_feedback.handle_command(types.SimpleNamespace(event_data={"action": "mpops_health"}))
    feedback_titles = [m.get("title") for m in p_cmd_feedback._stub_messages]
    check(feedback_titles == ["MP 运维助手命令执行结果"], "命令触发的任务未发送业务通知时，仍保留命令反馈")

    p_cmd_update_quiet = make_plugin(mod, fusion_notify_enabled=False, mp_update_enabled=True)
    p_cmd_update_quiet.run_mp_update_check = lambda: True
    p_cmd_update_quiet.handle_command(types.SimpleNamespace(event_data={"action": "mpops_updates"}))
    check(not p_cmd_update_quiet._stub_messages, "更新检查命令成功时不补发 TG/命令结果通知")

    p_cmd_failure = make_plugin(mod, fusion_notify_enabled=False)
    p_cmd_failure.run_daily_report = lambda: p_cmd_failure.post_message(mtype=mod.NotificationType.Plugin, title="业务通知", text="日报已发送") or True
    p_cmd_failure.run_health_check = lambda: False
    p_cmd_failure.handle_command(types.SimpleNamespace(event_data={"action": "mpops_run_all"}))
    failure_titles = [m.get("title") for m in p_cmd_failure._stub_messages]
    check(failure_titles == ["业务通知", "MP 运维助手命令执行结果"] and "健康巡查：失败" in p_cmd_failure._stub_messages[-1].get("text", ""),
          "组合命令已有业务通知但存在失败任务时，仍补发失败汇总")

    p_cmd_uninstall = make_plugin(mod, fusion_notify_enabled=False, plugin_uninstall_ids=["AutoBackup"])
    uninstall_command_calls = []
    p_cmd_uninstall.run_plugin_uninstall_clean = lambda: uninstall_command_calls.append("clean") or True
    p_cmd_uninstall.handle_command(types.SimpleNamespace(event_data={"action": "mpops_plugin_clean"}))
    uninstall_command_text = "\n".join(str(m.get("text", "")) for m in p_cmd_uninstall._stub_messages)
    check(not uninstall_command_calls and "配置页" in uninstall_command_text and "确认" in uninstall_command_text,
          "远程插件卸载命令不能绕过配置页显式确认直接执行")

    print("== onlyonce 保存后立即运行一次（修复死开关）==")
    p_once = make_plugin(mod, enabled=True, backup_enabled=True, log_clean_enabled=True,
                         market_update_enabled=True, subscribe_reminder_enabled=True, site_stat_enabled=True)
    once_calls = []
    p_once.run_backup = lambda: once_calls.append("backup") or True
    p_once.run_log_clean = lambda: once_calls.append("log") or True
    p_once.run_market_update = lambda: once_calls.append("market") or True
    p_once.run_subscribe_reminder = lambda: once_calls.append("sub") or True
    p_once.api_run_site_stat = lambda: once_calls.append("site") or {"code": 0}
    cfg_once = {
        "backup_onlyonce": True,
        "log_clean_onlyonce": True,
        "market_update_onlyonce": True,
        "subscribe_reminder_onlyonce": True,
        "site_stat_onlyonce": True,
    }
    fired = p_once._fire_onlyonce(cfg_once)
    expected_once_keys = {"backup_onlyonce", "log_clean_onlyonce", "market_update_onlyonce", "subscribe_reminder_onlyonce", "site_stat_onlyonce"}
    expected_once_calls = {"backup", "log", "market", "sub", "site"}
    deadline = time.monotonic() + 3
    while set(once_calls) != expected_once_calls and time.monotonic() < deadline:
        time.sleep(0.05)
    check(set(fired) == expected_once_keys, "onlyonce 命中置位的全部开关")
    check(all(cfg_once[key] is False for key in expected_once_keys), "onlyonce 命中后清零（防重载重复触发）")
    check(set(once_calls) == expected_once_calls, "onlyonce 全部映射到实际任务")
    check(p_once._fire_onlyonce({}) == [], "无 onlyonce 置位 -> 不触发")

    print("== 总开关 / 组件开关关闭态守卫 ==")
    p_disabled = make_plugin(mod, enabled=False, backup_enabled=True, market_update_enabled=True,
                             health_check_enabled=True, seedclean_enabled=True, seedclean_downloaders=["qb1"])
    disabled_calls = []
    p_disabled.run_backup = lambda: disabled_calls.append("backup") or True
    cfg_disabled_once = {"backup_onlyonce": True}
    fired_disabled = p_disabled._fire_onlyonce(cfg_disabled_once)
    check(fired_disabled == [] and cfg_disabled_once["backup_onlyonce"] is False and disabled_calls == [],
          "总开关关闭时 onlyonce 只复位不执行业务")
    p_disabled._create_agentops_backup = lambda: (_ for _ in ()).throw(RuntimeError("backup should not run"))
    disabled_backup = p_disabled.api_run_backup()
    check(disabled_backup.get("code") == 1 and "插件未启用" in disabled_backup.get("msg", ""),
          "总开关关闭时手动备份 API 跳过业务链路")
    check((disabled_backup.get("data") or {}).get("code") == 1
          and "插件未启用" in (disabled_backup.get("data") or {}).get("msg", ""),
          "总开关关闭时备份跳过响应在 data 内也保留失败信封，防止前端解包后误报成功")
    p_disabled._site_increment_snapshot = lambda: (_ for _ in ()).throw(RuntimeError("site should not run"))
    disabled_site = p_disabled.api_run_site_stat()
    disabled_market = p_disabled.api_run_market_update()
    check((disabled_site.get("data") or {}).get("code") == 1
          and (disabled_market.get("data") or {}).get("code") == 1
          and (disabled_site.get("data") or {}).get("skipped") is True
          and (disabled_market.get("data") or {}).get("skipped") is True,
          "总开关关闭时带 data 的手动动作跳过响应都保留失败信封，防止旧前端误报完成")
    disabled_restore_calls = []
    p_disabled._list_backup_archives = lambda: disabled_restore_calls.append("list") or []
    p_disabled._build_backup_restore_preview = lambda payload: disabled_restore_calls.append("preview") or {}
    p_disabled._run_backup_restore = lambda payload: disabled_restore_calls.append("run") or {"success": True}
    disabled_archives = p_disabled.api_backup_archives()
    disabled_restore_preview = p_disabled.api_preview_backup_restore({"archive": "bk_20260621010101.zip"})
    disabled_restore_run = p_disabled.api_run_backup_restore({"archive": "bk_20260621010101.zip"})
    check(disabled_restore_calls == []
          and disabled_archives.get("code") == 1
          and disabled_restore_preview.get("code") == 1
          and disabled_restore_run.get("code") == 1
          and "插件未启用" in disabled_restore_run.get("msg", ""),
          "总开关关闭时备份恢复 API 跳过业务链路")
    p_disabled._build_health_summary = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("health should not run"))
    disabled_health = p_disabled.api_run_health_check()
    check(disabled_health.get("code") == 1 and "插件未启用" in disabled_health.get("msg", ""),
          "总开关关闭时健康巡查 API 跳过业务链路")
    p_disabled.save_data("last_daily_report", {"success": False, "returncode": 2, "output": "插件未启用，已跳过每日汇报。", "time": "2026-06-21 13:26:01"})
    disabled_dashboard = p_disabled.api_dashboard().get("data", {})
    check(disabled_dashboard.get("task_on") == 0 and disabled_dashboard.get("task_failed") == 0,
          "总开关关闭时仪表盘不把单组件配置开关或历史跳过结果算作当前启用/异常")
    p_disabled._build_daily_report_message = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("daily preview should not run"))
    disabled_preview = p_disabled.api_preview_daily_report()
    check(disabled_preview.get("code") == 1,
          "plugin-off daily preview skips live build")
    disabled_preview_calls = []
    p_disabled._build_log_preview = lambda: disabled_preview_calls.append("log") or (_ for _ in ()).throw(RuntimeError("log preview should not run"))
    p_disabled._build_plugin_uninstall_status = lambda **kwargs: disabled_preview_calls.append("uninstall") or (_ for _ in ()).throw(RuntimeError("plugin uninstall preview should not run"))
    disabled_log_preview = p_disabled.api_preview_log_clean()
    disabled_uninstall_preview = p_disabled.api_preview_plugin_uninstall()
    check(disabled_preview_calls == []
          and disabled_log_preview.get("code") == 1
          and disabled_uninstall_preview.get("code") == 1
          and "插件未启用" in disabled_log_preview.get("msg", "")
          and "插件未启用" in disabled_uninstall_preview.get("msg", ""),
          "总开关关闭时日志清理/插件卸载预览不触发业务扫描")
    p_disabled._fusion_notify_enabled = False
    p_disabled._tg_console_enabled = False
    p_disabled._tg_console_suppress_individual_notifications = False
    p_disabled.handle_command(types.SimpleNamespace(event_data={"action": "mpops_backup"}))
    check(any("插件未启用" in (m.get("text", "") + m.get("title", "")) for m in p_disabled._stub_messages),
          "总开关关闭时远程命令只提示跳过")

    p_components_off = make_plugin(mod, enabled=True, backup_enabled=False, market_update_enabled=False,
                                   daily_report_enabled=False, health_check_enabled=False, site_stat_enabled=False,
                                   subscribe_reminder_enabled=False, seedclean_enabled=False,
                                   dltag_enabled=False, seedclean_downloaders=["qb1"], dltag_downloaders=["qb1"])
    p_components_off._create_agentops_backup = lambda: (_ for _ in ()).throw(RuntimeError("backup should not run"))
    check("自动备份未启用" in p_components_off.api_run_backup().get("msg", ""),
          "备份组件关闭时手动备份 API 跳过")
    component_restore_calls = []
    p_components_off._list_backup_archives = lambda: component_restore_calls.append("list") or []
    p_components_off._build_backup_restore_preview = lambda payload: component_restore_calls.append("preview") or {}
    p_components_off._run_backup_restore = lambda payload: component_restore_calls.append("run") or {"success": True}
    component_archives = p_components_off.api_backup_archives()
    component_restore_preview = p_components_off.api_preview_backup_restore({"archive": "bk_20260621010101.zip"})
    component_restore_run = p_components_off.api_run_backup_restore({"archive": "bk_20260621010101.zip"})
    check(component_restore_calls == []
          and component_archives.get("code") == 1
          and component_restore_preview.get("code") == 1
          and component_restore_run.get("code") == 1
          and "备份恢复未启用" in component_restore_run.get("msg", ""),
          "备份组件关闭时备份恢复 API 跳过")
    p_components_off._build_market_update_status = lambda apply=False: (_ for _ in ()).throw(RuntimeError("market should not run"))
    check("插件库更新未启用" in p_components_off.api_run_market_update().get("msg", ""),
          "插件库更新组件关闭时手动 API 跳过")
    p_components_off._build_health_summary = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("health should not run"))
    check("健康巡查未启用" in p_components_off.api_run_health_check().get("msg", ""),
          "健康巡查组件关闭时手动 API 跳过")
    p_components_off._build_daily_report_message = lambda *a, **k: "daily preview ok"
    check(p_components_off.api_preview_daily_report().get("code") == 0,
          "manual daily preview remains available when the schedule switch is off")
    p_components_off._build_update_status = lambda: (_ for _ in ()).throw(RuntimeError("update should not run"))
    check("主程序更新检查未启用" in p_components_off.api_preview_updates().get("msg", ""),
          "主程序更新组件关闭时预览 API 跳过")
    p_components_off._build_market_update_status = lambda apply=False: (_ for _ in ()).throw(RuntimeError("market preview should not run"))
    check("插件库更新未启用" in p_components_off.api_preview_market_update().get("msg", ""),
          "插件库更新组件关闭时预览 API 跳过")
    p_components_off._build_log_preview = lambda: (_ for _ in ()).throw(RuntimeError("log preview should not run"))
    check("日志清理未启用" in p_components_off.api_preview_log_clean().get("msg", ""),
          "日志清理组件关闭时预览 API 跳过")
    p_components_off._site_increment_snapshot = lambda: (_ for _ in ()).throw(RuntimeError("site should not run"))
    site_skip = p_components_off.api_site_stat_chart()
    check(site_skip.get("code") == 0 and "未启用" in site_skip.get("msg", "") and not site_skip.get("data", {}).get("sites"),
          "站点统计组件关闭时图表接口不采集站点数据")
    p_components_off._seed_clean_run = lambda: (_ for _ in ()).throw(RuntimeError("seed should not run"))
    check("自动删种未启用" in p_components_off.api_run_seed_clean().get("msg", ""),
          "自动删种组件关闭时手动 API 跳过")
    p_components_off._downloader_overview_data = lambda: (_ for _ in ()).throw(RuntimeError("downloader should not run"))
    downloader_skip = p_components_off.api_downloader_overview()
    check(downloader_skip.get("code") == 1
          and downloader_skip.get("data", {}).get("downloaders") == []
          and downloader_skip.get("data", {}).get("skipped") is True
          and "下载器活动未启用" in downloader_skip.get("msg", ""),
          "种子打标签组件关闭时下载器活动概览不访问下载器链路")
    check("种子打标签未启用" in p_components_off.api_run_downloader_tag().get("msg", ""),
          "种子打标签组件关闭时手动 API 跳过")

    print("== 发版自检：接口/服务/命令/生命周期完整性 ==")
    pa = make_plugin(mod, enabled=True, seedclean_enabled=True, seedclean_downloaders=["qb1"], seedclean_cron="0 1 * * *",
                     backup_enabled=True, daily_report_enabled=True, log_clean_enabled=True,
                     mp_update_enabled=True, market_update_enabled=True)
    apis = pa.get_api() or []
    check(len(apis) > 0 and all(callable(a.get("endpoint")) for a in apis), f"get_api 全部 endpoint 可调用（{len(apis)} 个）")
    check(len({a.get("path") for a in apis}) == len(apis), "get_api path 无重复")
    api_paths = {str(a.get("path") or "").lstrip("/") for a in apis}
    frontend_api_calls = {
        "dashboard", "site_stat_chart", "downloader_overview",
        "create_tg_console_card", "run_daily_report", "run_subscribe_reminder", "run_site_stat",
        "run_today_transfer", "run_downloader_tag", "run_backup", "run_log_clean", "run_mp_update",
        "run_market_update", "run_health_check", "run_seed_clean",
        "preview_updates",
        "installed_plugins", "plugin_markets", "downloaders", "mediaservers",
        "subfill_clear_history", "subfill_clear_handled", "run_plugin_uninstall",
    }
    check(frontend_api_calls <= api_paths, "前端调用的插件 API 均已在 get_api 注册")
    pr_health = make_plugin(mod, report_health=True)
    pr_health._get_site_increment_locked = lambda: []
    pr_health._get_site_health_locked = lambda: []
    pr_health._get_transfer_health_locked = lambda: []
    pr_health._get_today_subscribe_updates_locked = lambda: []
    pr_health._get_downloader_health_locked = lambda: []
    pr_health._get_storage_health_locked = lambda: []
    pr_health._get_today_downloads_locked = lambda: []
    pr_health._get_media_stats_locked = lambda: []
    pr_health.save_data("last_health_check", {"time": "2026-06-18 08:00:00", "success": True, "output": "⦁ 状态：全部正常"})
    msg_health = pr_health._build_heartbeat_message()
    check("🩺 健康巡查" in msg_health and "状态：全部正常" in msg_health, "report_health=True -> 日报包含健康巡查结果")

    print("== 健康巡查范围与兜底 ==")
    hc_service = make_plugin(mod, fusion_notify_enabled=False, enabled=True, health_check_enabled=True, health_check_cron="0 */6 * * *")
    hc_service_ids = {s.get("id") for s in (hc_service.get_service() or [])}
    check("AgentOpsAssistant.HealthCheck" in hc_service_ids, "启用健康巡查后注册独立定时服务")
    task_keys = {t.get("key") for t in hc_service._task_definitions()}
    check("health_check" in task_keys, "组件运行状况包含健康巡查")
    check("site_stat" in task_keys, "组件运行状况包含站点数据统计")
    check("downloader_tag" in task_keys, "组件运行状况包含种子标签")
    hc_service_off = make_plugin(mod, enabled=True, health_check_enabled=False)
    hc_service_off_ids = {s.get("id") for s in (hc_service_off.get_service() or [])}
    check("AgentOpsAssistant.HealthCheck" not in hc_service_off_ids, "关闭健康巡查后不注册定时服务")
    bad_cron = make_plugin(mod, enabled=True, daily_report_enabled=True, daily_report_cron="bad cron",
                           health_check_enabled=True, health_check_cron="bad cron",
                           seedclean_enabled=True, seedclean_downloaders=["qb1"], seedclean_cron="bad cron")
    try:
        bad_cron_ids = {s.get("id") for s in (bad_cron.get_service() or [])}
        bad_cron_raised = False
    except Exception:
        bad_cron_ids = set()
        bad_cron_raised = True
    check(not bad_cron_raised and "AgentOpsAssistant.DailyReport" not in bad_cron_ids
          and "AgentOpsAssistant.HealthCheck" not in bad_cron_ids
          and "AgentOpsAssistant.SeedClean" not in bad_cron_ids,
          "cron 配置错误时跳过对应定时服务，不拖垮插件调度加载")

    hc_all = make_plugin(mod, health_check_items=[])
    hc_all._check_database = lambda: {"name": "database", "ok": True, "detail": "db"}
    hc_all._check_storage = lambda: {"name": "storage", "ok": True, "detail": "storage"}
    hc_all._check_directory = lambda: {"name": "directory", "ok": True, "detail": "dir"}
    all_summary = hc_all._build_health_summary()
    all_names = {item.get("name") for item in all_summary.get("checks", [])}
    check({"database", "storage", "directory"} <= all_names, "health_check_items 为空时等价检查全部可选项")

    hc_run = make_plugin(mod)
    hc_run._build_health_summary = lambda: {
        "success": False,
        "checks": [{"name": "storage", "ok": False, "detail": "容量超过阈值"}],
        "total": 1,
        "pass": 0,
        "fail": 1,
    }
    check(hc_run.run_health_check() is True, "健康巡查发现异常时接口仍表示巡查任务已完成")
    check((hc_run.get_data("last_health_check") or {}).get("success") is False, "健康巡查异常状态仍保存在健康结果中")
    hc_dashboard = make_plugin(mod)
    long_health_output = "⦁ 状态：发现 2 项异常\n" + ("⦁ 存储空间：/downloads/library/very/long/path 已用 93%，超过阈值 85%\n" * 12) + "⦁ 目录权限：/config/plugins/AgentOpsAssistant/Backup 无写入权限"
    hc_dashboard.save_data("last_health_check", {"time": "2026-06-18 20:00:00", "success": False, "output": long_health_output})
    hc_dashboard_data = (hc_dashboard.api_dashboard().get("data") or {}).get("health") or {}
    check(hc_dashboard_data.get("output") == long_health_output, "仪表盘健康巡查异常详情不截断")
    hc_api = make_plugin(mod)
    hc_api._build_health_summary = lambda: {
        "success": False,
        "checks": [{"name": "storage", "ok": False, "detail": "容量超过阈值"}],
        "total": 1,
        "pass": 0,
        "fail": 1,
    }
    api_result = hc_api.api_run_health_check()
    check(api_result.get("code") == 0 and "异常" in api_result.get("msg", ""), "健康巡查 API 完成但发现异常时返回可读提示")

    hc_notify = make_plugin(mod, fusion_notify_enabled=False, health_check_notify_type="Other")
    hc_notify._build_health_summary = lambda: {
        "success": False,
        "checks": [
            {"name": "storage", "ok": False, "detail": "下载目录 不存在 /downloads"},
            {"name": "directory", "ok": False, "detail": "媒体库目录 权限不足 /media"},
            {"name": "database", "ok": True, "detail": "连接正常"},
        ],
        "total": 3,
        "pass": 1,
        "fail": 2,
    }
    hc_notify.run_health_check()
    notify_msg = hc_notify._stub_messages[-1] if hc_notify._stub_messages else {}
    check(notify_msg.get("mtype") == mod.NotificationType.Other, "健康巡查发现异常时按配置消息类型主动通知")
    check("发现 2 项异常" in notify_msg.get("title", "") and "存储空间：下载目录 不存在 /downloads" in notify_msg.get("text", "") and "目录权限：媒体库目录 权限不足 /media" in notify_msg.get("text", ""), "健康巡查异常通知列出具体异常项")

    hc_notify_ok = make_plugin(mod)
    hc_notify_ok._build_health_summary = lambda: {
        "success": True,
        "checks": [{"name": "database", "ok": True, "detail": "连接正常"}],
        "total": 1,
        "pass": 1,
        "fail": 0,
    }
    hc_notify_ok.run_health_check()
    check(not hc_notify_ok._stub_messages, "健康巡查全部正常时不主动发送异常通知")

    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_settings = sys.modules["app.core.config"].settings
        cfg_settings.CONFIG_PATH = tmpdir
        if hasattr(cfg_settings, "config_path"):
            delattr(cfg_settings, "config_path")
        hc_dir = make_plugin(mod, health_check_directory_targets=["config"])
        dir_result = hc_dir._check_directory()
        check(dir_result["ok"] is True and "目录" in dir_result["detail"], "目录权限使用 CONFIG_PATH 且不会因 os.W_X 报错")

    sqlalchemy_mod = types.ModuleType("sqlalchemy")
    class _FakeConn:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def execute(self, *a, **k): return 1
    class _FakeEngine:
        def connect(self): return _FakeConn()
    sqlalchemy_mod.create_engine = lambda *a, **k: _FakeEngine()
    sqlalchemy_mod.text = lambda sql: sql
    sys.modules["sqlalchemy"] = sqlalchemy_mod
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_settings = sys.modules["app.core.config"].settings
        cfg_settings.CONFIG_PATH = tmpdir
        cfg_settings.DB_TYPE = "sqlite"
        hc_db = make_plugin(mod)
        db_result = hc_db._check_database()
        check(db_result["ok"] is True and "SQLite" in db_result["detail"] and "user.db" in db_result["detail"], "数据库巡查说明实际检查的 SQLite 主库")

    import shutil as _real_shutil
    original_disk_usage = _real_shutil.disk_usage
    try:
        cfg_settings = sys.modules["app.core.config"].settings
        cfg_settings.CONFIG_PATH = str(ROOT)
        cfg_settings.config_path = str(ROOT)
        _real_shutil.disk_usage = lambda path: types.SimpleNamespace(
            total=100 * 1024 ** 3,
            used=90 * 1024 ** 3,
            free=10 * 1024 ** 3,
        )
        hc_storage = make_plugin(mod, health_check_storage_threshold=85)
        storage_result = hc_storage._check_storage()
        check(storage_result["ok"] is False and "90%" in storage_result["detail"], "存储巡查按已用阈值识别高风险")
    finally:
        _real_shutil.disk_usage = original_disk_usage

    original_directory_helper = sys.modules["app.helper.directory"].DirectoryHelper
    original_disk_usage = _real_shutil.disk_usage
    try:
        class _MixedStorageDirectoryHelper:
            def get_download_dirs(self):
                return [
                    types.SimpleNamespace(download_path=str(ROOT), storage="local"),
                    types.SimpleNamespace(download_path="/115open/待整理", storage="CloudDrive储存"),
                ]
            def get_library_dirs(self):
                return [
                    types.SimpleNamespace(library_path="/115open/NAS/影视库/", library_storage="CloudDrive储存"),
                    types.SimpleNamespace(library_path=str(ROOT), library_storage="local"),
                ]

        sys.modules["app.helper.directory"].DirectoryHelper = _MixedStorageDirectoryHelper

        def _mixed_disk_usage(path):
            if str(path).startswith("/115open"):
                raise FileNotFoundError(path)
            return types.SimpleNamespace(total=100 * 1024 ** 3, used=20 * 1024 ** 3, free=80 * 1024 ** 3)

        _real_shutil.disk_usage = _mixed_disk_usage
        hc_cloud = make_plugin(mod, health_check_storage_targets=["download", "library"], health_check_directory_targets=["download", "library"])
        cloud_storage = hc_cloud._check_storage()
        cloud_directory = hc_cloud._check_directory()
        check(cloud_storage["ok"] is True and "/115open/待整理" not in cloud_storage["detail"], "非本地下载/媒体库目录不按本地磁盘容量判定异常")
        check(cloud_directory["ok"] is True and "/115open/待整理" not in cloud_directory["detail"], "非本地下载/媒体库目录不按本地权限判定异常")
    finally:
        sys.modules["app.helper.directory"].DirectoryHelper = original_directory_helper
        _real_shutil.disk_usage = original_disk_usage

    svcs = pa.get_service() or []
    check(all(callable(s.get("func")) for s in svcs), f"get_service 全部 func 可调用（{len(svcs)} 个）")
    cmds = mod.AgentOpsAssistant.get_command() or []
    check(isinstance(cmds, list) and all(c.get("data", {}).get("action") for c in cmds), "get_command 结构完整")
    check(pa.get_render_mode()[0] == "vue", "渲染模式 = vue")
    form_schema, form_default = pa.get_form()
    check(form_schema == [] and isinstance(form_default, dict) and form_default, "get_form Vue 模式返回 ([], 默认配置dict)")
    multiselect_defaults = ["log_clean_selected_ids", "market_update_blacklist", "market_update_install_ids",
                            "market_update_exclude_ids", "plugin_uninstall_ids", "seedclean_downloaders",
                            "subfill_details", "msgnotify_types", "msgnotify_servers", "dltag_downloaders"]
    check(all(isinstance(form_default.get(key), list) for key in multiselect_defaults),
          "get_form 多选字段默认值保持数组类型")
    check(form_default.get("sidebar_nav_enabled") is True, "get_form 默认开启侧边栏入口")
    check(pa.get_page() == [], "get_page Vue 模式返回 []")
    has_sidebar_nav = hasattr(pa, "get_sidebar_nav")
    check(has_sidebar_nav, "get_sidebar_nav 注册 MP 主界面左侧仪表盘入口")
    if has_sidebar_nav:
        sidebar_nav = pa.get_sidebar_nav() or []
        check(sidebar_nav == [{
            "nav_key": "main",
            "title": "MP 运维助手",
            "icon": "mdi-view-dashboard-outline",
            "section": "start",
            "permission": "manage",
            "order": 50,
        }], "启用时 get_sidebar_nav 返回主导航顶部入口")
        sidebar_switch_off = make_plugin(mod, enabled=True, sidebar_nav_enabled=False).get_sidebar_nav()
        check(sidebar_switch_off == [], "侧边栏入口开关关闭时 get_sidebar_nav 不注册主界面入口")
        sidebar_off = make_plugin(mod, enabled=False).get_sidebar_nav()
        check(sidebar_off == [], "未启用时 get_sidebar_nav 不注册主界面入口")

    print("== MP dashboard integration ==")
    dashboard_default = make_plugin(mod, enabled=True)
    has_dashboard_meta = hasattr(dashboard_default, "get_dashboard_meta")
    has_dashboard = hasattr(dashboard_default, "get_dashboard")
    check(has_dashboard_meta, "plugin exposes get_dashboard_meta")
    check(has_dashboard, "plugin exposes get_dashboard")
    if has_dashboard_meta and has_dashboard:
        default_meta = dashboard_default.get_dashboard_meta()
        check([item.get("key") for item in default_meta] == ["site", "actions"],
              "enabled plugin publishes MP dashboard widgets without an extra plugin switch")
        dashboard_off = make_plugin(mod, enabled=False, mp_dashboard_enabled=True)
        check(dashboard_off.get_dashboard_meta() == [], "disabled plugin does not publish MP dashboard widgets")
        dashboard_on = dashboard_default
        dashboard_meta = dashboard_on.get_dashboard_meta()
        check([item.get("key") for item in dashboard_meta] == ["site", "actions"],
              "MP dashboard publishes only site statistics and manual actions")
        check(all(item.get("name") for item in dashboard_meta), "MP dashboard widget meta contains display names")
        site_dashboard = dashboard_on.get_dashboard(key="site")
        check(isinstance(site_dashboard, tuple) and len(site_dashboard) == 3,
              "get_dashboard returns the MoviePilot dashboard tuple")
        if isinstance(site_dashboard, tuple) and len(site_dashboard) == 3:
            cols, attrs, elements = site_dashboard
            check(cols.get("cols") == 12 and cols.get("md") == 8, "site widget returns wide MP column sizing")
            check(attrs.get("component") == "site" and attrs.get("rows"), "site widget attrs identify the migrated component")
            check(elements == [], "vue dashboard widget renders through exposed Dashboard component")
        actions_dashboard = dashboard_on.get_dashboard(key="actions")
        if isinstance(actions_dashboard, tuple) and len(actions_dashboard) == 3:
            _, action_attrs, _ = actions_dashboard
            check(action_attrs.get("component") == "actions", "manual actions widget is exposed separately")
            components = action_attrs.get("components") or {}
            check(components.get("site_stat") is True
                  and components.get("daily_report") is True
                  and components.get("subscribe_reminder") is True
                  and components.get("health_check") is True,
                  "manual actions widget attrs expose current component enabled states")
        else:
            check(False, "manual actions widget is exposed separately")
        dashboard_actions_off = make_plugin(mod, enabled=True, daily_report_enabled=False,
                                            subscribe_reminder_enabled=False, site_stat_enabled=False,
                                            health_check_enabled=False)
        actions_off = dashboard_actions_off.get_dashboard(key="actions")
        if isinstance(actions_off, tuple) and len(actions_off) == 3:
            _, action_off_attrs, _ = actions_off
            components = action_off_attrs.get("components") or {}
            check(components.get("site_stat") is False
                  and components.get("daily_report") is False
                  and components.get("subscribe_reminder") is False
                  and components.get("health_check") is False,
                  "manual actions widget attrs reflect disabled components so frontend can disable buttons")
        else:
            check(False, "manual actions widget remains available but receives disabled component states")
        check(dashboard_on.get_dashboard(key="status") is None, "status widget is not published to MP dashboard")
        check(dashboard_on.get_dashboard(key="runtime") is None, "runtime widget is not published to MP dashboard")
        check(dashboard_on.get_dashboard(key="unknown") is None, "unknown dashboard widget key is ignored")

    print()
    if _FAILS:
        print(f"FAILED: {len(_FAILS)} 项")
        for m in _FAILS:
            print(f"  - {m}")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
