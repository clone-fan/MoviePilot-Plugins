"""Telegram bot token redaction for logs and persisted task results.

Telegram bot tokens travel inside request URLs
(``https://api.telegram.org/bot<digits>:<token>/<method>``), so any exception,
HTTP error body or ``requests`` transport message raised while talking to the
Bot API can carry the raw secret. Logs and saved task results must never keep
it: the card refresh / update-center sinks below funnel their error text
through :func:`telegram_safe_error` before logging or persisting it.

Only the credential is replaced; the surrounding error text stays readable.
"""

import re
from typing import Any

# The two shapes the Bot API token takes in an error string. The URL and bare
# ``bot<digits>:<token>`` forms drop the whole credential, because the numeric
# id is part of the secret. The fallback ``<digits>:<token>`` form keeps the
# existing narrow scope: five or more leading digits and a token-like tail.
_BOT_TOKEN_PATTERN = re.compile(
    r"(?:bot\d+:([A-Za-z0-9_-]+)|(?<!\d)\d{5,}:([A-Za-z0-9_-]+))"
)

_DEFAULT_ERROR_LIMIT = 200


def _mask_bot_token(match: "re.Match[str]") -> str:
    return "bot***" if match.group(1) else "***TOKEN***"


def telegram_safe_error(value: Any, limit: int = _DEFAULT_ERROR_LIMIT) -> str:
    """Return ``value`` as text with Telegram bot tokens masked.

    ``bot<digits>:<token>`` and ``<digits>:<token>`` become ``bot***`` /
    ``***TOKEN***``. ``limit`` truncates the sanitized text (0 disables the
    truncation).
    """
    text = _BOT_TOKEN_PATTERN.sub(_mask_bot_token, str(value or ""))
    if limit and len(text) > limit:
        return text[:limit]
    return text