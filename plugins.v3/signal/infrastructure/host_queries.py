"""Read-only host queries via the official V3 SDK query facade.

`app.sdk.queries` is the sanctioned read-only surface for subscriptions and
history. It returns DTOs whose base class normalizes media identity: a dirty
half-pair becomes an empty identity, and an unknown legacy source degrades to
empty instead of failing the whole page. That is strictly safer than reading ORM
rows directly, so Signal reads through this module.

Two things this module exists to get right:

1. **No silent truncation.** The facade is paginated (default 50, max 200). A
   caller that wants "all subscriptions" must walk every page. Returning the
   first page would silently drop a user's data, so `list_all_*` here pages to
   exhaustion and raises if the host reports more pages than it will serve.

2. **Honest gaps.** `TransferHistoryFilter` has no date field, so "today's
   transfers" cannot be expressed through the facade. That one query stays on the
   canonical `TransferHistoryOper` with the reason recorded here rather than
   being emulated by paging the entire history.
"""

from typing import Any, Callable, Dict, List, Optional

from app.sdk.logging import logger

# The facade caps a page at MAX_QUERY_PAGE_SIZE; ask for the largest legal page
# so full reads cost the fewest round trips.
_PAGE_SIZE = 200

# A hard stop so a host that misreports `total` cannot spin this loop forever.
_MAX_PAGES = 500


def _walk_pages(fetch: Callable[[int], Any], what: str) -> List[Any]:
    """Page a facade query to exhaustion, never silently truncating."""
    items: List[Any] = []
    page = 1
    while page <= _MAX_PAGES:
        result = fetch(page)
        batch = list(getattr(result, "items", None) or [])
        items.extend(batch)
        total = getattr(result, "total", None)
        has_more = getattr(result, "has_more", None)
        if has_more is None:
            # Fall back to the count/total relation if the DTO lacks has_more.
            has_more = bool(total is not None and len(items) < int(total))
        if not has_more or not batch:
            return items
        page += 1
    raise RuntimeError(
        f"{what} 分页读取超过 {_MAX_PAGES} 页仍未结束，已中止以避免无限循环"
    )


def list_all_subscriptions() -> List[Any]:
    """Return every subscription as a SubscriptionSnapshot DTO."""
    from app.sdk.queries import list_subscriptions

    return _walk_pages(
        lambda page: list_subscriptions(page={"page": page, "count": _PAGE_SIZE}),
        "订阅列表",
    )


def get_subscription(subscription_id: Any) -> Optional[Any]:
    """Return one subscription DTO, or None when it does not exist."""
    from app.sdk.queries import get_subscription as _get

    try:
        return _get(int(subscription_id))
    except (TypeError, ValueError):
        return None


def list_subscriptions_by_identity(media_source: Any, media_id: Any) -> List[Any]:
    """Return subscriptions sharing one media identity.

    `SubscriptionFilter` inherits `MediaIdentityQuery`, which rejects an explicit
    half-pair outright, so callers must pass both halves or neither.
    """
    from app.sdk.queries import list_subscriptions

    filters: Dict[str, Any] = {"media_source": media_source, "media_id": str(media_id)}
    return _walk_pages(
        lambda page: list_subscriptions(
            filters=filters, page={"page": page, "count": _PAGE_SIZE}
        ),
        "按媒体身份查询订阅",
    )


def count_subscriptions() -> int:
    """Return the total subscription count.

    Reads the facade's reported total from a single minimal page instead of
    walking every page, since only the count is needed.
    """
    from app.sdk.queries import list_subscriptions

    result = list_subscriptions(page={"page": 1, "count": 1})
    total = getattr(result, "total", None)
    if total is None:
        return len(list(getattr(result, "items", None) or []))
    return int(total)


def get_download_history_by_hash(download_hash: str) -> Optional[Any]:
    """Return the download history DTO for a torrent hash, if present."""
    from app.sdk.queries import list_download_history

    if not download_hash:
        return None
    result = list_download_history(
        filters={"download_hash": str(download_hash)},
        page={"page": 1, "count": 1},
    )
    items = list(getattr(result, "items", None) or [])
    return items[0] if items else None


def list_transfer_history_for_date_prefix(date_prefix: str) -> List[Any]:
    """Return transfer history rows for one day.

    Kept on the canonical `TransferHistoryOper`: `TransferHistoryFilter` exposes
    no date field, so this query cannot be expressed through the SDK facade
    without paging the entire history and filtering client-side. This is a
    canonical Oper, not a legacy compat shim.
    """
    from app.db.oper.transferhistory import TransferHistoryOper

    try:
        return list(TransferHistoryOper().list_by_date(f"{date_prefix} 00:00:00") or [])
    except Exception as err:
        logger.warning(f"Signal 读取当日整理记录失败：{err}")
        raise
