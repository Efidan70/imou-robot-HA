import json, logging
from datetime import timedelta
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import ImouApi
from .const import DOMAIN, PROP_REFS, ACTIVE, P_STATUS

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["vacuum", "sensor", "number", "switch", "binary_sensor", "button"]


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
        for k, v in list(data.items()):          # flatten struct values (life, DND, error info)
            if isinstance(v, str) and v.startswith("{"):
                try:
                    v = json.loads(v)
                    data[k] = v
                except ValueError:
                    pass
            if isinstance(v, dict):
                for kk, vv in v.items():
                    data[str(kk)] = vv
        data["_status"] = res.get("status")
        return data

    async def set(self, props):
        pid = await self.ensure_product()
        return await self.api.set_props(pid, self.device_id, props)

    async def control(self, ref, content=None):
        pid = await self.ensure_product()
        return await self.api.control(pid, self.device_id, ref, content)


async def async_setup_entry(hass, entry):
    d = entry.data
    api = ImouApi(async_get_clientsession(hass), d["base_url"], d["app_id"], d["app_secret"])
    imou = ImouData(api, d["device_id"])
    coord = DataUpdateCoordinator(
        hass, _LOGGER, name=DOMAIN, update_method=imou.fetch,
        update_interval=timedelta(seconds=120))  # keeps within 30,000 free API calls/month
    inner = imou.fetch

    async def adaptive():
        data = await inner()
        try:   # poll faster while the robot is active, slow when idle (API quota: 30,000 calls/month)
            active = int(data.get(P_STATUS)) in ACTIVE
        except (TypeError, ValueError):
            active = False
        coord.update_interval = timedelta(seconds=30 if active else 120)
        return data

    coord.update_method = adaptive
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

    async def read_props(call):
        """Log arbitrary property refs (service imou_robot.read_properties, e.g. refs: ['40100','1025'])."""
        pid = await imou.ensure_product()
        res = await api.get_props(pid, d["device_id"], [str(r) for r in call.data["refs"]])
        _LOGGER.warning("IMOU PROPS: %s", json.dumps(res, ensure_ascii=False))

    hass.services.async_register(DOMAIN, "dump", dump)
    hass.services.async_register(DOMAIN, "read_properties", read_props)
    hass.services.async_register(DOMAIN, "set_properties", setp)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
