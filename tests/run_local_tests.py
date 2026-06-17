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
import sys
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
_PU = {"online": [], "local": [], "installed": [], "running": [],
       "install_result": (True, "ok"), "install_calls": [], "reloaded": []}


class _StubPluginManager:
    def get_online_plugins(self): return list(_PU["online"])
    def get_local_plugins(self): return list(_PU["local"])
    def reload_plugin(self, pid): _PU["reloaded"].append(pid)
    def get_plugin_apis(self): return []


class _StubPluginHelper:
    def install(self, pid=None, repo_url=None):
        _PU["install_calls"].append((pid, repo_url))
        return _PU["install_result"]


class _StubScheduler:
    def list(self):
        return [types.SimpleNamespace(id=i, status="正在运行") for i in _PU["running"]]
    def update_plugin_job(self, pid): pass


class _StubSystemConfigOper:
    def get(self, key):
        return list(_PU["installed"]) if key == "UserInstalledPlugins" else None


# 订阅规则填充桩：_SUB 配置下载历史/订阅列表，并记录 update 调用
_SUB = {"history": None, "subs": [], "updates": [], "sub_get": None, "sites": [], "site_latest": []}


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
    scht.SystemConfigKey = types.SimpleNamespace(Storages="Storages", UserInstalledPlugins="UserInstalledPlugins", RssSites="RssSites")
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
    dho = _mod("app.db.downloadhistory_oper")
    dho.DownloadHistoryOper = _StubDownloadHistoryOper
    subo = _mod("app.db.subscribe_oper")
    subo.SubscribeOper = _StubSubscribeOper
    siteo = _mod("app.db.site_oper")
    siteo.SiteOper = _StubSiteOper
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

    print("== 插件残留治理（多选 ID 回归）==")
    r1 = make_plugin(mod, plugin_uninstall_ids=["AutoBackup"])._build_plugin_uninstall_status(clean=False)
    check(r1.get("plugin_id") == "AutoBackup" and not r1.get("blocked") and r1.get("success") is True,
          "多选列表被识别（不再因单 ID 为空而 blocked）")
    r2 = make_plugin(mod, plugin_uninstall_ids=[])._build_plugin_uninstall_status(clean=False)
    check(bool(r2.get("blocked")) and r2.get("success") is False, "空目标 -> blocked，不误删")
    r3 = make_plugin(mod, plugin_uninstall_ids=["moviepilot"])._build_plugin_uninstall_status(clean=True)
    check(r3.get("success") is False and any("moviepilot" in e.lower() for e in r3.get("errors", [])),
          "禁止治理 MoviePilot/本体（保护）")
    r4 = make_plugin(mod, plugin_uninstall_ids=["A", "B"])._build_plugin_uninstall_status(clean=False)
    check(r4.get("plugin_id") == "A、B", "多个插件 ID 合并展示")

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
    check(any("馒头 | 正常" in x for x in sh_today_time), "站点状态：updated_day 带时间也识别为今日正常")

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

    print("== onlyonce 保存后立即运行一次（修复死开关）==")
    p_once = make_plugin(mod, enabled=True)
    once_calls = []
    p_once.run_backup = lambda: once_calls.append("backup") or True
    p_once.run_log_clean = lambda: once_calls.append("log") or True
    p_once.run_market_update = lambda: once_calls.append("market") or True
    p_once.run_subscribe_reminder = lambda: once_calls.append("sub") or True
    cfg_once = {"backup_onlyonce": True, "log_clean_onlyonce": True}
    fired = p_once._fire_onlyonce(cfg_once)
    check(set(fired) == {"backup_onlyonce", "log_clean_onlyonce"}, "onlyonce 命中置位的两个开关")
    check(cfg_once["backup_onlyonce"] is False and cfg_once["log_clean_onlyonce"] is False, "onlyonce 命中后清零（防重载重复触发）")
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
    svcs = pa.get_service() or []
    check(all(callable(s.get("func")) for s in svcs), f"get_service 全部 func 可调用（{len(svcs)} 个）")
    cmds = mod.AgentOpsAssistant.get_command() or []
    check(isinstance(cmds, list) and all(c.get("data", {}).get("action") for c in cmds), "get_command 结构完整")
    check(pa.get_render_mode()[0] == "vue", "渲染模式 = vue")
    form_schema, form_default = pa.get_form()
    check(form_schema == [] and isinstance(form_default, dict) and form_default, "get_form Vue 模式返回 ([], 默认配置dict)")
    check(pa.get_page() == [], "get_page Vue 模式返回 []")

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
