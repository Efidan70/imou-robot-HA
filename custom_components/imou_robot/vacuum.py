from homeassistant.components.vacuum import StateVacuumEntity, VacuumEntityFeature
from .const import *
from .entity import ImouEntity

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


class ImouVacuum(ImouEntity, StateVacuumEntity):
    _attr_supported_features = FEATURES
    _attr_fan_speed_list = list(FAN)

    def __init__(self, coord, imou, entry):
        super().__init__(coord, imou, entry, "vacuum", None)   # main entity of the device: no suffix
        self._attr_unique_id = f"imou_{entry.data['device_id']}"  # keep the id used by earlier versions

    def _st(self):
        try:
            return STATUS.get(int(self._v(P_STATUS)), "idle")
        except (TypeError, ValueError):
            return "idle"

    if NEW:
        @property
        def activity(self):
            return ACT[self._st()]
    else:
        @property
        def state(self):
            return self._st()

    @property
    def fan_speed(self):
        v = self._v(P_FAN)
        if v is None:
            return None
        return min(FAN, key=lambda k: abs(FAN[k] - int(v)))

    @property
    def extra_state_attributes(self):
        return {"cleaned_area_m2": self._v(P_AREA), "cleaning_time_min": self._v(P_TIME),
                "water_level": self._v(P_WATER)}

    async def async_start(self):
        await self._set({P_HOME: True})

    async def async_pause(self):
        await self._set({P_HOME: False})

    async def async_stop(self, **kw):
        await self._set({P_HOME: False})

    async def async_return_to_base(self, **kw):
        await self._set({P_DOCK: True})

    async def async_set_fan_speed(self, fan_speed, **kw):
        await self._set({P_FAN: FAN[fan_speed]})
