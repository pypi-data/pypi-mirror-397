from pydantic import Field
from typing import TypeAlias
from ..._schemas import Workspace
from ...._schemas import QueryBase

class GetWorkspacesQuery(QueryBase):
    since: int | None = Field(
        default=None,
        description="Retrieve workspaces created/modified/deleted since this UNIX timestamp.",
    )


GetWorkspacesResponse: TypeAlias = list[Workspace]

