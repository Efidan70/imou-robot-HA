import asyncio
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class ImouEntity(CoordinatorEntity):
    _attr_has_entity_name = False

    def __init__(self, coord, imou, did, key, name):
        super().__init__(coord)
        self._imou = imou
        self._attr_name = name
        self._attr_unique_id = f"imou_{did}_{key}"

    def _v(self, ref):
        return self.coordinator.data.get(str(ref))

    async def _set(self, props):
        await self._imou.set(props)
        await self.coordinator.async_request_refresh()
        # the cloud reports the new state a few seconds later
        self.hass.async_create_task(self._later())

    async def _later(self):
        for d in (4, 12):
            await asyncio.sleep(d)
            await self.coordinator.async_request_refresh()
