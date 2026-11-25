from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.util import dt as dt_util

from .entity import KesintiEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([SuAnSensor(entry.runtime_data, "su_an")])


class SuAnSensor(KesintiEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:flash-off"

    @property
    def is_on(self) -> bool:
        simdi = dt_util.now()
        return any(k.baslangic <= simdi < k.bitis for k in self.coordinator.ilgili)
