from ..services.service import Service
from ..settings import AUTH_SERVICE_URL


class AuthService(Service):
    request_base_url: str = AUTH_SERVICE_URL
    mask_response_data_fields: list = [
        "access_token",
    ]

    async def introspect(self, token: str) -> Service.Response:
        request = self.Request(
            url="/api/v1/auth/introspect",
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
        return await self.invoke(request)

    async def create_access_token_by_client_credentials(self, client_id: str, client_secret: str) -> Service.Response:
        request = self.Request(
            url="/api/v1/auth/token",
            method="POST",
            headers={
                "Content-Type": "application/json",
            },
            json={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        return await self.invoke(request)
