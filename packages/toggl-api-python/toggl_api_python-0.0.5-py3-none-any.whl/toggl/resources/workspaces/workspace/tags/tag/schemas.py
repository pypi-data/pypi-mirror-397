from ......_schemas import ApiDataModel
from typing import TypeAlias
from pydantic import Field
from ....._schemas import Tag

class PutTagRequest(ApiDataModel):
    name: str = Field(description="Tag name")

PutTagResponse: TypeAlias = Tag