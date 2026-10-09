"""Bound-source plugin updates through MoviePilot's install service."""

import asyncio
from collections.abc import Mapping
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Any, Dict, Optional
from weakref import WeakKeyDictionary

from .notice_transport import installed_plugin_versions


_install_locks = WeakKeyDictionary()


def _run_host(operation, *, timeout=60):
    """Keep host async resources on their owning loop, never wait on that loop."""
    from app.runtime.loop import main_loop_registry

    loop = main_loop_registry.require()
    try:
        current = asyncio.get_running_loop()
    except RuntimeError:
        current = None
    if current is loop or not loop.is_running():
        raise RuntimeError("插件更新需要在宿主工作线程中执行")
    future = asyncio.run_coroutine_threadsafe(operation(), loop)
    try:
        return future.result(timeout=timeout)
    except FutureTimeoutError:
        future.cancel()
        raise RuntimeError("插件更新服务响应超时") from None


def _value(value):
    return str(getattr(value, "value", value) or "")


def _binding(identity):
    if identity is None:
        return None
    source_type = _value(getattr(identity, "trusted_source_type", None))
    source_key = str(getattr(identity, "trusted_source_key", None) or "")
    revision = getattr(identity, "revision", None)
    if (source_type not in {"official", "third_party"} or not source_key
            or type(revision) is not int or revision < 1):
        return None
    return source_type, source_key, revision


def _candidate(inspection, plugin_id, current_version) -> Optional[Dict[str, Any]]:
    """A host selection is usable only when its online source matches the binding."""
    identity = inspection.identity
    binding = _binding(identity)
    if (not binding or str(inspection.plugin_id).lower() != plugin_id.lower()
            or str(identity.plugin_id).lower() != plugin_id.lower()):
        return None
    selection = inspection.selection
    if _value(selection.status) != "selected":
        if _value(selection.status) == "incomplete" or not inspection.inventory_complete:
            raise RuntimeError(str(selection.reason or "绑定插件库暂时无法读取"))
        return None
    candidate = selection.candidate
    if (candidate is None
            or str(candidate.plugin_id).lower() != plugin_id.lower()
            or (_value(candidate.source_type), candidate.source_key) != binding[:2]):
        # A selected local package or an unbound single market is not an update.
        return None
    version = str(candidate.plugin_version or "")
    repo_url = str(candidate.repo_url or "")
    if not version or not current_version or not repo_url.startswith(("https://", "http://")):
        return None
    metadata = candidate.dto if isinstance(candidate.dto, Mapping) else {}
    history = metadata.get("history") or {}
    history = history if isinstance(history, Mapping) else {}
    note = next((str(note) for number, note in history.items()
                 if str(number).removeprefix("v") == version.removeprefix("v")), "")
    return {
        "id": plugin_id, "name": str(metadata.get("name") or metadata.get("plugin_name") or plugin_id),
        "old": str(current_version), "new": version, "repo_url": repo_url, "history": note,
        "source_type": binding[0], "source_key": binding[1], "source_revision": binding[2],
        "package_generation": candidate.package_generation,
    }


def version_is_newer(target, current):
    from app.foundation.version import compare_version

    return bool(target and current and compare_version(str(target), ">", str(current)))


def same_target(expected, current):
    """Old cards lack binding metadata; their repository must still match exactly."""
    if not current:
        return False
    for key in ("id", "old", "new", "repo_url", "source_type", "source_key", "source_revision", "package_generation"):
        if key not in expected and key not in {"id", "old", "new", "repo_url"}:
            continue
        left, right = str(expected.get(key) or ""), str(current.get(key) or "")
        if key == "repo_url":
            left, right = left.rstrip("/").lower(), right.rstrip("/").lower()
        if left != right:
            return False
    return True


def inspect_bound_candidate(plugin_id, current_version):
    async def inspect():
        from app.application.plugin.gateway import get_plugin_install_service

        inspection = await get_plugin_install_service().inspect_source(plugin_id=plugin_id, force=False)
        return _candidate(inspection, plugin_id, current_version)

    return _run_host(inspect)


def install_bound_update(target):
    """Recheck at execution, use the bound repository, and verify the loaded result."""
    async def install():
        from app.application.plugin.gateway import get_plugin_install_service
        from app.application.plugin.lifecycle import plugin_lifecycle

        plugin_id = target["id"]
        locks = _install_locks.setdefault(asyncio.get_running_loop(), {})
        async with locks.setdefault(plugin_id.lower(), asyncio.Lock()):
            service = get_plugin_install_service()

            async def read_current():
                inspection = await service.inspect_source(plugin_id=plugin_id, force=False)
                version = installed_plugin_versions().get(plugin_id, "")
                candidate = _candidate(inspection, plugin_id, version)
                updatable = candidate if candidate and version_is_newer(candidate["new"], version) else None
                return version, updatable

            # The host's per-plugin hold is not reentrant. Its public lease lets
            # us keep the binding stable across inspection and gateway admission;
            # other plugin installs wait until this operation finishes.
            async with plugin_lifecycle.hold_startup() as lease:
                try:
                    current_version, current = await read_current()
                    if not current or not same_target(target, current):
                        return {"status": "stale", "candidate": current,
                                "already_current": current_version == target["new"]}
                    result = await service.install(
                        plugin_id=plugin_id, repo_url=current["repo_url"],
                        package_version=current["package_generation"],
                        # Pin this already-bound online repository. Without an
                        # explicit repository the gateway can prefer a new local
                        # package. This grants neither a rebind nor force rights.
                        explicit_source=True, source_change=False, force=False,
                        startup_token=lease,
                    )
                    if not result.success:
                        raise RuntimeError(str(result.message or "插件更新未完成"))
                    # The gateway owns reload/registration. A second reload here
                    # can run plugin startup twice; only read the loaded result.
                    actual = installed_plugin_versions().get(plugin_id, "")
                    after = await service.inspect_source(plugin_id=plugin_id, force=False)
                    binding = _binding(after.identity)
                    if (not binding or binding[:2] != (current["source_type"], current["source_key"])
                            or (_value(after.identity.payload_source_type), after.identity.payload_source_key) != binding[:2]):
                        raise RuntimeError("安装后插件来源复核不一致")
                    if actual != current["new"]:
                        raise RuntimeError(f"安装后版本复核不一致：目标 {current['new']}，实际 {actual or '未知'}")
                    return {"status": "updated"}
                except Exception as err:
                    # Never offer the pre-install snapshot as a retry. A failed
                    # install or readback can leave a different binding/version.
                    try:
                        _, candidate = await read_current()
                    except Exception:
                        candidate = None
                    return {"status": "failed", "message": str(err), "candidate": candidate}

    return _run_host(install, timeout=600)
