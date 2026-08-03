"""Transport-neutral V7 Fusion card composition model."""

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional

from .fusion_card_state import FUSION_TIER_ORDER, FUSION_OWNER_ORDER


MODEL_SCHEMA = "signal-fusion-v7-card-model/v1"
VALID_STATES = {"normal", "active", "alert", "loading"}


def build_v7_card_model(snapshot: Optional[Dict[str, Any]] = None, *, state: str = "normal") -> Dict[str, Any]:
    source = deepcopy(snapshot) if isinstance(snapshot, dict) else {}
    state_key = str(state or "normal").strip()
    if state_key not in VALID_STATES:
        raise ValueError(f"unsupported V7 card state: {state_key}")
    identity = _identity(source.get("identity"))
    if state_key == "loading":
        modules = [_loading_module(source.get("loading"))]
        return _model(state_key, identity, modules, suppressed=[])

    modules: List[Dict[str, Any]] = []
    anomalies = _anomaly_modules(source.get("anomalies")) if state_key == "alert" else []
    modules.extend(anomalies)
    anomaly_owners = {
        str(owner)
        for item in anomalies
        for owner in item.get("affected_owners") or []
        if owner
    }

    realtime = _realtime_modules(source.get("realtime")) if state_key in {"active", "alert"} else []
    suppressed = set(source.get("suppressed_owners") or [])
    suppressed.update(anomaly_owners)
    modules.extend(item for item in realtime if item["owner"] not in suppressed)

    persistent = source.get("persistent") if isinstance(source.get("persistent"), dict) else {}
    for key in ("sites", "subscriptions", "storage"):
        module = _persistent_module(key, persistent.get(key))
        if module and module["owner"] not in suppressed:
            modules.append(module)

    completion = _completion_module(source.get("completion"))
    if completion:
        modules.append(completion)
    return _model(state_key, identity, modules, suppressed=sorted(suppressed))


def replace_v7_module(model: Dict[str, Any], owner: str, module: Dict[str, Any]) -> Dict[str, Any]:
    """Replace exactly one owner while preserving every other module and order."""
    owner_key = str(owner or "").strip()
    if not owner_key:
        raise ValueError("owner is required")
    result = deepcopy(model)
    modules = list(result.get("modules") or [])
    replacement = deepcopy(module)
    replacement["owner"] = owner_key
    for index, item in enumerate(modules):
        if item.get("owner") == owner_key:
            modules[index] = replacement
            result["modules"] = _stable_v7_modules(modules)
            return validate_v7_card_model(result)
    modules.append(replacement)
    result["modules"] = _stable_v7_modules(modules)
    return validate_v7_card_model(result)


def remove_v7_module(model: Dict[str, Any], owner: str) -> Dict[str, Any]:
    """Remove one owner without reordering or clearing settled modules."""
    owner_key = str(owner or "").strip()
    if not owner_key:
        raise ValueError("owner is required")
    result = deepcopy(model)
    result["modules"] = [item for item in result.get("modules") or [] if item.get("owner") != owner_key]
    return validate_v7_card_model(result)


def module_for_owner(model: Dict[str, Any], owner: str) -> Optional[Dict[str, Any]]:
    key = str(owner or "").strip()
    return next((deepcopy(item) for item in model.get("modules") or [] if item.get("owner") == key), None)


def validate_v7_card_model(model: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(model, dict) or model.get("schema") != MODEL_SCHEMA:
        raise ValueError("invalid V7 card model")
    if model.get("state") not in VALID_STATES:
        raise ValueError("invalid V7 card state")
    modules = list(model.get("modules") or [])
    owners = [str(item.get("owner") or "") for item in modules]
    if any(not owner for owner in owners):
        raise ValueError("every V7 module needs an owner")
    if len(set(owners)) != len(owners):
        raise ValueError("V7 module owners must be unique")
    tier_rank = {tier: index for index, tier in enumerate(FUSION_TIER_ORDER)}
    expected = sorted(
        modules,
        key=lambda item: (tier_rank.get(item.get("tier"), 999), FUSION_OWNER_ORDER.get(item.get("owner"), 999), item.get("owner", "")),
    )
    if [item.get("owner") for item in expected] != owners:
        raise ValueError("V7 modules are not in stable tier order")
    for item in modules:
        if item.get("tier") not in FUSION_TIER_ORDER:
            raise ValueError(f"unsupported V7 module tier: {item.get('tier')}")
        if item.get("always_visible_preview") and not item.get("preview_rows"):
            raise ValueError(f"visible V7 module has no preview rows: {item.get('owner')}")
        if item.get("details_rows") is not None and not isinstance(item.get("details_rows"), list):
            raise ValueError(f"Details rows must be a list: {item.get('owner')}")
    return deepcopy(model)


def _stable_v7_modules(modules: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tier_rank = {tier: index for index, tier in enumerate(FUSION_TIER_ORDER)}
    return sorted(
        (deepcopy(item) for item in modules),
        key=lambda item: (
            tier_rank.get(item.get("tier"), 999),
            FUSION_OWNER_ORDER.get(item.get("owner"), 999),
            item.get("owner", ""),
        ),
    )


def _model(state: str, identity: Dict[str, Any], modules: List[Dict[str, Any]], suppressed: Iterable[str]) -> Dict[str, Any]:
    model = {
        "schema": MODEL_SCHEMA,
        "state": state,
        "identity": identity,
        "tier_order": list(FUSION_TIER_ORDER),
        "suppressed_owners": list(suppressed),
        "modules": modules,
    }
    return validate_v7_card_model(model)


def _identity(value: Any) -> Dict[str, Any]:
    data = value if isinstance(value, dict) else {}
    return {
        "owner": "card",
        "tier": "identity",
        "title": str(data.get("title") or "运维助手 · 融合通知"),
"version": str(data.get("version") or "v1.0.4"),
        "refreshed_at": str(data.get("refreshed_at") or ""),
    }


def _anomaly_modules(value: Any) -> List[Dict[str, Any]]:
    items = value if isinstance(value, list) else []
    if not items:
        return []
    grouped = items[0] if len(items) == 1 and isinstance(items[0], dict) and items[0].get("owner") == "current-anomalies" else {
        "owner": "current-anomalies",
        "kicker": "当前异常",
        "count": f"{len(items)} 项",
        "primary": "需要关注",
        "context": "健康巡查 · 配置备份",
        "meta": "",
        "details_rows": items,
        "affected_owners": [item.get("affected_owner") for item in items if isinstance(item, dict)],
    }
    return [_module("current-anomalies", "anomalies", grouped, always_visible=False)]


def _realtime_modules(value: Any) -> List[Dict[str, Any]]:
    items = value if isinstance(value, list) else []
    modules = []
    for item in items:
        if not isinstance(item, dict):
            continue
        owner = str(item.get("owner") or "").strip()
        if owner not in {"realtime-media", "realtime-task-backup"}:
            continue
        modules.append(_module(owner, "realtime", item, always_visible=False))
    return modules


def _persistent_module(key: str, value: Any) -> Optional[Dict[str, Any]]:
    data = value if isinstance(value, dict) else {}
    mapping = {
        "sites": ("persistent-sites", "站点数据"),
        "storage": ("persistent-storage", "存储空间"),
        "subscriptions": ("persistent-subscriptions", "订阅追新"),
    }
    owner_tier = mapping.get(key)
    if not owner_tier or not data:
        return None
    owner, default_kicker = owner_tier
    data = {"kicker": default_kicker, **data}
    return _module(owner, "persistent", data, always_visible=True)


def _completion_module(value: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(value, dict):
        return None
    return _module("today-completion", "completion", value, always_visible=False)


def _loading_module(value: Any) -> Dict[str, Any]:
    data = value if isinstance(value, dict) else {}
    return {
        "owner": "card-creation",
        "tier": "identity",
        "kind": "loading",
        "kicker": "建卡中",
        "tasks": deepcopy(data.get("tasks") or []),
        "status": str(data.get("status") or "collecting"),
        "always_visible_preview": True,
        "preview_rows": deepcopy(data.get("tasks") or []),
        "details_rows": [],
    }


def _module(owner: str, tier: str, data: Dict[str, Any], *, always_visible: bool) -> Dict[str, Any]:
    return {
        "owner": owner,
        "tier": tier,
        "kind": str(data.get("kind") or tier),
        "kicker": str(data.get("kicker") or ""),
        "count": str(data.get("count") or ""),
        "primary": str(data.get("primary") or data.get("title") or ""),
        "status": str(data.get("status") or data.get("level") or ""),
        "context": str(data.get("context") or data.get("body") or ""),
        "meta": str(data.get("meta") or data.get("updated_at") or ""),
        "progress": str(data.get("progress") or ""),
        "session_ip": str(data.get("session_ip") or ""),
        "playback_url": str(data.get("playback_url") or ""),
        "preview_rows": deepcopy(data.get("preview_rows") or []),
        "details_rows": deepcopy(data.get("details_rows") or []),
        "tasks": deepcopy(data.get("tasks") or []),
        "always_visible_preview": bool(always_visible),
        "streaming": bool(data.get("streaming") or tier == "realtime"),
        "affected_owner": str(data.get("affected_owner") or ""),
        "affected_owners": [str(owner) for owner in data.get("affected_owners") or [] if owner],
    }
