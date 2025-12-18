from .schemas import GetPreferencesResponse
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase

class Preferences(SyncAPIResourceBase):
    def get(self) -> GetPreferencesResponse:
        return self._client.get(path="me/preferences", options={"params": {}}, ResponseT=GetPreferencesResponse)

class AsyncPreferences(AsyncAPIResourceBase):
    async def get(self) -> GetPreferencesResponse:
        return await self._client.get(path="me/preferences", options={"params": {}}, ResponseT=GetPreferencesResponse)