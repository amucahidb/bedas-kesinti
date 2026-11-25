"""Kurulum ekranı: ilçe (listeden), mahalle ve sokak(lar) + BEDAŞ duyurularıyla yazım kontrolü."""
from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .const import CONF_ILCE, CONF_MAHALLE, CONF_OLASI, CONF_SOKAKLAR, DOMAIN, ILCELER
from .coordinator import bedas_sorgula
from .parser import ilce_sorgu, mahalle_kontrol, norm

_ILCE_SECICI = SelectSelector(SelectSelectorConfig(options=ILCELER, mode=SelectSelectorMode.DROPDOWN))


def _sema(v: dict) -> vol.Schema:
    ilce = ilce_sorgu(v.get(CONF_ILCE, "")) if v.get(CONF_ILCE) else vol.UNDEFINED
    return vol.Schema({
        vol.Required(CONF_ILCE, default=ilce if ilce in ILCELER else vol.UNDEFINED): _ILCE_SECICI,
        vol.Required(CONF_MAHALLE, default=v.get(CONF_MAHALLE, "")): str,
        vol.Optional(CONF_SOKAKLAR, default=v.get(CONF_SOKAKLAR, "")): str,
        vol.Required(CONF_OLASI, default=v.get(CONF_OLASI, True)): bool,
    })


class BedasKesintiConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._uyarilan: tuple[str, str] | None = None

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        hatalar, oneriler = {}, ""
        if user_input is not None:
            ilce, mah = user_input[CONF_ILCE], user_input[CONF_MAHALLE]
            await self.async_set_unique_id("_".join(norm(ilce) + norm(mah) + norm(user_input.get(CONF_SOKAKLAR, ""))).lower())
            self._abort_if_unique_id_configured()
            try:
                ham = await bedas_sorgula(async_get_clientsession(self.hass), ilce)
            except (aiohttp.ClientError, TimeoutError, ValueError):
                hatalar["base"] = "baglanti"
            else:
                var, benzer = mahalle_kontrol(ham, mah)
                anahtar = (ilce, " ".join(norm(mah)))
                if var or self._uyarilan == anahtar:   # doğru ya da kullanıcı ikinci kez onayladı
                    return self.async_create_entry(title=f"{mah.strip()} / {ilce.title()}", data=user_input)
                self._uyarilan = anahtar
                hatalar[CONF_MAHALLE] = "mahalle_yok"
                oneriler = ", ".join(benzer) if benzer else "—"
        return self.async_show_form(step_id="user", data_schema=_sema(user_input or {}), errors=hatalar,
                                    description_placeholders={"oneriler": oneriler or "—"})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return BedasKesintiOptionsFlow()


class BedasKesintiOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(step_id="init", data_schema=_sema({**self.config_entry.data, **self.config_entry.options}))
