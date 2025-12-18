from __future__ import annotations
from typing import TYPE_CHECKING
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetTasksQuery, GetTasksResponse

if TYPE_CHECKING:
    from ...._client import SyncAPIClient, AsyncAPIClient


class Tasks(SyncAPIResourceBase):
    def get(self, query: GetTasksQuery | None = None) -> GetTasksResponse:
        query_params = query.model_dump(exclude_none=True) if query else {}
        return self._client.get(
            path="me/tasks",
            options={"params": query_params},
            ResponseT=GetTasksResponse,
        )


class AsyncTasks(AsyncAPIResourceBase):
    async def get(self, query: GetTasksQuery | None = None) -> GetTasksResponse:
        query_params = query.model_dump(exclude_none=True) if query else {}
        return await self._client.get(
            path="me/tasks",
            options={"params": query_params},
            ResponseT=GetTasksResponse,
        )

