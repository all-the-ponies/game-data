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



class QuestInfo(BaseModel):
    title: StringId = ''
    description: StringId = ''
    completed_description: StringId = ''
    skippable: bool = True
    auto_start: bool = False
    global_quest: bool = False
    invisible: bool = False
    add_to_complete_after_start: bool = False
    skip_for_COPPA: bool = False
    skip_for_OFT: bool = False
    icon: RenamedFile | None = None
    giver_icon: RenamedFile | None = None
    giver_image: RenamedFile | None = None
    location: Location = 'UNKNOWN'
    any_quest: bool = False

class GlobalCountRequirement(BaseModel):
    category: str
    item: GameObjectId
    amount: int
    
class QuestRequirements(BaseModel):
    any_quest: bool = False
    quests_completed: list[str] = Field(default_factory = list)
    global_counts: list[GlobalCountRequirement] = Field(default_factory = list)
    no_start_zones: list[Location] = Field(default_factory = list)

class QuestTaskObjective(BaseModel):
    scope: Literal['local', 'global']
    category: str
    item: GameObjectId | None
    value: int

class QuestTask(BaseModel):
    id: str
    description: StringId = ''
    icon: RenamedFile = Field(default_factory = RenamedFile)
    skippable: bool = False
    skip_for_OFT: bool = False
    skip_cost: int = 0
    ad_skip: bool = True
    has_go: bool = True
    objective: QuestTaskObjective | None = None

class QuestRewardItem(BaseModel):
    id: str = ''
    value: int = 0
    alt_currency: Currency = 'Gems'
    alt_value: int = 0
    consumable_id: str = ''
    consumable_count: int = 0

class QuestRewards(BaseModel):
    bits: int = 0
    gems: int = 0
    hearts: int = 0
    xp: int = 0
    item1: QuestRewardItem = Field(default_factory = QuestRewardItem)
    item2: QuestRewardItem = Field(default_factory = QuestRewardItem)

class QuestEvent(BaseModel):
    type: str = ''
    value: str = ''

class QuestEvents(BaseModel):
    start: list[QuestEvent] = Field(default_factory = list)
    end: list[QuestEvent] = Field(default_factory = list)

class QuestType(BaseModel):
    id: str
    category: str
    info: QuestInfo = Field(default_factory = QuestInfo)
    requirements: QuestRequirements = Field(default_factory = QuestRequirements)
    tasks: list[QuestTask] = Field(default_factory = list)
    rewards: QuestRewards = Field(default_factory = QuestRewards)
    events: QuestEvents = Field(default_factory = QuestEvents)


class QuestCategory(BaseModel):
    id: str
    name: StringId
    final_text: StringId = ''
    active_limit: int = 0
    time_limited: bool = False
    image: ImageBase[Literal['outro', 'reward']] = Field(default_factory = dict)
    building: GameObjectId | None = None
    outro_cinematic: CinematicId | None = None


class QuestData(BaseModel):
    quests: dict[str, QuestType] = Field(default_factory = dict)
    categories: dict[str, QuestCategory] = Field(default_factory = dict)
