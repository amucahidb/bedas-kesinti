"""BEDAŞ'ı 3 saatte bir sorgulayan veri koordinatörü."""
from __future__ import annotations

import logging

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_ILCE, CONF_MAHALLE, CONF_OLASI, CONF_SOKAKLAR, DOMAIN, REFERER, SCAN_INTERVAL, SEVIYE_KESIN, URL
from .parser import Kesinti, ilce_sorgu, suz

_LOGGER = logging.getLogger(__name__)


async def bedas_sorgula(session: aiohttp.ClientSession, ilce: str) -> list:
    """Bir ilçenin tüm planlı kesintilerini döndürür (ham liste)."""
    async with session.post(
        URL,
        data={"countryName": "İSTANBUL", "cityName": ilce_sorgu(ilce)},
        headers={"X-Requested-With": "XMLHttpRequest", "Referer": REFERER},
        timeout=aiohttp.ClientTimeout(total=30),
    ) as resp:
        resp.raise_for_status()
        veri = await resp.json(content_type=None)
    if not isinstance(veri, list):
        raise ValueError("BEDAŞ beklenmeyen yanıt verdi")
    return veri


def ayarlar(entry: ConfigEntry) -> dict:
    """Kurulum + seçenekler birleşimi (seçenekler önceliklidir)."""
    return {**entry.data, **entry.options}


def sokak_listesi(metin: str) -> list[str]:
    return [s.strip() for s in (metin or "").split(",") if s.strip()]


class KesintiCoordinator(DataUpdateCoordinator[list[Kesinti]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL, config_entry=entry)
        self.ilce_kayit = 0

    async def _async_update_data(self) -> list[Kesinti]:
        a = ayarlar(self.config_entry)
        try:
            ham = await bedas_sorgula(async_get_clientsession(self.hass), a[CONF_ILCE])
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"BEDAŞ sorgusu başarısız: {err}") from err
        self.ilce_kayit = len(ham)
        return suz(ham, a[CONF_MAHALLE], sokak_listesi(a.get(CONF_SOKAKLAR, "")))

    @property
    def ilgili(self) -> list[Kesinti]:
        """Bildirim ayarına göre: 'olası' kapalıysa sadece kesin olanlar."""
        if ayarlar(self.config_entry).get(CONF_OLASI, True):
            return list(self.data or [])
        return [k for k in (self.data or []) if k.seviye == SEVIYE_KESIN]
