from hashlib import sha256

from zoneramaapi.zeep.async_ import ZeepAsyncClients
from zoneramaapi.zeep.common import AsyncServiceProxy


class ZoneramaAsyncClient:
    _zeep: ZeepAsyncClients
    logged_in_as: int | None

    def __init__(self):
        self._zeep = ZeepAsyncClients()

    async def __aenter__(self):
        await self._zeep.__aenter__()
        return self

    async def __aexit__(self, *_):
        await self.close()
        return

    async def close(self):
        if self.logged_in:
            await self.logout()
        await self._zeep.close()

    async def login(self, username: str, password: str) -> bool:
        service = self._zeep.api.service
        response = await service.Login(
            username, sha256(bytes(password, "utf-8")).hexdigest()
        )
        self.logged_in_as = response.Result if response.Success else None
        return response.Success

    async def logout(self) -> bool:
        if not self.logged_in:
            return False

        service = self._zeep.api.service
        response = await service.Logout()

        if response.Success:
            self.logged_in_as = None

        return response.Success

    @property
    def logged_in(self) -> bool:
        return self.logged_in_as is not None

    @property
    def _api_service(self) -> AsyncServiceProxy:
        return self._zeep.api.service  # type: ignore

    @property
    def _data_service(self) -> AsyncServiceProxy:
        return self._zeep.data.service  # type: ignore
