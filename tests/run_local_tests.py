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
import sys
import tempfile
import time
import types
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
        "site_refresh_calls": 0, "site_refresh_result": {}, "site_refresh_error": None}


class _StubDownloadHistoryOper:
    def get_by_hash(self, h): return _SUB["history"]


class _StubSubscribeOper:
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
        PluginAction="PluginAction", WebhookMessage="WebhookMessage",
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
    check(ok is True and len(items) == 1 and "💽 60 B/100 B" in items[0] and "🟢 已用 60%" in items[0], "存储输出已用/总量与已用百分比")
    check("剩余" not in items[0], "存储输出不重复展示剩余空间")
    items2 = []
    ok2 = p._append_usage_line(items2, "空盘", 0, None, 0)  # total<=0 -> skip
    check(ok2 is False and items2 == [], "total<=0 跳过（不输出“已配置”噪声）")

    print("== 删种条件守卫 ==")
    check(p._seedclean_has_any_condition() is False, "无条件时 has_any_condition=False")
    p._seedclean_size = "1-10"
    check(p._seedclean_has_any_condition() is True, "设了大小后=True")
    p._seedclean_size = ""

    g = make_plugin(mod, seedclean_downloaders=[])
    check(g.run_seed_clean() is False, "无下载器 -> 不执行返回 False")
    check(g._stub_messages and "选择下载器" in g._stub_messages[-1].get("text", ""), "无下载器时按通知配置提醒用户")
    g2 = make_plugin(mod, seedclean_downloaders=["qb1"])  # 无任何条件
    check(g2.run_seed_clean() is False, "有下载器但无条件 -> 跳过返回 False")

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

    p = make_plugin(mod, seedclean_downloaders=["qb1"], seedclean_size="1-10", seedclean_action="pause")
    res = p.run_seed_clean()
    check(res is True, "pause 动作执行成功返回 True")
    check(inst.stopped == ["h1"], "命中种子被暂停（stop_torrents 收到 h1）")
    check(inst.deleted == [] and inst.deleted_with_files == [], "暂停动作未调用删除")

    inst2 = FakeDownloaderInstance([fake_qb_torrent(hash="h2", size=int(5 * 1024 ** 3))])
    service.instance = inst2
    p2 = make_plugin(mod, seedclean_downloaders=["qb1"], seedclean_size="1-10", seedclean_action="delete")
    p2.run_seed_clean()
    check(inst2.deleted == ["h2"], "delete 动作调用 delete_torrents(delete_file=False)")

    inst3 = FakeDownloaderInstance([fake_qb_torrent(hash="h3", size=int(0.1 * 1024 ** 3))])  # 太小，不命中
    service.instance = inst3
    p3 = make_plugin(mod, seedclean_downloaders=["qb1"], seedclean_size="1-10", seedclean_action="delete")
    p3.run_seed_clean()
    check(inst3.deleted == [] and inst3.stopped == [], "不命中的种子不被处理（无误删）")

    print("== 下载器助手：按站点批量打标签（幂等）==")
    tinst = FakeDownloaderInstance([
        fake_qb_torrent(hash="ta", tags=""),
        fake_qb_torrent(hash="tb", tags="https://tracker.example.com/announce"),
    ])
    service.instance = tinst
    make_plugin(mod, dltag_downloaders=["qb1"]).run_downloader_tag()
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

    print("== 插件卸载（多选 ID 与卸载流程回归）==")
    r1 = make_plugin(mod, plugin_uninstall_ids=["AutoBackup"])._build_plugin_uninstall_status(clean=False)
    check(r1.get("plugin_id") == "AutoBackup" and not r1.get("blocked") and r1.get("success") is True,
          "多选列表被识别（不再因单 ID 为空而 blocked）")
    r2 = make_plugin(mod, plugin_uninstall_ids=[])._build_plugin_uninstall_status(clean=False)
    check(bool(r2.get("blocked")) and r2.get("success") is False, "空目标 -> blocked，不误删")
    api_uninstall_empty = make_plugin(mod, plugin_uninstall_ids=[]).api_preview_plugin_uninstall()
    check(api_uninstall_empty.get("code") == 1 and "选择目标插件" in api_uninstall_empty.get("msg", ""),
          "插件卸载预览无目标时提示用户先选择插件")
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
        p_uninstall_guard._plugin_uninstall_candidates = lambda pid: [{
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
    _SUB.update({"history": types.SimpleNamespace(type="电影", tmdbid=5, seasons=""), "subs": [], "updates": []})
    make_plugin(mod, subfill_enabled=True, subfill_details="分辨率").on_download_fill_subscribe(ev)
    check(not _SUB["updates"], "非电视剧下载 -> 不填充")

    print("== 媒体库服务器通知 ==")
    check(AOA._msg_group_of("playback.start") == "开始播放", "事件归类 playback.start->开始播放")
    check(AOA._msg_group_of("ItemAdded") == "新入库", "ItemAdded->新入库")
    check(AOA._msg_group_of("unknown.x") is None, "未知事件 -> None")
    info = types.SimpleNamespace(event="playback.start", item_type="TV", item_name="剧A", user_name="张三",
                                 device_name="客厅", client="Emby", ip=None, percentage=None, overview=None,
                                 item_id="i1", server_name="Emby1", channel="emby", image_url=None)
    pm = make_plugin(mod, msgnotify_enabled=True, msgnotify_types="开始播放,新入库")
    pm.on_webhook_message(types.SimpleNamespace(event_data=info))
    check(len(pm._stub_messages) == 1 and "开始播放剧集 剧A" in pm._stub_messages[0]["title"], "开始播放 -> 发通知，标题正确")
    check("用户：张三" in pm._stub_messages[0]["text"], "正文含用户")
    check(getattr(pm._stub_messages[0].get("mtype"), "name", "") == "MediaServer", "媒体通知默认走媒体服务器消息类型")
    pm_other = make_plugin(mod, msgnotify_enabled=True, msgnotify_types="开始播放", msgnotify_notify_type="Other")
    pm_other.on_webhook_message(types.SimpleNamespace(event_data=info))
    check(pm_other._stub_messages and pm_other._stub_messages[0].get("mtype") == mod.NotificationType.Other,
          "媒体通知消息类型支持 其他")
    pm.on_webhook_message(types.SimpleNamespace(event_data=info))
    check(len(pm._stub_messages) == 1, "同 item 重复事件 30s 内去重")
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
    check("<details><summary>📈 站点增量</summary>" in tg_html and "<table>" not in tg_html and "<th" not in tg_html and "<b>馒头</b><br>流量：↑" in tg_html and "<br>指标：分享" in tg_html and "<h3>📈 站点增量</h3>" not in tg_html and "<details><summary>📡 站点状态</summary>" in tg_html and "<details><summary>📥 今日下载</summary>" in tg_html,
          "Telegram RichMessage 明细保留折叠，但移动端/桌面端都不能依赖宽表格布局")
    p_risk = make_plugin(mod, report_site_increment=False, report_today_download=False,
                         report_transfer=False, report_subscribe=False, report_storage=False,
                         report_media_stat=False, report_health=False, report_summary=False)
    p_risk._get_site_health_locked = lambda: ["⦁ 馒头 | 正常", "⦁ 红叶 | 异常（Cookie 失效）"]
    p_risk._version_report_lines = lambda: []
    risk_html = p_risk._build_daily_report_telegram_html(preview=True)
    check("🚨 站点风险</b>" in risk_html and "红叶：异常（Cookie 失效）" in risk_html and "<details><summary>📡 站点状态</summary>" in risk_html,
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
    check("\u200b" in long_storage_html and long_cell not in long_storage_html and "&lt;safe&gt;" in long_storage_html and "<table>" not in long_storage_html and "<table>" not in media_html,
          "Telegram RichMessage 长文本明细使用可换行的移动端友好块，同时保留 HTML escape")
    _SUB["site_refresh_error"] = None
    _SUB["site_refresh_result"] = {"馒头": object()}
    p_tg_send = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                            daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    sent_rich_payloads = []
    p_tg_send._post_telegram_rich_message = lambda rich, token=None, chat_id=None: sent_rich_payloads.append(rich) or True
    check(p_tg_send.run_daily_report() is True and sent_rich_payloads and not p_tg_send._stub_messages,
          "每日汇报只发送 Telegram RichMessage，不再发飞书或 MP 纯文本通知")
    check((p_tg_send._stub_data.get("last_daily_report") or {}).get("message") == "OK telegram_rich_message",
          "每日汇报成功状态明确记录 telegram_rich_message")
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
    p_live_report._post_telegram_rich_message = lambda rich, token=None, chat_id=None: True
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
    p_summary_site_refresh._post_telegram_rich_message = lambda rich, token=None, chat_id=None: True
    check(p_summary_site_refresh.run_daily_report() is True and _SUB["site_refresh_calls"] == 1,
          "即使关闭站点栏目，只要日报摘要会读取站点状态，也必须先刷新当时站点数据")
    p_tg_fallback = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                                daily_report_telegram_bot_token="token", daily_report_telegram_chat_id="chat")
    p_tg_fallback._post_telegram_rich_message = lambda rich, token=None, chat_id=None: False
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
    p_tg_global._post_telegram_rich_message = (
        lambda rich, token=None, chat_id=None: global_send.update(token=token, chat_id=chat_id) or True
    )
    check(p_tg_global.run_daily_report() is True
          and global_send == {"token": "global-token", "chat_id": "-100123"},
          "旧配置未填写 TG 字段时，日报复用 MoviePilot 全局 Telegram 通知配置")
    p_tg_explicit = make_plugin(mod, daily_report_telegram_rich_enabled=True,
                                daily_report_telegram_bot_token="plugin-token", daily_report_telegram_chat_id="67890")
    explicit_send = {}
    p_tg_explicit._post_telegram_rich_message = (
        lambda rich, token=None, chat_id=None: explicit_send.update(token=token, chat_id=chat_id) or True
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
    p_tg_detail._post_telegram_rich_message = (
        lambda rich, token=None, chat_id=None:
        setattr(p_tg_detail, "_daily_report_telegram_last_error", "Telegram RichMessage 返回失败：Bad Request") or False
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
    config_vue = (ROOT / "plugins.v2" / "agentopsassistant" / "src" / "components" / "Config.vue").read_text(encoding="utf-8")
    check('label="Bot Token"' not in config_vue and 'label="Chat ID"' not in config_vue
          and 'label="Telegram RichMessage"' not in config_vue,
          "日报设置页不暴露插件私有 TG Bot Token/Chat ID，默认复用 MoviePilot 全局 Telegram 通知配置")
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
    p_tg_disabled_legacy._post_telegram_rich_message = (
        lambda rich, token=None, chat_id=None: legacy_send.update(token=token, chat_id=chat_id) or True
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
    inc_text = "\n".join(make_plugin(mod)._get_site_increment_locked())
    check("📊 3.405" in inc_text and "⬆" in inc_text and "⬇" in inc_text and "🪙 18,619.5" in inc_text,
          "站点增量使用图标展示分享率/上传/下载/魔力")
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
    p_sr = make_plugin(mod, enabled=True, subscribe_reminder_enabled=True, subscribe_reminder_cron="0 9 * * *")
    sr_ids = [s.get("id") for s in (p_sr.get_service() or [])]
    check("AgentOpsAssistant.SubscribeReminder" in sr_ids, "启用后注册独立订阅追新定时服务")
    p_sr._get_today_subscribe_updates_locked = lambda: ["凡人修仙传 S01E50"]
    sr_sent = {}
    p_sr.post_message = lambda **kw: sr_sent.update(kw)
    ok_sr = p_sr.run_subscribe_reminder()
    check(ok_sr is True and "凡人修仙传" in str(sr_sent.get("text", "")), "run_subscribe_reminder 推送今日追新并返回 True")
    p_sr_other = make_plugin(mod, subscribe_reminder_msgtype="其他")
    p_sr_other._get_today_subscribe_updates_locked = lambda: ["凡人修仙传 S01E51"]
    sr_other_sent = {}
    p_sr_other.post_message = lambda **kw: sr_other_sent.update(kw)
    p_sr_other.run_subscribe_reminder()
    check(getattr(sr_other_sent.get("mtype"), "name", "") == "Other", "订阅追新消息类型支持 其他")
    p_off = make_plugin(mod, enabled=True, subscribe_reminder_enabled=False)
    check("AgentOpsAssistant.SubscribeReminder" not in [s.get("id") for s in (p_off.get_service() or [])], "关闭时不注册订阅追新服务")

    print("== 通知类型统一 ==")
    p_market = make_plugin(mod, market_update_notify=True, market_update_notify_type="Other")
    p_market._build_market_update_status = lambda apply=False: {"success": True, "has_update": True}
    p_market._auto_update_installed_plugins = lambda apply=True: {}
    p_market._format_market_update_text = lambda data: "market update"
    market_sent = {}
    p_market.post_message = lambda **kw: market_sent.update(kw)
    p_market.run_market_update()
    check(getattr(market_sent.get("mtype"), "name", "") == "Other", "插件库更新通知使用所选消息类型")
    p_market_preview_error = make_plugin(mod)
    p_market_preview_error._build_market_update_status = lambda apply=False: (_ for _ in ()).throw(RuntimeError("插件库记录页面获取失败：no_response"))
    market_preview_error = p_market_preview_error.api_preview_market_update()
    check(market_preview_error.get("code") == 1 and "no_response" in market_preview_error.get("msg", ""), "插件库更新预览失败时返回可读错误而不是抛异常")
    check(not p_market_preview_error._stub_messages and not p_market_preview_error._stub_data, "插件库更新预览失败不发消息也不写状态")
    p_update_preview_error = make_plugin(mod)
    p_update_preview_error._build_update_status = lambda: (_ for _ in ()).throw(RuntimeError("release api timeout"))
    update_preview_error = p_update_preview_error.api_preview_updates()
    check(update_preview_error.get("code") == 1 and "release api timeout" in update_preview_error.get("msg", ""), "MP 更新预览失败时返回可读错误而不是抛异常")
    p_log_preview_error = make_plugin(mod)
    p_log_preview_error._build_log_preview = lambda: (_ for _ in ()).throw(RuntimeError("log path denied"))
    log_preview_error = p_log_preview_error.api_preview_log_clean()
    check(log_preview_error.get("code") == 1 and "log path denied" in log_preview_error.get("msg", ""), "日志清理预览失败时返回可读错误而不是抛异常")
    p_plugin_preview_error = make_plugin(mod)
    p_plugin_preview_error._build_plugin_uninstall_status = lambda clean=False: (_ for _ in ()).throw(RuntimeError("plugin list broken"))
    plugin_preview_error = p_plugin_preview_error.api_preview_plugin_uninstall()
    check(plugin_preview_error.get("code") == 1 and "plugin list broken" in plugin_preview_error.get("msg", ""), "插件卸载预览失败时返回可读错误而不是抛异常")
    p_api_task_error = make_plugin(mod)
    p_api_task_error.run_subfill_clear_history = lambda: (_ for _ in ()).throw(RuntimeError("save_data failed"))
    api_task_error = p_api_task_error.api_subfill_clear_history()
    check(api_task_error.get("code") == 1 and "save_data failed" in api_task_error.get("msg", ""), "通用手动任务异常时返回失败信封而不是硬抛")

    print("== 更新检查：通知去重 ==")
    p_update = make_plugin(mod, enabled=True, mp_update_enabled=True, mp_update_notify=True, mp_update_notify_type="Other")
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
    update_titles = [m.get("title") for m in p_update._stub_messages]
    check(len(p_update._stub_messages) == 1, "MP 更新有新版时只发送一条通知")
    check(update_titles == ["MP 运维助手 - MoviePilot更新检查"], "MP 更新通知标题不是预览标题")
    check(getattr(p_update._stub_messages[0].get("mtype"), "name", "") == "Other", "MP 更新通知使用所选消息类型")

    p_update_preview = make_plugin(mod, enabled=True, mp_update_notify=True)
    p_update_preview._get_local_versions = p_update._get_local_versions
    p_update_preview._check_one_release = p_update._check_one_release
    p_update_preview._build_market_status = p_update._build_market_status
    preview_result = p_update_preview.api_preview_updates()
    check(preview_result.get("code") == 0 and not p_update_preview._stub_messages, "MP 更新预览接口不发送通知")
    p_update_restart_preview = make_plugin(mod, enabled=True, mp_update_notify=True, mp_update_restart_confirm=True)
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
    p_cmd_notify = make_plugin(mod, subscribe_reminder_msgtype="Plugin")
    p_cmd_notify._get_today_subscribe_updates_locked = lambda: ["凡人修仙传 S01E52"]
    p_cmd_notify.handle_command(types.SimpleNamespace(event_data={"action": "mpops_subscribe"}))
    cmd_titles = [m.get("title") for m in p_cmd_notify._stub_messages]
    check(cmd_titles == ["MP 运维助手 - 订阅追新"], "命令触发的任务已发送业务通知时，不再补发命令执行结果")

    p_cmd_feedback = make_plugin(mod)
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

    p_cmd_failure = make_plugin(mod)
    p_cmd_failure.run_daily_report = lambda: p_cmd_failure.post_message(mtype=mod.NotificationType.Plugin, title="业务通知", text="日报已发送") or True
    p_cmd_failure.run_health_check = lambda: False
    p_cmd_failure.handle_command(types.SimpleNamespace(event_data={"action": "mpops_run_all"}))
    failure_titles = [m.get("title") for m in p_cmd_failure._stub_messages]
    check(failure_titles == ["业务通知", "MP 运维助手命令执行结果"] and "健康巡查：失败" in p_cmd_failure._stub_messages[-1].get("text", ""),
          "组合命令已有业务通知但存在失败任务时，仍补发失败汇总")

    print("== onlyonce 保存后立即运行一次（修复死开关）==")
    p_once = make_plugin(mod, enabled=True)
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
        "run_daily_report", "run_subscribe_reminder", "run_site_stat",
        "run_downloader_tag", "run_backup", "run_log_clean", "run_mp_update",
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
    hc_service = make_plugin(mod, enabled=True, health_check_enabled=True, health_check_cron="0 */6 * * *")
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

    hc_notify = make_plugin(mod, health_check_notify_type="Other")
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
        else:
            check(False, "manual actions widget is exposed separately")
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
