from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, P_BATTERY, P_AREA, P_TIME


async def async_setup_entry(hass, entry, add):
    coord = hass.data[DOMAIN][entry.entry_id]["coord"]
    did = entry.data["device_id"]
    add([ImouSensor(coord, did, "battery", "Imou battery", P_BATTERY, "%", SensorDeviceClass.BATTERY, True),
         ImouSensor(coord, did, "area", "Imou clean area", P_AREA, "m²", None, False),
         ImouSensor(coord, did, "time", "Imou clean time", P_TIME, "min", None, False)])


class ImouSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coord, did, key, name, ref, unit, dclass, absval):
        super().__init__(coord)
        self._ref, self._abs = ref, absval
        self._attr_name = name
        self._attr_unique_id = f"imou_{did}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = dclass
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        v = self.coordinator.data.get(self._ref)
        if v is None:
            return None
        v = int(v)
        return abs(v) if self._abs else v  # negative battery = charging
