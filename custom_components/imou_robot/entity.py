import asyncio
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN


def device_info(entry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.data["device_id"])},
        name=entry.data.get("name") or "Imou robot vacuum",
        manufacturer="Imou",
        model=entry.data.get("model") or "RV-L11-A",
        serial_number=entry.data["device_id"],
    )


class ImouEntity(CoordinatorEntity):
    """Base class: groups every entity under one device and refreshes shortly after a command."""
    _attr_has_entity_name = True

    def __init__(self, coord, imou, entry, key, name):
        super().__init__(coord)
        self._imou = imou
        self._attr_name = name
        self._attr_unique_id = f"imou_{entry.data['device_id']}_{key}"
        self._attr_device_info = device_info(entry)

    def _v(self, ref):
        return self.coordinator.data.get(str(ref))

    async def _set(self, props):
        await self._imou.set(props)
        await self.coordinator.async_request_refresh()
        self.hass.async_create_task(self._later())   # the cloud reports the new state a few seconds later

    async def _later(self):
        for d in (4, 12):
            await asyncio.sleep(d)
            await self.coordinator.async_request_refresh()
