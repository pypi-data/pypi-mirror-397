from ...._schemas import ResponseBase
from typing import TypeAlias


class TrackReminder(ResponseBase):
    craeted_at: str
    frequency: str
    group_ids: list[int]
    reminder_id: int
    threshold: int
    user_ids: list[int]
    workspace_id: int

GetTrackRemindersResponse: TypeAlias = list[TrackReminder]
