from __future__ import annotations

from datetime import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util import dt as dt_util

from .entity import KesintiEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([KesintiTakvim(entry.runtime_data, "takvim")])


def _olay(k) -> CalendarEvent:
    yer = "sokağın listede" if k.seviye == "kesin" else "mahallede, sokak belirtilmemiş"
    return CalendarEvent(
        start=k.baslangic, end=k.bitis,
        summary=f"⚡ Elektrik kesintisi ({'kesin' if k.seviye == 'kesin' else 'olası'})",
        description=f"{k.neden}\n{k.mahalle}: {k.sokaklar or '-'} ({yer})",
        location=k.mahalle, uid=f"{k.baslangic.isoformat()}_{k.mahalle}",
    )


class KesintiTakvim(KesintiEntity, CalendarEntity):
    @property
    def event(self) -> CalendarEvent | None:
        simdi = dt_util.now()
        k = next((k for k in self.coordinator.ilgili if k.bitis > simdi), None)
        return _olay(k) if k else None

    async def async_get_events(self, hass, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        return [_olay(k) for k in self.coordinator.ilgili if k.bitis > start_date and k.baslangic < end_date]
