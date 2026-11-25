"""Kurulum ekranı: ilçe, mahalle, sokak(lar) ve 'olası' bildirim tercihi."""
from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_ILCE, CONF_MAHALLE, CONF_OLASI, CONF_SOKAKLAR, DOMAIN
from .coordinator import bedas_sorgula
from .parser import norm


def _sema(v: dict) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_ILCE, default=v.get(CONF_ILCE, "")): str,
        vol.Required(CONF_MAHALLE, default=v.get(CONF_MAHALLE, "")): str,
        vol.Optional(CONF_SOKAKLAR, default=v.get(CONF_SOKAKLAR, "")): str,
        vol.Required(CONF_OLASI, default=v.get(CONF_OLASI, True)): bool,
    })


class BedasKesintiConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        hatalar = {}
        if user_input is not None:
            anahtar = "_".join(norm(user_input[CONF_ILCE]) + norm(user_input[CONF_MAHALLE])
                               + norm(user_input.get(CONF_SOKAKLAR, "")))
            await self.async_set_unique_id(anahtar.lower())
            self._abort_if_unique_id_configured()
            try:
                await bedas_sorgula(async_get_clientsession(self.hass), user_input[CONF_ILCE])
            except (aiohttp.ClientError, TimeoutError, ValueError):
                hatalar["base"] = "baglanti"
            else:
                return self.async_create_entry(
                    title=f"{user_input[CONF_MAHALLE].strip()} / {user_input[CONF_ILCE].strip()}", data=user_input)
        return self.async_show_form(step_id="user", data_schema=_sema(user_input or {}), errors=hatalar)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return BedasKesintiOptionsFlow()


class BedasKesintiOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        mevcut = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_sema(mevcut))
