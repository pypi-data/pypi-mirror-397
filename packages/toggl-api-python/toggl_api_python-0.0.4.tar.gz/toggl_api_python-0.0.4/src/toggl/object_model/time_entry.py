from ._object_model_base import ObjectModelBase
from typing import Self
from toggl import TogglAPI

class TimeEntry(ObjectModelBase):
    project_id: int
    def find(cls) -> Self:
        client = TogglAPI()
        client.me.time_entries