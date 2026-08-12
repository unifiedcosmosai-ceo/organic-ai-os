"""
watcher.py - Event-getriebener Watch-Ordner (Layer 08 Immunsystem).

Nutzt watchdog fuer sofortige Datei-Events (create/modify/move).
Faellt auf Polling zurueck, falls watchdog nicht installiert ist.

Callback-Signatur: on_file(path: Path, event: str)
  event in {"created", "modified"}
"""

import threading
from pathlib import Path

from organics_log import get_logger

logger = get_logger("watcher")

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    _WATCHDOG_AVAILABLE = True
except ImportError:
    FileSystemEventHandler = None
    Observer = None
    _WATCHDOG_AVAILABLE = False

SUFFIXES = {".fasta", ".fa", ".fas", ".fastq", ".fq", ".txt"}


def _matches(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUFFIXES


if _WATCHDOG_AVAILABLE:

    class _Handler(FileSystemEventHandler):
        def __init__(self, callback):
            self.callback = callback

        def on_created(self, event):
            if not event.is_directory:
                self._fire(event.event_type, getattr(event, "dest_path", None) or event.src_path)

        def on_modified(self, event):
            if not event.is_directory:
                self._fire(event.event_type, getattr(event, "dest_path", None) or event.src_path)

        def on_moved(self, event):
            if not event.is_directory:
                self._fire("created", event.dest_path)

        def _fire(self, kind, raw_path):
            path = Path(raw_path)
            if _matches(path):
                try:
                    self.callback(path, kind)
                except Exception as exc:  # Callback-Fehler duerfen den Watcher nie toeten
                    logger.error("Watcher callback Fehler fuer %s: %s", path, exc)


class DirectoryWatcher:
    """Beobachtet einen Ordner. Startet als Daemon-Thread."""

    def __init__(self, watch_dir: Path, on_file, interval: float = 2.0):
        self.watch_dir = watch_dir
        self.on_file = on_file
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None
        self._observer = None

    def start(self):
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        if _WATCHDOG_AVAILABLE:
            self._start_watchdog()
        else:
            logger.warning("watchdog fehlt - nutze Polling alle %.1fs", self.interval)
            self._thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread.start()

    def _start_watchdog(self):
        self._observer = Observer()
        self._observer.schedule(_Handler(self.on_file), str(self.watch_dir), recursive=False)
        self._observer.daemon = True
        self._observer.start()
        logger.info("watchdog beobachtet %s", self.watch_dir)

    def _poll_loop(self):
        seen = {}
        while not self._stop.is_set():
            try:
                for path in self.watch_dir.iterdir():
                    if not _matches(path):
                        continue
                    stat = path.stat()
                    key = (path, stat.st_mtime, stat.st_size)
                    if key not in seen:
                        seen.clear()
                        seen[key] = True
                        self.on_file(path, "created")
            except OSError:
                pass
            self._stop.wait(self.interval)

    def stop(self):
        self._stop.set()
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=2)
        if self._thread is not None:
            self._thread.join(timeout=2)