from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from .const import *
from .entity import ImouEntity


async def async_setup_entry(hass, entry, add):
    s = hass.data[DOMAIN][entry.entry_id]
    c, i, d = s["coord"], s["imou"], entry
    add([ImouSwitch(c, i, d, "light", "Indicator light", P_LIGHT, P_LIGHT, "mdi:led-on"),
         ImouSwitch(c, i, d, "keep_clean", "Resume cleaning after charging", P_KEEP, P_KEEP, "mdi:restart"),
         ImouSwitch(c, i, d, "auto_dust", "Auto empty dust bin", P_DUST, P_DUST, "mdi:delete-empty"),
         ImouSwitch(c, i, d, "rug_press", "Carpet boost", P_RUG, P_RUG, "mdi:rug"),
         # struct property: the exact write format is unverified (experimental)
         ImouSwitch(c, i, d, "dnd", "Do not disturb", "40201", P_DND, "mdi:sleep", struct="40201")])


class ImouSwitch(ImouEntity, SwitchEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, c, i, did, key, name, read_ref, write_ref, icon, struct=None):
        super().__init__(c, i, did, key, name)
        self._r, self._w, self._attr_icon, self._struct = read_ref, write_ref, icon, struct

    @property
    def is_on(self):
        v = self._v(self._r)
        return None if v is None else str(v).lower() in ("1", "true", "on")

    async def _write(self, on):
        if self._struct:
            await self._set({self._w: {self._struct: on}})
        else:
            await self._set({self._w: on})

    async def async_turn_on(self, **kw):
        await self._write(True)

    async def async_turn_off(self, **kw):
        await self._write(False)
