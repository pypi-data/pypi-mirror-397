from typing import Any, Literal
from pydantic import BaseModel, Field, field_serializer, field_validator
from datetime import datetime, timezone
from ....._schemas import ApiDataModel, ApiDataModel, QueryBase
from ...._schemas import SharedWith

class EventMetadata(BaseModel):
    origin_feature: str | None = Field(default=None)
    visible_goals_count: int | None = Field(default=None)
    
class PostTimeEntryRequest(ApiDataModel):
    billable: bool | None = Field(default=None)
    created_with: str = Field(default="")
    description: str | None = Field(default=None)
    duration: int | None = Field(default=None)
    duronly: bool | None = Field(default=None)
    event_metadata: EventMetadata | None = Field(default=None)
    expense_ids: list[int] | None = Field(default=None)
    pid: int | None = Field(default=None)
    project_id: int | None = Field(default=None)
    shared_with_user_ids: list[int] | None = Field(default=None)
    start: datetime | str = Field(description="Start time as a timezone-aware datetime or ISO string.")
    start_date: str | None = Field(default=None)
    stop: datetime | str | None = Field(default=None, description="Stop time as a timezone-aware datetime or ISO string.")
    tag_action: Literal["add", "delete"] | None = Field(description="Can be 'add' or 'delete'. Used when updating an existing time entry", default=None)
    tag_ids: list[int] = Field(default=[])
    tags: list[str] | None = Field(default=None)
    task_id: int | None = Field(default=None)
    tid: int | None = Field(default=None)
    uid: int | None = Field(default=None)
    user_id: int | None = Field(default=None)
    wid: int
    workspace_id: int | None = Field(default=None)
    
    @field_serializer("start", "stop")
    def serialize_datetime(self, dt: datetime) -> str:
        return self.parse_tz_aware_datetime_to_iso_string(dt)


class PostTimeEntryResponse(ApiDataModel):
    billable: bool | None = Field(default=None)
    client_name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    duration: int | None = Field(default=None)
    duronly: bool | None = Field(default=None)
    expense_ids: list[int] | None = Field(default=None)
    permissions: list[str] | None = Field(default=None)
    pid: int | None = Field(default=None)
    project_active: bool | None = Field(default=None)
    project_billable: bool | None = Field(default=None)
    project_color: str | None = Field(default=None)
    project_id: int | None = Field(default=None)
    project_name: str | None = Field(default=None)
    shared_with: list[SharedWith] | None = Field(default=None)
    start: str | None = Field(default=None)
    stop: str | None = Field(default=None)
    tag_ids: list[int] | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    task_id: int | None = Field(default=None)
    task_name: str | None = Field(default=None)
    tid: int | None = Field(default=None)
    uid: int | None = Field(default=None)
    user_avatar_url: str | None = Field(default=None)
    user_id: int | None = Field(default=None)
    user_name: str | None = Field(default=None)
    wid: int | None = Field(default=None)
    workspace_id: int | None = Field(default=None)


class PostTimeEntryQuery(QueryBase):
    meta: bool | None = Field(default=None)