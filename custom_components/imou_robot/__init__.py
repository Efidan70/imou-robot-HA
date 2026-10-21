import json, logging
from datetime import timedelta
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import ImouApi
from .const import DOMAIN, PROP_REFS

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["vacuum"]


class ImouData:
    def __init__(self, api, device_id):
        self.api, self.device_id, self.product_id = api, device_id, None

    async def ensure_product(self):
        if not self.product_id:
            dev = await self.api.device(self.device_id)
            self.product_id = dev.get("productId")
        return self.product_id

    async def fetch(self):
        pid = await self.ensure_product()
        res = await self.api.get_props(pid, self.device_id, PROP_REFS)
        data = dict(res.get("properties") or {})
        data["_status"] = res.get("status")
        return data

    async def set(self, props):
        pid = await self.ensure_product()
        return await self.api.set_props(pid, self.device_id, props)


async def async_setup_entry(hass, entry):
    d = entry.data
    api = ImouApi(async_get_clientsession(hass), d["base_url"], d["app_id"], d["app_secret"])
    imou = ImouData(api, d["device_id"])
    coord = DataUpdateCoordinator(
        hass, _LOGGER, name=DOMAIN, update_method=imou.fetch,
        update_interval=timedelta(seconds=120))  # keeps within 30,000 free API calls/month
    await coord.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"imou": imou, "coord": coord}

    async def dump(call):
        dev = await api.device(d["device_id"])
        _LOGGER.warning("IMOU DEVICE: %s", json.dumps(dev, ensure_ascii=False))
        pid = dev.get("productId")
        if pid:
            _LOGGER.warning("IMOU MODEL: %s", json.dumps(await api.model(pid), ensure_ascii=False))

    async def setp(call):
        await imou.set(call.data["properties"])
        await coord.async_request_refresh()

    hass.services.async_register(DOMAIN, "dump", dump)
    hass.services.async_register(DOMAIN, "set_properties", setp)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
