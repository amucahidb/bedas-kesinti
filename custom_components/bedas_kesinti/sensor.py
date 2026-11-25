from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.util import dt as dt_util

from .entity import KesintiEntity


async def async_setup_entry(hass, entry, async_add_entities):
    c = entry.runtime_data
    async_add_entities([SiradakiSensor(c, "siradaki"), AdetSensor(c, "adet")])


class SiradakiSensor(KesintiEntity, SensorEntity):
    """Sıradaki (ya da süren) kesintinin başlangıcı."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:transmission-tower-off"

    def _ilk(self):
        simdi = dt_util.now()
        return next((k for k in self.coordinator.ilgili if k.bitis > simdi), None)

    @property
    def native_value(self):
        k = self._ilk()
        return k.baslangic if k else None

    @property
    def extra_state_attributes(self):
        k = self._ilk()
        if not k:
            return {"ozet": "Planlı kesinti yok"}
        yer = "Sokağın listede" if k.seviye == "kesin" else "Mahallede (sokak belirtilmemiş)"
        return {**k.as_dict(), "ozet": f"{k.baslangic:%d.%m %H:%M}–{k.bitis:%H:%M} · {yer} · {k.neden}"}


class AdetSensor(KesintiEntity, SensorEntity):
    """Adresi etkileyen bitmemiş kesinti sayısı; ayrıntılar öznitelikte."""

    _attr_icon = "mdi:format-list-numbered"
    _attr_native_unit_of_measurement = "kesinti"

    @property
    def native_value(self):
        return len(self.coordinator.ilgili)

    @property
    def extra_state_attributes(self):
        return {"kesintiler": [k.as_dict() for k in self.coordinator.data or []][:10],
                "ilce_kayit": self.coordinator.ilce_kayit}
