from __future__ import annotations

from datetime import datetime, timezone
from threading import Event, Lock, Thread
from typing import Any

from .service import run_pipeline


class SchedulerService:
    def __init__(self, interval_minutes: int = 60, max_per_source: int = 10) -> None:
        self.interval_minutes = interval_minutes
        self.max_per_source = max_per_source
        self.running = False
        self._thread: Thread | None = None
        self._stop_event = Event()
        self._lock = Lock()
        self._last_started_at: str | None = None
        self._last_finished_at: str | None = None
        self._last_error: str | None = None

    def start(self) -> None:
        with self._lock:
            if self.running:
                return
            self.running = True
            self._stop_event.clear()
            self._thread = Thread(target=self._loop, daemon=True, name="blog-kb-scheduler")
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            if not self.running:
                return
            self.running = False
            self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def trigger_once(self) -> None:
        self._run_job()

    def describe_jobs(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "pipeline",
                "interval_minutes": self.interval_minutes,
                "max_per_source": self.max_per_source,
                "last_started_at": self._last_started_at,
                "last_finished_at": self._last_finished_at,
                "last_error": self._last_error,
            }
        ]

    def _loop(self) -> None:
        while not self._stop_event.wait(timeout=self.interval_minutes * 60):
            self._run_job()

    def _run_job(self) -> None:
        self._last_started_at = datetime.now(timezone.utc).isoformat()
        self._last_error = None
        try:
            run_pipeline(max_per_source=self.max_per_source)
        except Exception as exc:
            self._last_error = str(exc)
        finally:
            self._last_finished_at = datetime.now(timezone.utc).isoformat()


_SCHEDULER: SchedulerService | None = None


def get_scheduler_service() -> SchedulerService:
    global _SCHEDULER
    if _SCHEDULER is None:
        _SCHEDULER = SchedulerService()
    return _SCHEDULER
