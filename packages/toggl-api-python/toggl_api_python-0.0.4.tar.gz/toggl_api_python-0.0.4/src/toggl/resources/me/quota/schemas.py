from typing import TypeAlias
from ...._schemas import ResponseBase

class Quota(ResponseBase):
    organization_id: int
    remaining: int
    resets_in_secs: int
    total: int

GetQuotaResponse: TypeAlias = list[Quota]
