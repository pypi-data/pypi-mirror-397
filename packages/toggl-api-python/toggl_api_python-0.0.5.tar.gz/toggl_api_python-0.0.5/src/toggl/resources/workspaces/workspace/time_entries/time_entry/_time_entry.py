from __future__ import annotations
from functools import cached_property
from ......_resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .stop import Stop, AsyncStop


class TimeEntry(SyncAPIResourceBase):
    def __init__(self, client, workspace_id: int, time_entry_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._time_entry_id = time_entry_id

    def _path(self) -> str:
        return f"workspaces/{self._workspace_id}/time_entries/{self._time_entry_id}"

    @cached_property
    def stop(self) -> Stop:
        return Stop(self._client, workspace_id=self._workspace_id, time_entry_id=self._time_entry_id)
    
    
class AsyncTimeEntry(AsyncAPIResourceBase):
    def __init__(self, client, workspace_id: int, time_entry_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._time_entry_id = time_entry_id

    def _path(self) -> str:
        return f"workspaces/{self._workspace_id}/time_entries/{self._time_entry_id}"

    @cached_property
    def stop(self) -> AsyncStop:
        return AsyncStop(self._client, workspace_id=self._workspace_id, time_entry_id=self._time_entry_id)