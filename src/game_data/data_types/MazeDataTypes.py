from typing import Literal

from pydantic import BaseModel, Field

from .common_types import GameObjectId, ImageBase, TranslatableString

class MazeBlockEntity(BaseModel):
    id: str
    type: Literal["MazeBlock_Start", "MazeBoss", "MazeChest", "MazeShop"]


class MazeMapBlock(BaseModel):
    id: str
    x: int
    y: int
    connections: dict[
        Literal[
            "north_east",
            "north_west",
            "south_east",
            "south_west",
        ],
        bool,
    ]
    uncovered: bool
    entity: MazeBlockEntity | None = None


class MazeMapShop(BaseModel):
    id: GameObjectId
    x: int
    y: int


class MazeMap(BaseModel):
    blocks: list[MazeMapBlock] = Field(default_factory=list)
    shops: list[MazeMapShop] = Field(default_factory=list)


class MazeShopSlot(BaseModel):
    id: str
    price: int


class MazeShopTier(BaseModel):
    id: str
    slots: list[MazeShopSlot]


class MazeChest(BaseModel):
    id: str
    tier: str


class MazeBossReward(BaseModel):
    item: GameObjectId
    amount: int


class MazeBoss(BaseModel):
    id: str
    pony: GameObjectId
    required_power: int
    hp: int
    critical_multiplier: float
    drop_chest: str
    rewards: list[MazeBossReward]


class MazeShop(BaseModel):
    id: str
    tier: str


class MazePony(BaseModel):
    id: str
    pony: GameObjectId
    power: int
    fights: int
    upgraded: bool


class MazeCommHelper(BaseModel):
    id: str
    pony: GameObjectId
    cooldown: int = 0
    skip: int = 0
    points: list[int] = Field(default_factory = list)
    multiplier: int = 1

class MazeCommunity(BaseModel):
    helpers: list[MazeCommHelper] = Field(default_factory = list)
    token: GameObjectId = ''

class MazeSettings(BaseModel):
    tile_energy: int = 30
    battle_energy: int = 15
    max_energy: int = 300
    energy_cooldown: int = 114


class MazeData(BaseModel):
    id: str = ""
    name: TranslatableString = Field(default_factory=dict)
    settings: MazeSettings = Field(default_factory = MazeSettings)
    image: ImageBase[Literal["outro"]] = Field(default_factory=dict)
    map: MazeMap = Field(default_factory=MazeMap)
    shop_tiers: dict[str, MazeShopTier] = Field(default_factory=dict)
    chest_rewards: dict[str, list[str]] = Field(default_factory=dict)
    ponies: dict[str, MazePony] = Field(default_factory=dict)
    chests: dict[str, MazeChest] = Field(default_factory=dict)
    bosses: dict[str, MazeBoss] = Field(default_factory=dict)
    shops: dict[str, MazeShop] = Field(default_factory=dict)
    community: MazeCommunity = Field(default_factory = MazeCommunity)
