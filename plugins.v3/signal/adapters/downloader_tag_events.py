"""Downloader Helper event adapters.

DownloadAdded is deliberately limited to tagging/seeding.  Destructive cleanup
is only triggered by the explicit source-file/download-deleted listeners or by
the scheduled/manual pipeline.
"""

from typing import Any


class DownloaderTagEventsMixin:
    """Translate MoviePilot download events into bounded helper runs."""

    def _dltag_event_context(self, data: dict) -> dict:
        context = data.get("context") or {}
        source_file = data.get("source_file") or self._dltag_value(context, "source_file")
        source_path = data.get("src") or data.get("path") or (source_file if isinstance(source_file, str) else self._dltag_value(source_file, "src", "path", "file_path"))
        return {
            "context": context,
            "torrent_info": data.get("torrent_info") or self._dltag_value(context, "torrent_info"),
            "source_file": source_file,
            "source_file_path": source_path,
            "site_name": data.get("site_name") or data.get("sitename"),
            "hash": data.get("hash") or data.get("download_hash") or data.get("torrent_hash"),
        }

    def on_download_tag(self, event: Any = None):
        """DownloadAdded can tag and resume seeding, never delete a task."""
        if self._event_should_noop_after_stop():
            return
        ok, _ = self._runtime_gate("event", component="dltag", name="DownloadAdded")
        if not ok or not self._dltag_enabled or not getattr(self, "_dltag_listen_download", True) or not event or not getattr(event, "event_data", None):
            return
        data = dict(event.event_data or {})
        event_context = self._dltag_event_context(data)
        torrent_hash = event_context.get("hash")
        self.run_downloader_helper(
            target_hashes=[str(torrent_hash)] if torrent_hash else None,
            event_context=event_context,
            trigger="download",
            task_override=["tagging", "seeding"],
        )

    def on_download_file_deleted(self, event: Any = None):
        """Source file removal only runs the bounded cleanup task."""
        if self._event_should_noop_after_stop():
            return
        ok, _ = self._runtime_gate("event", component="dltag", name="DownloadFileDeleted")
        if not ok or not self._dltag_enabled or not getattr(self, "_dltag_listen_source_file", False) or not event or not getattr(event, "event_data", None):
            return
        data = dict(event.event_data or {})
        context = self._dltag_event_context(data)
        self.run_downloader_helper(event_context=context, trigger="source_file", task_override=["cleanup"])

    def on_download_deleted(self, event: Any = None):
        """A deleted download task only allows matching-torrent cleanup."""
        if self._event_should_noop_after_stop():
            return
        ok, _ = self._runtime_gate("event", component="dltag", name="DownloadDeleted")
        if not ok or not self._dltag_enabled or not getattr(self, "_dltag_listen_source_file", False) or not event or not getattr(event, "event_data", None):
            return
        data = dict(event.event_data or {})
        deleted = (data.get("torrents") or [data.get("torrent") or data])[0]
        self.run_downloader_helper(event_context={"deleted_torrent": deleted}, trigger="download_deleted", task_override=["cleanup"])
