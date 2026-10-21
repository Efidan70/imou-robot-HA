from homeassistant.components.vacuum import StateVacuumEntity, VacuumEntityFeature
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import *

try:  # HA 2025.1+
    from homeassistant.components.vacuum import VacuumActivity
    ACT = {"idle": VacuumActivity.IDLE, "paused": VacuumActivity.PAUSED, "returning": VacuumActivity.RETURNING,
           "docked": VacuumActivity.DOCKED, "cleaning": VacuumActivity.CLEANING, "error": VacuumActivity.ERROR}
    NEW = True
except ImportError:
    NEW = False

FEATURES = VacuumEntityFeature(0)
for _n in ("START", "PAUSE", "STOP", "RETURN_HOME", "STATE", "FAN_SPEED"):
    if hasattr(VacuumEntityFeature, _n):
        FEATURES |= getattr(VacuumEntityFeature, _n)
FAN = {"quiet": 25, "standard": 50, "strong": 75, "max": 100}


async def async_setup_entry(hass, entry, add):
    s = hass.data[DOMAIN][entry.entry_id]
    add([ImouVacuum(s["coord"], s["imou"], entry)])


class ImouVacuum(CoordinatorEntity, StateVacuumEntity):
    _attr_name = "Imou robot"
    _attr_supported_features = FEATURES
    _attr_fan_speed_list = list(FAN)

    def __init__(self, coord, imou, entry):
        super().__init__(coord)
        self._imou = imou
        self._attr_unique_id = f"imou_{entry.data['device_id']}"

    def _st(self):
        try:
            return STATUS.get(int(self.coordinator.data.get(P_STATUS)), "idle")
        except (TypeError, ValueError):
            return "idle"

    if NEW:
        @property
        def activity(self):
            return ACT[self._st()]
    else:
        @property
        def state(self):
            return {"cleaning": "cleaning", "docked": "docked", "returning": "returning",
                    "paused": "paused", "error": "error"}.get(self._st(), "idle")

    @property
    def fan_speed(self):
        v = self.coordinator.data.get(P_FAN)
        if v is None:
            return None
        return min(FAN, key=lambda k: abs(FAN[k] - int(v)))

    @property
    def extra_state_attributes(self):
        d = self.coordinator.data
        return {"clean_area_m2": d.get(P_AREA), "clean_time_min": d.get(P_TIME),
                "water_level": d.get(P_WATER), "cloud_status": d.get("_status"),
                "raw_work_status": d.get(P_STATUS), "home_switch": d.get(P_HOME)}

    async def _set(self, props):
        await self._imou.set(props)
        await self.coordinator.async_request_refresh()

    async def async_start(self):
        await self._set({P_HOME: True})  # app home-screen clean switch (to be verified)

    async def async_pause(self):
        await self._set({P_HOME: False})

    async def async_stop(self, **kw):
        await self._set({P_HOME: False})

    async def async_return_to_base(self, **kw):
        await self._set({P_DOCK: True})

    async def async_set_fan_speed(self, fan_speed, **kw):
        await self._set({P_FAN: FAN[fan_speed]})
