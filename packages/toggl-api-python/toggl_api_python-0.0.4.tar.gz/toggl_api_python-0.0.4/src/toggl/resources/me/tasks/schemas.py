from pydantic import Field
from typing import Any, TypeAlias
from ...._schemas import QueryBase, ResponseBase


class GetTasksQuery(QueryBase):
    meta: bool | None = Field(default=None, description="Should the response contain data for meta entities")
    since: int | None = Field(default=None, description="Get tasks modified since this UNIX timestamp.")
    include_not_active: bool | None = Field(default=None, description="Include tasks marked as done.")
    offset: int | None = Field(default=None, description="Offset to resume the next pagination from.")
    per_page: int | None = Field(default=None, description="Number of items per page, default is all.")

class Task(ResponseBase):
    active: bool = Field(description="False when the task has been done")
    at: str = Field(description="When the task was created/last modified")
    avatar_url: str | None = Field(default=None, description="Avatar URL")
    client_id: int | None = Field(default=None, description="Client ID")
    client_name: str | None = Field(default=None, description="Client name")
    estimated_seconds: int | None = Field(default=None, description="Estimated seconds")
    external_reference: str | None = Field(default=None, description="ExternalReference can be used to store an external reference to the Track Task Entity.")
    id: int = Field(description="Task ID")
    integration_ext_id: str | None = Field(default=None, description="The external ID of the linked entity in the external system (e.g. JIRA/SalesForce)")
    integration_ext_type: str | None = Field(default=None, description="The external type of the linked entity in the external system (e.g. JIRA/SalesForce)")
    integration_provider: Any | None = Field(default=None, description="The provider (e.g. JIRA/SalesForce) that has an entity linked to this Toggl Track entity")
    name: str = Field(description="Task Name")
    permissions: list[str] | None = Field(default=None, description="Array of string")
    project_billable: bool | None = Field(default=None, description="-")
    project_color: str | None = Field(default=None, description="Metadata")
    project_id: int | None = Field(default=None, description="Project ID")
    project_is_private: bool | None = Field(default=None, description="null")
    project_name: str | None = Field(default=None, description="-")
    rate: float | None = Field(default=None, description="Rate for this task")
    rate_last_updated: str | None = Field(default=None, description="null")
    recurring: bool | None = Field(default=None, description="Whether this is a recurring task")
    toggl_accounts_id: str | None = Field(default=None, description="null")
    tracked_seconds: int | None = Field(default=None, description="The value tracked_seconds is in milliseconds, not in seconds.")
    user_id: int | None = Field(default=None, description="null")
    user_name: str | None = Field(default=None, description="null")
    workspace_id: int | None = Field(default=None, description="Workspace ID")
    
GetTasksResponse: TypeAlias = list[Task]

