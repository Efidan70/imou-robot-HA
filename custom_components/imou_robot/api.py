"""Minimal Imou Open API client."""
import base64, hashlib, hmac, time, uuid
from aiohttp import ClientSession

def calc_sign(t, nonce, secret):
    """sign = Base64(HMAC-SHA256(template, hex(SHA256(secret))))."""
    password = hashlib.sha256(secret.encode()).hexdigest()
    template = f"time:{t},nonce:{nonce},appSecret:{secret}"
    return base64.b64encode(hmac.new(password.encode(), template.encode(), hashlib.sha256).digest()).decode()

class ImouError(Exception):
    pass

class ImouApi:
    def __init__(self, session: ClientSession, base_url, app_id, app_secret):
        self._s, self._url, self._id, self._secret = session, base_url.rstrip("/"), app_id, app_secret
        self._token, self._exp = None, 0

    def _system(self):
        t = int(time.time()); n = uuid.uuid4().hex
        return {"ver": "1.0", "appId": self._id, "sign": calc_sign(t, n, self._secret), "time": t, "nonce": n}

    async def call(self, method, params=None):
        body = {"system": self._system(), "id": uuid.uuid4().hex, "params": params or {}}
        async with self._s.post(f"{self._url}/openapi/{method}", json=body, timeout=20) as r:
            data = await r.json(content_type=None)
        res = data.get("result", {})
        if res.get("code") != "0":
            raise ImouError(f"{method}: {res.get('code')} {res.get('msg')}")
        return res.get("data", {})

    async def token(self):
        if not self._token or time.time() > self._exp:
            d = await self.call("accessToken")
            self._token = d["accessToken"]; self._exp = time.time() + int(d.get("expireTime", 3600)) - 60
        return self._token

    async def authed(self, method, params=None):
        p = {"token": await self.token()}; p.update(params or {})
        return await self.call(method, p)

    async def device(self, device_id):
        d = await self.authed("listDeviceDetailsByIds", {"deviceList": [{"deviceId": device_id, "channelList": [0]}]})
        return (d.get("deviceList") or [{}])[0]

    async def model(self, product_id):
        return await self.authed("getProductModel", {"productId": product_id})

    async def get_props(self, product_id, device_id, refs):
        return await self.authed("getIotDeviceProperties", {"productId": product_id, "deviceId": device_id, "properties": refs})

    async def set_props(self, product_id, device_id, props):
        return await self.authed("setIotDeviceProperties", {"productId": product_id, "deviceId": device_id, "properties": props})

    async def control(self, product_id, device_id, ref, content=None):
        return await self.authed("iotDeviceControl", {"productId": product_id, "deviceId": device_id,
                                                      "ref": str(ref), "content": content or {}})

    async def list_devices(self):
        """Devices bound to the account (IoT devices have a productId)."""
        d = await self.authed("listDeviceDetailsByPage",
                              {"bindId": -1, "limit": 50, "type": "bindAndShare", "needApInfo": False})
        return d.get("deviceList") or []
