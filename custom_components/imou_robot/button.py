from homeassistant.components.button import ButtonEntity
from .const import *
from .entity import ImouEntity


async def async_setup_entry(hass, entry, add):
    s = hass.data[DOMAIN][entry.entry_id]
    c, i, d = s["coord"], s["imou"], entry
    # thing-model services; the call format is based on the Imou docs but unverified (experimental)
    add([ImouButton(c, i, d, "locate", "Locate robot", "20400", "mdi:map-marker"),
         ImouButton(c, i, d, "empty_dust", "Empty dust bin", "2300", "mdi:delete-empty")])


class ImouButton(ImouEntity, ButtonEntity):
    def __init__(self, c, i, did, key, name, ref, icon):
        super().__init__(c, i, did, key, name)
        self._ref, self._attr_icon = ref, icon

    async def async_press(self):
        await self._imou.control(self._ref)
