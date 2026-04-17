"""Utilities for cron-based scheduling."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Awaitable, Callable

LOG = logging.getLogger(__name__)

try:
    from croniter import croniter  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    croniter = None


class CronScheduler:
    """Run an async callback according to a cron expression."""

    def __init__(self, cron_expression: str, callback: Callable[[], Awaitable[None]]) -> None:
        self.cron_expression = cron_expression
        self.callback = callback
        self._running = False

    async def run(self) -> None:
        self._running = True

        if croniter is not None:
            iterator = croniter(self.cron_expression, datetime.now())
            while self._running:
                next_run = iterator.get_next(datetime)
                delay = max(0.0, (next_run - datetime.now()).total_seconds())
                await self._sleep_and_execute(delay)
            return

        # Fallback for environments missing croniter (keeps bot functional in tests).
        LOG.warning("croniter is not installed; using 60s fallback schedule")
        while self._running:
            await self._sleep_and_execute(60.0)

    async def _sleep_and_execute(self, delay: float) -> None:
        try:
            await asyncio.sleep(delay)
            if self._running:
                await self.callback()
        except asyncio.CancelledError:
            self._running = False
            raise
        except Exception as exc:  # keep scheduler alive
            LOG.error("Cron callback failed: %s", exc)

    def stop(self) -> None:
        self._running = False
