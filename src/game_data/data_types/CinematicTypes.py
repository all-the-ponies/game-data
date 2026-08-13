from typing import Literal

from pydantic import BaseModel, Field

from .common_types import (
    CinematicId,
    Currency,
    GameObjectId,
    ImageBase,
    Location,
    RenamedFile,
    StringId,
)


class CinematicLine(BaseModel):
    image: RenamedFile
    line: StringId

class CinematicType(BaseModel):
    id: CinematicId
    lines: list[CinematicLine] = Field(default_factory = list)


class CinematicData(BaseModel):
    cinematics: dict[CinematicId, CinematicType] = Field(default_factory = dict)
