import logging, json
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import ImouApi
from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    d = entry.data
    api = ImouApi(async_get_clientsession(hass), d["base_url"], d["app_id"], d["app_secret"])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = api

    async def dump(call):
        """Log device info, product model and current properties (service imou_robot.dump)."""
        dev = await api.device(d["device_id"])
        _LOGGER.warning("IMOU DEVICE: %s", json.dumps(dev, ensure_ascii=False))
        pid = dev.get("productId")
        if pid:
            _LOGGER.warning("IMOU MODEL: %s", json.dumps(await api.model(pid), ensure_ascii=False))
    async def setp(call):
        dev = await api.device(d["device_id"])
        await api.set_props(dev["productId"], d["device_id"], call.data["properties"])
    hass.services.async_register(DOMAIN, "dump", dump)
    hass.services.async_register(DOMAIN, "set_properties", setp)
    return True

async def async_unload_entry(hass, entry):
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
