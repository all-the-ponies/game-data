from typing import (
    Any,
    Any,
    Literal,
    NotRequired,
    Optional,
    TYPE_CHECKING,
    TypeVar,
    TypeVarTuple,
    TypedDict,
)

from pydantic import BaseModel, Field

def ExcludeIfNone(value: Any):
    return value is None


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

type TranslatableString = dict[Language, str]
type AltName = dict[Language, list[str]]

class RenamedFile(BaseModel):
    path: str
    original: Optional[str]

type ImageBase[T] = dict[T | Literal['main'], RenamedFile]

class StarReward(BaseModel):
    item: str
    amount: int

class PriceBase(BaseModel):
    currency: Currency | None = None
    amount: int = 0

class Price(BaseModel):
    base: PriceBase = Field(default_factory = PriceBase)
    token: GameObjectId | None = None
    daily_goals: int = 0

class GenericObjectType(BaseModel):
    index: int
    id: str
    name: TranslatableString = Field(default_factory = dict)
    image: ImageBase = Field(default_factory = dict)
    preferred_name: Optional[TranslatableString] = Field(default = None, exclude_if = lambda v: v is None)
    alt_name: Optional[AltName] = Field(default = None, exclude_if = lambda v: v is None)
    price: Optional[Price] = Field(default = None, exclude_if = lambda v: v is None)
    tags: list[str] = Field(default_factory = list)


class ChangelingData(BaseModel):
    id: str = ''
    IAmAlterSet: bool = False

class MinigameData(BaseModel):
    can_play_minecart: bool = True
    hard_lock: bool = True
    cooldown: int = 0
    skip_cost: int = 0
    exp_rank: int = 0
    has_wings: bool = False

class TaskData(BaseModel):
    name: TranslatableString
    time: int
    xp: int
    bits: int
    gems: int
    token: str
    chance: float
    token_amount: int
    requires: str

class PonyType(GenericObjectType):
    category: Literal['pony'] = 'pony'
    description: TranslatableString = Field(default_factory = dict)
    image: ImageBase[Literal['portrait']] = Field(default_factory = dict)
    location: Location = 'UNKNOWN'
    house: Optional[str] = None
    inns: list[GameObjectId] = Field(default_factory = list)
    changeling: ChangelingData = Field(default_factory = ChangelingData)
    group_master: bool = False
    group: list[str] = Field(default_factory = list)
    max_level: bool = False
    rewards: list[StarReward] = Field(default_factory = list)
    minigame: MinigameData = Field(default_factory = MinigameData)
    arrival_xp: int = 0
    unlock_level: int = 0
    ai_type: int = 0
    not_pony: bool = False
    ban_pets: bool = False
    tasks: list[str] = Field(default_factory = list)
    pro: list[str] = Field(default_factory = list)
    collections: list[str] = Field(default_factory = list)
    costumes: list[GameObjectId] = Field(default_factory = list)
    wiki_path: str = ''

class HouseBuild(BaseModel):
    time: int = 0
    skip_cost: int = 0
    xp: int = 0

class HouseType(GenericObjectType):
    category: Literal['house'] = 'house'
    location: list[Location] = Field(default_factory = list)
    grid_size: int = 0
    build: HouseBuild = Field(default_factory = HouseBuild)
    residents: list[str] = Field(default_factory = list)
    visitors: list[str] = Field(default_factory = list)
    wiki_path: str = ''

class ShopType(GenericObjectType):
    category: Literal['shop'] = 'shop'
    grid_size: int = 0
    build: HouseBuild = Field(default_factory = HouseBuild)
    residents: list[str] = Field(default_factory = list)
    visitors: list[str] = Field(default_factory = list)
    unlock_level: int = 0
    location: Location = 'UNKNOWN'
    product: GameObjectId = ''
    special: Literal['lotto', 'ck_entrance', 'ferris_wheel'] | None = None
    can_sell: bool = False
    cost: Price = Field(default_factory = Price)
    wiki_path: str = ''

class DecorPro(BaseModel):
    is_pro: bool = False
    size: int = 0
    time: int = 0
    bits: int = 0

class DecorType(GenericObjectType):
    category: Literal['decor'] = 'decor'
    location: Location = 'UNKNOWN'
    unlock_level: int = 0
    limit: int = 0
    grid_size: int = 0
    xp: int = 0
    fusion_points: int = 0
    pro: DecorPro = Field(default_factory = DecorPro)

class ItemType(GenericObjectType):
    category: Literal['item'] = 'item'
    alt_ids: list[str] = Field(default_factory = list)

class TokenType(GenericObjectType):
    category: Literal['token'] = 'token'
    consumable: GameObjectId = ''
    chance: float = 0
    tasks: list[str] = Field(default_factory = list)
    unlimited: bool = False
    no_reset: bool = False
    special: int = 0

class AvatarType(GenericObjectType):
    category: Literal['avatar'] = 'avatar'
    image: ImageBase[Literal['preview']] = Field(default_factory = dict)
    is_default: bool = False
    pony: GameObjectId | None = None
    animated: bool = False

class AvatarFrameType(GenericObjectType):
    category: Literal['avatar_frame'] = 'avatar_frame'
    image: ImageBase[Literal['preview']] = Field(default_factory = dict)
    is_default: bool = False
    animated: bool = False

class BackgroundType(GenericObjectType):
    category: Literal['background'] = 'background'
    image: ImageBase[Literal['preview']] = Field(default_factory = dict)
    is_default: bool = False

class BackgroundFrameType(GenericObjectType):
    category: Literal['background_frame'] = 'background_frame'
    is_default: bool = False

class CutieMarkType(GenericObjectType):
    category: Literal['cutie_mark'] = 'cutie_mark'
    pony: GameObjectId = ''
    is_default: bool = False

class PetType(GenericObjectType):
    category: Literal['pet'] = 'pet'
    pony: GameObjectId = ''
    flying: bool = False
    task_bonus: int = 0
    minecart_bonus: int = 0

class ThemeType(GenericObjectType):
    category: Literal['theme'] = 'theme'
    location: Location = 'UNKNOWN'
    season: str = ''
    shop_bonus: int = 0
    quest: str = ''
    texture_suffix: str = ''

class PathType(GenericObjectType):
    category: Literal['path'] = 'path'
    location: Location = 'UNKNOWN'
    sprite: str = ''

class BoosterType(GenericObjectType):
    category: Literal['booster'] = 'booster'
    type: Literal['xp', 'bits'] | None = None
    time: int = 0
    multiplier: int = 0

class FarmCost(BaseModel):
    shard: GameObjectId
    shard_cost: int
    item: GameObjectId
    item_cost: int

class CritterUpgrade(BaseModel):
    currency: GameObjectId
    cost: int
    shard: GameObjectId
    shard_cost: int

class ConsumableCritter(BaseModel):
    critter: GameObjectId
    main_feed: GameObjectId
    additional_feed: GameObjectId
    phases: list[dict[Literal['main', 'additional'], int]]
    upgrade: CritterUpgrade
    final_cooldown: int
    final_reward: dict[Literal['gems', 'xp'], int]

class ConsumableType(GenericObjectType):
    category: Literal['consumable'] = 'consumable'
    consume: dict[Literal['xp', 'bits', 'gems', 'hearts', 'wheels', 'blitz_energy', 'tls'], int] = Field(default_factory = dict)
    time: int = 0
    skip_cost: int = 0
    farm: Optional[list[FarmCost]] = Field(default = None, exclude_if = lambda v: v is None)
    critter: Optional[ConsumableCritter] = Field(default = None, exclude_if = lambda v: v is None)

class CostumeBonus(BaseModel):
    type: Literal['MineCart', 'ShopProduction', 'MiniGames', ''] = ''
    amount: int = 0

class CostumeType(GenericObjectType):
    category: Literal['costume'] = 'costume'
    image: ImageBase[Literal['alt']] = Field(default_factory = dict)
    pony: GameObjectId = ''
    enabled: bool = False
    can_be_new: bool = False
    is_subset: bool = False
    is_only_alternate_mesh: bool = False
    parts: dict[Literal['body', 'mane', 'tail'], GameObjectId | None] = Field(default_factory = dict)
    bonus: CostumeBonus = Field(default_factory = CostumeBonus)
    tls_background: RenamedFile | None = None
    subsets: list[GameObjectId] = Field(default_factory = list)

class CostumePartType(BaseModel):
    index: int
    id: GameObjectId
    category: Literal['costume_part'] = 'costume_part'
    image: ImageBase[Literal['alt']] = Field(default_factory = dict)
    model_name: str = ''
    linked_part: GameObjectId | None = None
    type: Literal['body', 'mane', 'tail'] = 'body'
    apply_time: int = 0
    materials: list[int] = Field(default_factory = list)
    gem_price: int = 0


class QuestDetail(BaseModel):
    name: TranslatableString
    description: TranslatableString
    pro: list[str] = Field(default_factory = list)
    special: Literal['seasonal', 'tutorial'] | None = None

class GroupQuests(BaseModel):
    random_pros: list[str] = Field(default_factory = list)
    quests: dict[str, QuestDetail] = Field(default_factory = dict)


type FortuneShopRarities = Literal['common', 'uncommon', 'rare']
type FortuneShopPrices = Literal['regular', 'discount', 'super', 'ultra']

class FortuneShopItemPricesList(BaseModel):
    regular: dict[FortuneShopPrices, int]
    royal: dict[FortuneShopPrices, int]

class FortuneShopItem(BaseModel):
    id: GameObjectId
    rarity: FortuneShopRarities
    amount: int
    prices: FortuneShopItemPricesList

class FortuneShop(BaseModel):
    max_items_in_shop: int = 6
    refresh_cost: int = 50
    item_rarity_chances: dict[FortuneShopRarities, float] = Field(default_factory = dict)
    item_price_chances: dict[FortuneShopPrices, float] = Field(default_factory = dict)
    items: dict[FortuneShopRarities, dict[GameObjectId, FortuneShopItem]] = Field(default_factory = dict)


class CategoryData[T](BaseModel):
    objects: dict[GameObjectId, T] = Field(default_factory = dict)


type CategoryName = Literal[
    'pony',
    'house',
    'shop',
    'decor',
    'avatar',
    'avatar_frame',
    'background',
    'background_frame',
    'cutie_mark',
    'pet',
    'theme',
    'path',
    'item',
    'booster',
    'token',
    'consumable',
    'costume',
    'costume_part',
]

CATEGORY_NAMES: list[CategoryName] = [
    'pony',
    'house',
    'shop',
    'decor',
    'avatar',
    'avatar_frame',
    'background',
    'background_frame',
    'cutie_mark',
    'pet',
    'theme',
    'path',
    'item',
    'booster',
    'token',
    'consumable',
    'costume',
    'costume_part',
]

class GameObjects(BaseModel):
    pony: CategoryData[PonyType] = Field(default_factory = CategoryData[PonyType])
    house: CategoryData[HouseType] = Field(default_factory = CategoryData[HouseType])
    shop: CategoryData[ShopType] = Field(default_factory = CategoryData[ShopType])
    decor: CategoryData[DecorType] = Field(default_factory = CategoryData[DecorType])
    avatar: CategoryData[AvatarType] = Field(default_factory = CategoryData[AvatarType])
    avatar_frame: CategoryData[AvatarFrameType] = Field(default_factory = CategoryData[AvatarFrameType])
    background: CategoryData[BackgroundType] = Field(default_factory = CategoryData[BackgroundType])
    background_frame: CategoryData[BackgroundFrameType] = Field(default_factory = CategoryData[BackgroundFrameType])
    cutie_mark: CategoryData[CutieMarkType] = Field(default_factory = CategoryData[CutieMarkType])
    pet: CategoryData[PetType] = Field(default_factory = CategoryData[PetType])
    theme: CategoryData[ThemeType] = Field(default_factory = CategoryData[ThemeType])
    path: CategoryData[PathType] = Field(default_factory = CategoryData[PathType])
    item: CategoryData[ItemType] = Field(default_factory = CategoryData[ItemType])
    booster: CategoryData[BoosterType] = Field(default_factory = CategoryData[BoosterType])
    token: CategoryData[TokenType] = Field(default_factory = CategoryData[TokenType])
    consumable: CategoryData[ConsumableType] = Field(default_factory = CategoryData[ConsumableType])
    costume: CategoryData[CostumeType] = Field(default_factory = CategoryData[CostumeType])
    costume_part: CategoryData[CostumePartType] = Field(default_factory = CategoryData[CostumePartType])

class GameVersion(BaseModel):
    game_version: str = Field(default = '')
    content_version: str = Field(default = '')
