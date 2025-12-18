from __future__ import annotations
from typing import TYPE_CHECKING
from ....._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetProjectsResponse

if TYPE_CHECKING:
    from ....._client import SyncAPIClient, AsyncAPIClient


class Projects(SyncAPIResourceBase):
    def __init__(self, client, workspace_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id

    def _base_path(self) -> str:
        return f"workspaces/{self._workspace_id}"

    def get(self) -> GetProjectsResponse:
        return self._client.get(
            path=f"{self._base_path()}/projects",
            options={"params": {}},
            ResponseT=GetProjectsResponse,
        )


class AsyncProjects(AsyncAPIResourceBase):
    def __init__(self, client, workspace_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id

    def _base_path(self) -> str:
        return f"workspaces/{self._workspace_id}"

    async def get(self) -> GetProjectsResponse:
        return await self._client.get(
            path=f"{self._base_path()}/projects",
            options={"params": {}},
            ResponseT=GetProjectsResponse,
        )

