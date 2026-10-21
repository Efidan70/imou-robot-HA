from homeassistant.components.number import NumberEntity
from homeassistant.const import EntityCategory
from .const import *
from .entity import ImouEntity


async def async_setup_entry(hass, entry, add):
    s = hass.data[DOMAIN][entry.entry_id]
    c, i, d = s["coord"], s["imou"], entry
    add([ImouNumber(c, i, d, "water", "Water level", P_WATER, "mdi:water"),
         ImouNumber(c, i, d, "suction", "Suction power", P_FAN, "mdi:fan"),
         ImouNumber(c, i, d, "volume", "Voice volume", P_VOLUME, "mdi:volume-high", EntityCategory.CONFIG)])


class ImouNumber(ImouEntity, NumberEntity):
    _attr_native_min_value, _attr_native_max_value, _attr_native_step = 0, 100, 1

    def __init__(self, c, i, did, key, name, ref, icon, cat=None):
        super().__init__(c, i, did, key, name)
        self._ref, self._attr_icon, self._attr_entity_category = ref, icon, cat

    @property
    def native_value(self):
        v = self._v(self._ref)
        return None if v is None else int(v)

    async def async_set_native_value(self, value):
        await self._set({self._ref: int(value)})
