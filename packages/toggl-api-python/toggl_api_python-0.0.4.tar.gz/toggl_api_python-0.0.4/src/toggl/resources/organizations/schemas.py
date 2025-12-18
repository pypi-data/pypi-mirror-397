from pydantic import Field
from ..._schemas import RequestBody, ResponseBase

class PostOrganizationRequest(RequestBody):
    name: str = Field(description="Name of the organization")
    workspace_name: str = Field(description="Name of the workspace")

class PostOrganizationResponse(ResponseBase):
    id: int = Field(description="ID of the organization")
    name: str = Field(description="Name of the organization")
    permissions: list[str] = Field(description="Permissions of the organization")
    workspace_id: int = Field(description="ID of the workspace")
    workspace_name: str = Field(description="Name of the workspace")