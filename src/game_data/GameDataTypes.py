from typing import Any, Literal, TypedDict, NotRequired, Optional, TypeVarTuple, TypeVar, Any

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, DataClassJsonMixin, config

def ExcludeIfNone(value: Any):
    return value is None

def OptionalField[T](default = None):
    return field(default = default, metadata = config(exclude = ExcludeIfNone))


type GameObjectId = str

type Language = Literal[
    'arabic', 'chinese', 'english', 'french', 'german', 'italian',
    'japanese', 'korean', 'brazilian portuguese', 'russian',
    'spanish', 'thai', 'turkish'
]

type Location = Literal[
    'PONYVILLE', 'CANTERLOT', 'SWEET_APPLE_ACRES', 'EVERFREE_FOREST',
    'CRYSTAL_EMPIRE', 'CHANGELING_KINGDOM', 'KLUGETOWN', 'UNKNOWN'
]

type Currency = Literal['Gems', 'Bits'] | GameObjectId

type CategoryName = Literal[
    'pony', 'house', 'shop', 'decor', 'item',
    'token', 'avatar', 'frame', 'background_frame', 'background'
]

type TranslatableString = dict[Language, str]
type AltName = dict[Language, list[str]]

@dataclass
class RenamedFile(DataClassJsonMixin):
    path: str
    original: Optional[str]

type ImageBase[T] = dict[T | Literal['main'], RenamedFile]

@dataclass
class StarReward(DataClassJsonMixin):
    item: str
    amount: int

@dataclass
class PriceBase(DataClassJsonMixin):
    currency: Currency | None = None
    amount: int = 0

@dataclass
class Price(DataClassJsonMixin):
    base: PriceBase = field(default_factory = PriceBase)
    token: GameObjectId | None = None
    daily_goals: int = 0

@dataclass
class GenericObjectType(DataClassJsonMixin):
    index: int
    id: str
    name: TranslatableString
    image: ImageBase
    preferred_name: Optional[TranslatableString] = OptionalField()
    alt_name: Optional[AltName] = OptionalField()
    price: Optional[Price] = OptionalField()
    tags: list[str] = field(default_factory = list)


@dataclass
class ChangelingData(DataClassJsonMixin):
    id: str = ''
    IAmAlterSet: bool = False

@dataclass
class MinigameData(DataClassJsonMixin):
    can_play_minecart: bool = True
    hard_lock: bool = True
    cooldown: int = 0
    skip_cost: int = 0
    exp_rank: int = 0
    has_wings: bool = False

@dataclass
class TaskData(DataClassJsonMixin):
    name: TranslatableString
    time: int
    xp: int
    bits: int
    gems: int
    token: str
    chance: float
    token_amount: int
    requires: str

@dataclass
class PonyType(GenericObjectType):
    category: Literal['pony'] = 'pony'
    description: TranslatableString = field(default_factory = dict)
    image: ImageBase[Literal['portrait']]
    location: Location = 'UNKNOWN'
    house: Optional[str] = None
    inns: list[GameObjectId] = field(default_factory = list)
    changeling: ChangelingData = field(default_factory = ChangelingData)
    group_master: bool = False
    group: list[str] = field(default_factory = list)
    max_level: bool = False
    rewards: list[StarReward] = field(default_factory = list)
    minigame: MinigameData = field(default_factory = MinigameData)
    arrival_xp: int = 0
    unlock_level: int = 0
    ai_type: int = 0
    not_pony: bool = False
    ban_pets: bool = False
    tasks: list[str] = field(default_factory = list)
    pro: list[str] = field(default_factory = list)
    collections: list[str] = field(default_factory = list)
    wiki_path: str | None = None

@dataclass
class HouseBuild(DataClassJsonMixin):
    time: int
    skip_cost: int
    xp: int

class HouseType(GenericObjectType):
    category: Literal['house']
    image: ImageBase
    location: list[Location]
    grid_size: int
    build: HouseBuild
    residents: list[str]
    visitors: list[str]
    wiki_path: str

class ShopType(GenericObjectType):
    category: Literal['shop']
    image: ImageBase
    grid_size: int
    build: HouseBuild
    residents: list[str]
    visitors: list[str]
    unlock_level: int
    location: Location
    product: ShopProduct
    can_sell: bool
    cost: Price
    wiki_path: str

@dataclass
class DecorPro(DataClassJsonMixin):
    is_pro: bool
    size: int
    time: int
    bits: int

class DecorType(GenericObjectType):
    category: Literal['decor']
    image: ImageBase
    location: Location
    unlock_level: int
    limit: int
    grid_size: int
    xp: int
    cost: Price
    fusion_points: int
    pro: DecorPro

class ItemType(GenericObjectType):
    category: Literal['item']
    image: ImageBase
    alt_ids: list[str]

class TokenType(GenericObjectType):
    category: Literal['token']
    image: ImageBase
    chance: float
    tasks: list[str]
    unlimited: bool
    no_reset: bool

class AvatarType(GenericObjectType):
    category: Literal['avatar']
    image: ImageBase[Literal['preview']]
    is_default: bool
    pony: str
    animated: bool

class AvatarFrameType(GenericObjectType):
    category: Literal['avatar_frame']
    image: ImageBase[Literal['preview']]
    is_default: bool
    animated: bool

class BackgroundType(GenericObjectType):
    category: Literal['background']
    image: ImageBase[Literal['preview']]
    is_default: bool
    animated: bool

class BackgroundFrameType(GenericObjectType):
    category: Literal['background_frame']
    image: ImageBase[Literal['preview']]
    is_default: bool
    animated: bool

class PetType(GenericObjectType):
    category: Literal['pet']
    pony: GameObjectId
    flying: bool
    task_bonus: int
    minecart_bonus: int

class ThemeType(GenericObjectType):
    category: Literal['theme']
    location: Location
    season: str
    shop_bonus: int
    quest: str

class PathType(GenericObjectType):
    category: Literal['path']
    location: Location
    sprite: str

class BoosterType(GenericObjectType):
    category: Literal['booster']
    type: Literal['xp', 'bits']
    time: int
    multiplier: int

@dataclass
class FarmCost(DataClassJsonMixin):
    shard: GameObjectId
    shard_cost: int
    item: GameObjectId
    item_cost: int

@dataclass
class CritterUpgrade(DataClassJsonMixin):
    currency: GameObjectId
    cost: int
    shard: GameObjectId
    shard_cost: int

@dataclass
class ConsumableCritter(DataClassJsonMixin):
    main_feed: GameObjectId
    additional_feed: GameObjectId
    phases: list[dict[Literal['main', 'additional'], int]]
    upgrade: CritterUpgrade
    final_cooldown: int

class ConsumableType(GenericObjectType):
    category: Literal['consumable']
    consume: dict[Literal['xp', 'bits', 'gems', 'hearts', 'wheels', 'blitz_energy', 'tls'], int]
    farm: Optional[list[FarmCost]] = OptionalField()
    critter: Optional[ConsumableCritter] = OptionalField()

@dataclass
class CostumeBonus(DataClassJsonMixin):
    type: Literal['MineCart', 'ShopProduction', 'MiniGames', '']
    amount: int

class CostumeType(GenericObjectType):
    category: Literal['costume']
    image: ImageBase[Literal['alt']]
    enabled: bool
    can_be_new: bool
    is_subset: bool
    is_only_alternate_mesh: bool
    parts: dict[Literal['body', 'mane', 'tail'], GameObjectId | None]
    bonus: CostumeBonus
    tls_background: RenamedFile | None
    sunsets: list[GameObjectId] | None

@dataclass
class CostumePartType(DataClassJsonMixin):
    index: int
    category: Literal['costume_part']
    image: ImageBase[Literal['alt']]
    model_name: str
    LinkedPart: GameObjectId | None
    type: Literal['body', 'mane', 'tail']
    apply_time: int
    gem_price: int


type GameObject = PonyType | HouseType | ShopType | DecorType | ItemType | TokenType | AvatarType | GenericObjectType


@dataclass
class QuestDetail(DataClassJsonMixin):
    name: TranslatableString
    description: TranslatableString
    pro: list[str]
    special: Literal['seasonal', 'tutorial'] | None

@dataclass
class GroupQuests(DataClassJsonMixin):
    file_version: int = 1
    random_pros: list[str] = field(default_factory = list)
    quests: dict[str, QuestDetail] = field(default_factory = dict)


type FortuneShopRarities = Literal['rare', 'common', 'uncommon']
type FortuneShopPrices = Literal['regular', 'discount', 'super', 'ultra']

@dataclass
class FortuneShopItemPricesList(DataClassJsonMixin):
    regular: dict[FortuneShopPrices, int]
    royal: dict[FortuneShopPrices, int]

@dataclass
class FortuneShopItem(DataClassJsonMixin):
    id: GameObjectId
    rarity: FortuneShopRarities
    amount: int
    prices: FortuneShopItemPricesList

@dataclass
class FortuneShop(DataClassJsonMixin):
    file_version: int = 1
    max_items_in_shop: int = 6
    refresh_cost: int = 50
    item_rarity_chances: dict[FortuneShopRarities, float] = field(default_factory = dict)
    item_price_chances: dict[FortuneShopPrices, float] = field(default_factory = dict)
    items: dict[FortuneShopRarities, dict[GameObjectId, FortuneShopItem]] = field(default_factory = dict)


@dataclass
class CategoryData[T](DataClassJsonMixin):
    objects: dict[GameObjectId, T] = field(default_factory = dict)


@dataclass
class GameObjects(DataClassJsonMixin):
    file_version: int = 1
    pony: CategoryData[PonyType] = field(default_factory = CategoryData[PonyType])
    house: CategoryData[HouseType] = field(default_factory = CategoryData[HouseType])
    shop: CategoryData[ShopType] = field(default_factory = CategoryData[ShopType])
    decor: CategoryData[DecorType] = field(default_factory = CategoryData[DecorType])
    avatar: CategoryData[AvatarType] = field(default_factory = CategoryData[AvatarType])
    avatar_frame: CategoryData[AvatarFrameType] = field(default_factory = CategoryData[AvatarFrameType])
    background: CategoryData[BackgroundType] = field(default_factory = CategoryData[BackgroundType])
    background_frame: CategoryData[BackgroundFrameType] = field(default_factory = CategoryData[BackgroundFrameType])
    pet: CategoryData[PetType] = field(default_factory = CategoryData[PetType])
    theme: CategoryData[ThemeType] = field(default_factory = CategoryData[ThemeType])
    path: CategoryData[PathType] = field(default_factory = CategoryData[PathType])
    item: CategoryData[ItemType] = field(default_factory = CategoryData[ItemType])
    booster: CategoryData[BoosterType] = field(default_factory = CategoryData[BoosterType])
    token: CategoryData[TokenType] = field(default_factory = CategoryData[TokenType])
    consumable: CategoryData[ConsumableType] = field(default_factory = CategoryData[ConsumableType])
    costume: CategoryData[CostumeType] = field(default_factory = CategoryData[CostumeType])
    costume_part: CategoryData[CostumePartType] = field(default_factory = CategoryData[CostumePartType])

@dataclass
class GameVersion(DataClassJsonMixin):
    game_version: str = ''
    content_version: str = ''

class GameDataType(TypedDict):
    file_version: int
    game_version: str
    content_version: str
    categories: GameObjects
    group_quests: GroupQuests
    fortune_shop: FortuneShop
