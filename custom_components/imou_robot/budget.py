"""Counts Imou API calls per calendar month and keeps polling inside a monthly budget."""
import calendar
from datetime import datetime
from homeassistant.helpers.storage import Store

SAVE_EVERY = 10   # persist the counter every N calls (and on unload)


class Budget:
    def __init__(self, hass, entry_id, budget):
        self._store = Store(hass, 1, f"imou_robot_calls_{entry_id}")
        self.budget = int(budget)
        self.month, self.calls, self._unsaved = self._key(), 0, 0

    @staticmethod
    def _key(now=None):
        n = now or datetime.now()
        return f"{n.year}-{n.month:02d}"

    async def load(self):
        data = await self._store.async_load() or {}
        if data.get("month") == self._key():
            self.calls = int(data.get("calls", 0))

    def count(self):
        """Called for every HTTP request to the Imou cloud."""
        if self.month != self._key():            # new month: quota resets
            self.month, self.calls = self._key(), 0
        self.calls += 1
        self._unsaved += 1
        if self._unsaved >= SAVE_EVERY:
            self.save()

    def save(self):
        self._unsaved = 0
        self._store.async_delay_save(lambda: {"month": self.month, "calls": self.calls}, 5)

    @property
    def percent(self):
        return round(100 * self.calls / self.budget, 1) if self.budget else 0

    def floor_interval(self, now=None):
        """Smallest interval (s) that still spreads the remaining calls over the rest of the month."""
        n = now or datetime.now()
        days = calendar.monthrange(n.year, n.month)[1]
        left = (days - n.day + 1) * 86400 - (n.hour * 3600 + n.minute * 60 + n.second)
        remaining = self.budget - self.calls
        if remaining <= 0:
            return 3600                          # budget used up: one check per hour
        return max(1, left / remaining)
