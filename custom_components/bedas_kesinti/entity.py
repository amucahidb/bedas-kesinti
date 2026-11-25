from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_MAHALLE, DOMAIN
from .coordinator import KesintiCoordinator, ayarlar


class KesintiEntity(CoordinatorEntity[KesintiCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: KesintiCoordinator, anahtar: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{anahtar}"
        self._attr_translation_key = anahtar
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"BEDAŞ Kesinti – {ayarlar(entry)[CONF_MAHALLE]}",
            manufacturer="BEDAŞ (planlı kesinti duyuruları)",
            entry_type=DeviceEntryType.SERVICE,
        )
