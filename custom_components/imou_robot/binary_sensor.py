from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from .const import *
from .entity import ImouEntity


async def async_setup_entry(hass, entry, add):
    s = hass.data[DOMAIN][entry.entry_id]
    c, i, d = s["coord"], s["imou"], entry
    add([Mop(c, i, d), Charging(c, i, d), Online(c, i, d)])


class Mop(ImouEntity, BinarySensorEntity):
    _attr_icon = "mdi:water-pump"

    def __init__(self, c, i, d):
        super().__init__(c, i, d, "mop", "Mop attached")

    @property
    def is_on(self):
        v = self._v(P_MOP)
        return None if v is None else str(v).lower() in ("1", "true")


class Charging(ImouEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def __init__(self, c, i, d):
        super().__init__(c, i, d, "charging", "Charging")

    @property
    def is_on(self):
        try:
            return int(self._v(P_BATTERY)) < 0   # negative battery value = charging
        except (TypeError, ValueError):
            return None


class Online(ImouEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, c, i, d):
        super().__init__(c, i, d, "online", "Cloud connection")

    @property
    def is_on(self):
        return self.coordinator.data.get("_status") == "online"
