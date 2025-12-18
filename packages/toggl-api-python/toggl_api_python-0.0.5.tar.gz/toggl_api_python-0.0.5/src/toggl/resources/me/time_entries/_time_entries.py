from __future__ import annotations
from functools import cached_property
from typing import TYPE_CHECKING
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .current._current import Current, AsyncCurrent
from .schemas import GetTimeEntriesResponse, GetTimeEntriesQuery

if TYPE_CHECKING:
    from ...._client import SyncAPIClient, AsyncAPIClient

class TimeEntries(SyncAPIResourceBase):
    @cached_property
    def current(self) -> Current:
        return Current(self._client)
    
    def get(self, query: GetTimeEntriesQuery) -> GetTimeEntriesResponse:
        return self._client.get(path="me/time_entries", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetTimeEntriesResponse)
    
class AsyncTimeEntries(AsyncAPIResourceBase):
    @cached_property
    def current(self) -> AsyncCurrent:
        return AsyncCurrent(self._client)
    
    async def get(self, query: GetTimeEntriesQuery) -> GetTimeEntriesResponse:
        return await self._client.get(path="me/time_entries", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetTimeEntriesResponse)