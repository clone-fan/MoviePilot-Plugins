"""Idempotent migration of Signal's persisted media identities to V3 format.

V2 stored the download-fill dedup key as ``{type}:{tmdbid}`` — a bare numeric ID
with the source left implicit. V3 keys it as ``{type}:{media_key}`` where
``media_key`` comes from ``build_media_key()`` and looks like ``tmdb:12345``.

An upgraded install therefore carries dedup keys that can never match a freshly
computed one, which would let an already-filled subscription be filled a second
time. This module rewrites those keys once, in place.

Backfilling the source as TMDB is sound rather than a guess: the V2 code path
that wrote these keys queried ``SubscribeOper.list_by_tmdbid``, so every stored
ID was by construction a TMDB ID.

Contract, per plan section V2:

* a value already in V3 form is left untouched;
* a legacy value is backfilled from its old ID;
* the new value is written and verified before the old one is dropped;
* an entry with no resolvable identity is preserved as-is, never discarded;
* the marker is versioned and the whole pass is repeatable;
* any failure is logged and swallowed so it can never block reading old data.
"""

from typing import Any, Dict, List, Optional, Tuple

from app.sdk.logging import logger

# Bump when the migration logic itself changes in a way that must re-run.
IDENTITY_MIGRATION_VERSION = 1
IDENTITY_MIGRATION_KEY = "identity_migration_state_v1"

# The V2 writer for this key only ever resolved TMDB IDs.
_LEGACY_SUBFILL_SOURCE = "themoviedb"


def _looks_like_v3_key(candidate: str) -> bool:
    """True when the identity segment already parses as a V3 media key."""
    from app.sdk.media import parse_media_key

    source, media_id = parse_media_key(candidate)
    return bool(source and media_id)


def _split_subfill_entry(entry: Any) -> Optional[Tuple[str, str]]:
    """Split a stored ``{type}:{identity}`` entry, or None if unparseable."""
    text = str(entry or "").strip()
    if not text or ":" not in text:
        return None
    media_type, _, identity = text.partition(":")
    media_type = media_type.strip()
    identity = identity.strip()
    if not media_type or not identity:
        return None
    return media_type, identity


def migrate_subfill_handled(entries: Any) -> Tuple[List[str], Dict[str, int]]:
    """Return (migrated entries, stats) for one ``subfill_handled`` list.

    Pure and total: it never raises and never drops an entry it cannot
    understand, so a malformed record degrades to "left alone" rather than
    "silently deleted".
    """
    from app.sdk.media import build_media_key

    stats = {
        "total": 0,
        "already_v3": 0,
        "migrated": 0,
        "kept_unresolved": 0,
        "dropped_empty": 0,
    }
    if not isinstance(entries, (list, tuple)):
        return [], stats

    migrated: List[str] = []
    seen = set()

    for entry in entries:
        stats["total"] += 1
        original = str(entry or "").strip()

        if not original:
            # An empty entry is not a record: it carries no identity and no
            # information, so it is counted as dropped rather than "kept".
            stats["dropped_empty"] += 1
            continue

        parts = _split_subfill_entry(original)

        if parts is None:
            stats["kept_unresolved"] += 1
            result = original
        else:
            media_type, identity = parts
            if _looks_like_v3_key(identity):
                stats["already_v3"] += 1
                result = original
            else:
                media_key = build_media_key(_LEGACY_SUBFILL_SOURCE, identity)
                if media_key:
                    stats["migrated"] += 1
                    result = f"{media_type}:{media_key}"
                else:
                    # No usable identity: preserve rather than discard.
                    stats["kept_unresolved"] += 1
                    result = original

        if result not in seen:
            seen.add(result)
            migrated.append(result)

    return migrated, stats


class IdentityMigrationMixin:
    """Runs the persisted-identity migration once per version, on startup."""

    def _identity_migration_state(self) -> Dict[str, Any]:
        state = self.get_data(IDENTITY_MIGRATION_KEY)
        return state if isinstance(state, dict) else {}

    def _identity_migration_completed(self) -> bool:
        state = self._identity_migration_state()
        try:
            return int(state.get("version") or 0) >= IDENTITY_MIGRATION_VERSION
        except (TypeError, ValueError):
            return False

    def run_identity_migration(self, force: bool = False) -> Dict[str, Any]:
        """Migrate persisted identities to V3 format. Safe to call repeatedly."""
        result: Dict[str, Any] = {
            "version": IDENTITY_MIGRATION_VERSION,
            "skipped": False,
            "keys": {},
            "errors": [],
        }

        if not force and self._identity_migration_completed():
            result["skipped"] = True
            return result

        try:
            stored = self.get_data("subfill_handled")
            if stored:
                migrated, stats = migrate_subfill_handled(stored)
                result["keys"]["subfill_handled"] = stats
                if stats["migrated"]:
                    # Write the new value first; only a confirmed write advances
                    # the marker, so an interrupted run simply repeats.
                    self.save_data("subfill_handled", migrated)
                    written = self.get_data("subfill_handled")
                    if list(written or []) != migrated:
                        raise RuntimeError("subfill_handled 迁移写入未生效")
                    logger.info(
                        f"Signal 媒体身份迁移：subfill_handled 迁移 {stats['migrated']} 条，"
                        f"保留 {stats['already_v3']} 条已是 V3 格式，"
                        f"保留 {stats['kept_unresolved']} 条无法解析"
                    )
            else:
                result["keys"]["subfill_handled"] = {
                    "total": 0, "already_v3": 0, "migrated": 0,
                    "kept_unresolved": 0, "dropped_empty": 0,
                }
        except Exception as err:
            # Never block plugin startup or old-data reads on a migration fault.
            logger.warning(f"Signal 媒体身份迁移失败（不影响运行）：{err}")
            result["errors"].append(str(err))
            return result

        try:
            self.save_data(IDENTITY_MIGRATION_KEY, {
                "version": IDENTITY_MIGRATION_VERSION,
                "keys": result["keys"],
            })
        except Exception as err:
            logger.warning(f"Signal 媒体身份迁移标记写入失败：{err}")
            result["errors"].append(str(err))

        return result
