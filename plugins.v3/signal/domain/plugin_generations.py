"""Plugin generation paths.

A V3 host still carries plugin trees from earlier generations: users upgrade in
place, and the official repository keeps `plugins/`, `plugins.v2/` and
`plugins.v3/` side by side. Backup, uninstall and purge must therefore look in
every generation directory, not just the one this build ships from. Hardcoding a
single generation is how a source tree gets silently skipped.
"""

from pathlib import Path
from typing import Iterator, List

# Newest first: a V3 host resolves its own generation before older leftovers.
PLUGIN_GENERATION_DIRS = ("plugins.v3", "plugins.v2", "plugins")


def generation_roots(repo_root: Path) -> List[Path]:
    """Return every generation plugin directory under a local plugin repository."""
    return [Path(repo_root) / name for name in PLUGIN_GENERATION_DIRS]


def generation_plugin_paths(repo_root: Path, plugin_id: str) -> Iterator[Path]:
    """Yield candidate plugin directories across generations, both casings."""
    lower = str(plugin_id).lower()
    for root in generation_roots(repo_root):
        yield root / lower
        if plugin_id != lower:
            yield root / plugin_id
