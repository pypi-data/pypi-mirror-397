from ..caches.service_token_cache import ServiceTokenCache
from ..objects.base_object import BaseObject
from ..services.auth_service import AuthService
from ..settings import CLIENT_ID, CLIENT_SECRET


class ServiceToken(BaseObject):
    token: str

    @staticmethod
    async def get() -> "ServiceToken":
        service_token_cache = ServiceTokenCache()
        token = await service_token_cache.get(CLIENT_ID)
        if token:
            return ServiceToken(token=token)

        create_access_token_response = await AuthService().create_access_token_by_client_credentials(CLIENT_ID, CLIENT_SECRET)
        token = create_access_token_response.data["access_token"]

        await service_token_cache.set(CLIENT_ID, token)

        return ServiceToken(token=token)
