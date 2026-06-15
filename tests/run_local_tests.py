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
    sch.NotificationType = types.SimpleNamespace(Plugin="Plugin", SiteMessage="SiteMessage")
    sch.ServiceInfo = object
    scht = _mod("app.schemas.types")
    scht.EventType = types.SimpleNamespace(
        PluginAction="PluginAction", WebhookMessage="WebhookMessage",
        SubscribeAdded="SubscribeAdded", DownloadAdded="DownloadAdded",
    )
    scht.SystemConfigKey = types.SimpleNamespace(Storages="Storages")
    http = _mod("app.utils.http")
    http.RequestUtils = _StubRequestUtils
    stru = _mod("app.utils.string")
    stru.StringUtils = _StubStringUtils
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
             tracker="https://tracker.example.com/announce", state="pausedUP", category="tv")
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
        self.stopped, self.deleted, self.deleted_with_files = [], [], []
    def is_inactive(self): return False
    def get_torrents(self, tags=None): return (self._torrents, False)
    def stop_torrents(self, ids=None): self.stopped.extend(ids or [])
    def delete_torrents(self, delete_file=False, ids=None):
        (self.deleted_with_files if delete_file else self.deleted).extend(ids or [])


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

    print("== 存储行（_append_usage_line）==")
    items = []
    ok = p._append_usage_line(items, "本地", 100, None, 40)  # total=100, free=40 -> used=60
    check(ok is True and len(items) == 1 and "已用 60%" in items[0], "有真实用量才输出，已用百分比正确")
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
