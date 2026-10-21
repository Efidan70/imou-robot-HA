import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import ImouApi, ImouError
from .const import (DOMAIN, DATACENTERS, CONF_IDLE, CONF_ACTIVE, DEFAULT_IDLE, DEFAULT_ACTIVE)


class FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._creds, self._devices = {}, []

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return OptionsFlow()

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            url = DATACENTERS[user_input["datacenter"]]
            api = ImouApi(async_get_clientsession(self.hass), url, user_input["app_id"].strip(), user_input["app_secret"].strip())
            try:
                await api.token()
            except ImouError:
                errors["base"] = "invalid_auth"
            except Exception:  # network problems
                errors["base"] = "cannot_connect"
            else:
                self._creds = {"app_id": user_input["app_id"].strip(), "app_secret": user_input["app_secret"].strip(), "base_url": url}
                try:
                    self._devices = [d for d in await api.list_devices() if d.get("productId")]
                except Exception:
                    self._devices = []
                return await self.async_step_device()
        schema = vol.Schema({
            vol.Required("app_id"): str,
            vol.Required("app_secret"): selector.TextSelector(selector.TextSelectorConfig(type="password")),
            vol.Required("datacenter", default="fk"): selector.SelectSelector(selector.SelectSelectorConfig(
                options=[{"value": "fk", "label": "Europe (Frankfurt)"}, {"value": "sg", "label": "Asia (Singapore)"},
                         {"value": "or", "label": "Americas (Oregon)"}], mode="dropdown")),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_device(self, user_input=None):
        errors = {}
        if user_input:
            did = user_input["device_id"].strip()
            await self.async_set_unique_id(did)
            self._abort_if_unique_id_configured()
            info = next((d for d in self._devices if d.get("deviceId") == did), {})
            data = dict(self._creds, device_id=did, name=info.get("name") or "Imou robot vacuum",
                        model=info.get("deviceModel") or "RV-L11-A")
            return self.async_create_entry(title=data["name"], data=data)
        if self._devices:   # pick from the account's devices
            opts = [{"value": d["deviceId"], "label": f"{d.get('name') or 'Device'} ({d['deviceId']})"} for d in self._devices]
            field = selector.SelectSelector(selector.SelectSelectorConfig(options=opts, mode="dropdown"))
        else:               # listing failed: type the serial number
            field = str
        return self.async_show_form(step_id="device", data_schema=vol.Schema({vol.Required("device_id"): field}), errors=errors)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        errors = {}
        entry = self._get_reauth_entry()
        if user_input:
            api = ImouApi(async_get_clientsession(self.hass), entry.data["base_url"], user_input["app_id"].strip(), user_input["app_secret"].strip())
            try:
                await api.token()
            except ImouError:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(entry, data_updates={"app_id": user_input["app_id"].strip(), "app_secret": user_input["app_secret"].strip()})
        schema = vol.Schema({vol.Required("app_id", default=entry.data["app_id"]): str,
                             vol.Required("app_secret"): selector.TextSelector(selector.TextSelectorConfig(type="password"))})
        return self.async_show_form(step_id="reauth_confirm", data_schema=schema, errors=errors)


class OptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        o = self.config_entry.options
        schema = vol.Schema({
            vol.Required(CONF_IDLE, default=o.get(CONF_IDLE, DEFAULT_IDLE)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=60, max=900, step=10, unit_of_measurement="s", mode="box")),
            vol.Required(CONF_ACTIVE, default=o.get(CONF_ACTIVE, DEFAULT_ACTIVE)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=10, max=120, step=5, unit_of_measurement="s", mode="box")),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
