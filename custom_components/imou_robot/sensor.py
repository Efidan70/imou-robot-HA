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
    c, i, d = s["coord"], s["imou"], entry.data["device_id"]
    E = EntityCategory.DIAGNOSTIC
    add([
        ImouSensor(c, i, d, "battery", "Imou battery", P_BATTERY, "%", SensorDeviceClass.BATTERY, lambda v: abs(_int(v)) if _int(v) is not None else None),
        ImouSensor(c, i, d, "area", "Imou clean area", P_AREA, "m\u00b2", None, _int),
        ImouSensor(c, i, d, "time", "Imou clean time", P_TIME, "min", None, _int),
        ImouSensor(c, i, d, "status", "Imou status", P_STATUS, None, None, lambda v: STATUS_TEXT.get(_int(v), v)),
        ImouSensor(c, i, d, "wifi", "Imou wifi signal", P_WIFI, None, None, lambda v: WIFI_TEXT.get(_int(v), v), E),
        ImouSensor(c, i, d, "side_brush", "Imou side brush hours", "12202", "h", None, _int, E),
        ImouSensor(c, i, d, "main_brush", "Imou main brush hours", "12204", "h", None, _int, E),
        ImouSensor(c, i, d, "dust_box", "Imou dust box/filter hours", "12206", "h", None, _int, E),
        ImouSensor(c, i, d, "sensors", "Imou sensor hours", "12208", "h", None, _int, E),
        ImouSensor(c, i, d, "error", "Imou error code", "40501", None, None, lambda v: v, E),
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
