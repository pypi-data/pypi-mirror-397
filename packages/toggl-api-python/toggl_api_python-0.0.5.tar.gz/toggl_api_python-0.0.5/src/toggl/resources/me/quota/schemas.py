from typing import TypeAlias
from ...._schemas import ApiDataModel

class Quota(ApiDataModel):
    organization_id: int
    remaining: int
    resets_in_secs: int
    total: int

GetQuotaResponse: TypeAlias = list[Quota]
