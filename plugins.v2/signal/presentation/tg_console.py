import re
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.log import logger
from app.schemas import NotificationType

from .tg_console_render import TgConsoleRenderMixin
from .tg_console_fusion import TgConsoleFusionMixin
from .tg_console_callback import TgConsoleCallbackMixin
from .tg_console_state import TgConsoleStateMixin


class TgConsoleMixin(
    TgConsoleRenderMixin,
    TgConsoleFusionMixin,
    TgConsoleCallbackMixin,
    TgConsoleStateMixin,
):
    """Telegram fusion card ? composition of render, fusion, callback, and state mixins."""

    pass
