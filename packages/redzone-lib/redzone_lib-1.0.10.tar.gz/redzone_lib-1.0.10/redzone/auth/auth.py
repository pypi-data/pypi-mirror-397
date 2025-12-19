from fastapi import Request
from fastapi.security import HTTPBearer

from ..exceptions.auth_exceptions import NotAuthenticated, NotAuthorized
from ..services.auth_service import AuthService


class Auth(HTTPBearer):
    def __init__(self, *allowed_scopes: str | list) -> None:
        super().__init__()
        self.allowed_scopes: tuple = allowed_scopes

    async def __call__(self, request: Request) -> None:
        authorization = request.headers.get("Authorization", "")

        try:
            token_type, token = authorization.split()
        except ValueError:
            raise NotAuthenticated()

        if token_type != "Bearer":
            raise NotAuthenticated()

        introspect_response = await AuthService().introspect(token)

        if introspect_response.status_code != 200:
            raise NotAuthenticated()

        token_scopes = introspect_response.data.get("scope", "").split()

        organization_id = request.path_params.get("organization_id", None)

        for allowed_scope in self.allowed_scopes:
            if isinstance(allowed_scope, str):
                if self.scope_match(allowed_scope, token_scopes, organization_id):
                    return
            elif isinstance(allowed_scope, list):
                if all(self.scope_match(scope, token_scopes, organization_id) for scope in allowed_scope):
                    return

        raise NotAuthorized()

    @staticmethod
    def scope_match(allowed_scope: str, token_scopes: set[str], organization_id=None) -> bool:
        # resolve {organization_id} in scope
        if organization_id:
            allowed_scope = allowed_scope.replace("{organization_id}", organization_id)

        # allow * to match any organization id
        allowed_scope = allowed_scope.replace("*", "")

        # check if any token scope starts with the allowed scope
        for token_scope in token_scopes:
            if token_scope.startswith(allowed_scope):
                return True

        return False
