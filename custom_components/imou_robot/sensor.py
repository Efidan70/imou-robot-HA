from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory
from .const import *
from .entity import ImouEntity


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


async def async_setup_entry(hass, entry, add):
    s = hass.data[DOMAIN][entry.entry_id]
    c, i, d = s["coord"], s["imou"], entry
    E = EntityCategory.DIAGNOSTIC
    add([
        ImouSensor(c, i, d, "battery", "Battery", P_BATTERY, "%", SensorDeviceClass.BATTERY, lambda v: abs(_int(v)) if _int(v) is not None else None),
        ImouSensor(c, i, d, "area", "Cleaned area", P_AREA, "m\u00b2", None, _int),
        ImouSensor(c, i, d, "time", "Cleaning time", P_TIME, "min", None, _int),
        ImouSensor(c, i, d, "status", "Status", P_STATUS, None, None, lambda v: STATUS_TEXT.get(_int(v), v)),
        ImouSensor(c, i, d, "wifi", "Wi-Fi signal", P_WIFI, None, None, lambda v: WIFI_TEXT.get(_int(v), v), E),
        ImouSensor(c, i, d, "side_brush", "Side brush usage", "12202", "h", None, _int, E),
        ImouSensor(c, i, d, "main_brush", "Main brush usage", "12204", "h", None, _int, E),
        ImouSensor(c, i, d, "dust_box", "Dust box and filter usage", "12206", "h", None, _int, E),
        ImouSensor(c, i, d, "sensors", "Sensors usage", "12208", "h", None, _int, E),
        ImouSensor(c, i, d, "error", "Error code", "40501", None, None, lambda v: v, E),
    ])


class ImouSensor(ImouEntity, SensorEntity):
    def __init__(self, c, i, did, key, name, ref, unit, dclass, conv, cat=None):
        super().__init__(c, i, did, key, name)
        self._ref, self._conv = ref, conv
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = dclass
        self._attr_entity_category = cat
        if unit:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        v = self._v(self._ref)
        return None if v is None else self._conv(v)
