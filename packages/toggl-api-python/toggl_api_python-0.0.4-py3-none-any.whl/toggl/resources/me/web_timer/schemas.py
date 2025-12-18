from pydantic import ConfigDict
from ...._schemas import ResponseBase


class GetWebTimerResponse(ResponseBase):
    # The web timer payload contains various fields; allow passthrough.
    model_config = ConfigDict(extra="allow")

