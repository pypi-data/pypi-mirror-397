from __future__ import annotations
from functools import cached_property
from typing import TYPE_CHECKING
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .current._current import Current, AsyncCurrent

if TYPE_CHECKING:
    from ...._client import SyncAPIClient, AsyncAPIClient

class TimeEntries(SyncAPIResourceBase):
    @cached_property
    def current(self) -> Current:
        return Current(self._client)
    
class AsyncTimeEntries(AsyncAPIResourceBase):
    @cached_property
    def current(self) -> AsyncCurrent:
        return AsyncCurrent(self._client)