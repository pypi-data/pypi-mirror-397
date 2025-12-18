import os
import uuid
import base64
import hmac
import hashlib
import time
from typing import Dict
from functools import cached_property
import httpx
from .resources.me import Me, AsyncMe
from .resources.workspaces import Workspaces, AsyncWorkspaces
from .resources.organizations import Organizations, AsyncOrganizations
from ._client_base import SyncAPIClient, AsyncAPIClient


class TogglAPI(SyncAPIClient):
    @cached_property
    def me(self) -> Me:
        return Me(self)
    
    @cached_property
    def workspaces(self) -> Workspaces:
        return Workspaces(self)
    
    @cached_property
    def organizations(self) -> Organizations:
        return Organizations(self)
    
    def __init__(
            self,
            api_token: str | None = None,
            base_url: str | httpx.URL | None = None,
            http_client: httpx.Client | None = None
    ) -> None:
        if api_token is None:
            api_token = os.environ.get("TOGGL_API_TOKEN")
        if api_token is None:
            raise Exception("api_token must be specified")
        if base_url is None:
            base_url = os.environ.get("TOGGL_BASE_URL")
        if base_url is None:
            base_url = f"https://api.track.toggl.com/api/v9/"

        super().__init__(
            base_url=base_url,
            http_client=http_client)

        self._api_token = api_token

        
    @property
    def auth_headers(self) -> Dict[str, str]:
        user = self._api_token
        password = 'api_token'
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        return {
            "Authorization": f"Basic {token}",
        }

    @property
    def default_headers(self) -> Dict[str, str]:
        return {
            **super().default_headers
        }


class AsyncTogglAPI(AsyncAPIClient):
    @cached_property
    def me(self) -> AsyncMe:
        return AsyncMe(self)
    
    @cached_property
    def workspaces(self) -> AsyncWorkspaces:
        return AsyncWorkspaces(self)
    
    @cached_property
    def organizations(self) -> AsyncOrganizations:
        return AsyncOrganizations(self)
    
    def __init__(
            self,
            api_token: str | None = None,
            base_url: str | httpx.URL | None = None,
            http_client: httpx.Client | None = None
    ) -> None:
        if api_token is None:
            api_token = os.environ.get("TOGGL_API_TOKEN")
        if api_token is None:
            raise Exception("api_token must be specified")
        if base_url is None:
            base_url = os.environ.get("TOGGL_BASE_URL")
        if base_url is None:
            base_url = f"https://api.track.toggl.com/api/v9/"

        super().__init__(
            base_url=base_url,
            http_client=http_client)

        self._api_token = api_token
        
    @property
    def auth_headers(self) -> Dict[str, str]:
        t = int(round(time.time() * 1000))
        nonce = uuid.uuid4()
        return {
            'Authorization': self._api_token,
            't': str(t),
            'sign': str(base64.b64encode(
                hmac.new(bytes(self._api_token, 'utf-8'), msg=bytes(f'{self._api_token}{t}{nonce}', 'utf-8'), digestmod=hashlib.sha256).digest()), 'utf-8'),
            'nonce': str(nonce)
        }

    @property
    def default_headers(self) -> Dict[str, str]:
        return {
            **super().default_headers
        }


Client = TogglAPI
AsyncClient = AsyncTogglAPI
