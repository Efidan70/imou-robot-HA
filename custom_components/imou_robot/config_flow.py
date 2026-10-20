import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import ImouApi, ImouError
from .const import DOMAIN, DEFAULT_URL

class FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            api = ImouApi(async_get_clientsession(self.hass), user_input["base_url"], user_input["app_id"], user_input["app_secret"])
            try:
                await api.token()
                return self.async_create_entry(title=f"Imou {user_input['device_id']}", data=user_input)
            except (ImouError, Exception):
                errors["base"] = "auth"
        schema = vol.Schema({vol.Required("app_id"): str, vol.Required("app_secret"): str,
                             vol.Required("device_id", default="LCL25592022040002533"): str,
                             vol.Required("base_url", default=DEFAULT_URL): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
