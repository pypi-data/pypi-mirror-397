from pydantic import ConfigDict
from typing import TypeAlias
from ...._schemas import ResponseBase

class Feature(ResponseBase):
    enabled: bool
    feature_id: str
    name: str
    
class WorkspaceFeatures(ResponseBase):
    features: list[Feature]
    workspace_id: int

GetFeaturesResponse: TypeAlias = list[WorkspaceFeatures]