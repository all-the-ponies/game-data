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
    name: TranslatableString = field(default_factory = dict)
    image: ImageBase = field(default_factory = dict)
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
    image: ImageBase[Literal['portrait']] = field(default_factory = dict)
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
    time: int = 0
    skip_cost: int = 0
    xp: int = 0

@dataclass
class HouseType(GenericObjectType):
    category: Literal['house'] = 'house'
    location: list[Location] = field(default_factory = list)
    grid_size: int = 0
    build: HouseBuild = field(default_factory = HouseBuild)
    residents: list[str] = field(default_factory = list)
    visitors: list[str] = field(default_factory = list)
    wiki_path: str = ''

@dataclass
class ShopType(GenericObjectType):
    category: Literal['shop'] = 'shop'
    grid_size: int = 0
    build: HouseBuild = field(default_factory = HouseBuild)
    residents: list[str] = field(default_factory = list)
    visitors: list[str] = field(default_factory = list)
    unlock_level: int = 0
    location: Location = 'UNKNOWN'
    product: GameObjectId = ''
    special: Literal['lotto', 'ck_entrance', 'ferris_wheel'] | None = None
    can_sell: bool = False
    cost: Price = field(default_factory = Price)
    wiki_path: str = ''

@dataclass
class DecorPro(DataClassJsonMixin):
    is_pro: bool = False
    size: int = 0
    time: int = 0
    bits: int = 0

@dataclass
class DecorType(GenericObjectType):
    category: Literal['decor'] = 'decor'
    location: Location = 'UNKNOWN'
    unlock_level: int = 0
    limit: int = 0
    grid_size: int = 0
    xp: int = 0
    fusion_points: int = 0
    pro: DecorPro = field(default_factory = DecorPro)

@dataclass
class ItemType(GenericObjectType):
    category: Literal['item'] = 'item'
    alt_ids: list[str] = field(default_factory = list)

@dataclass
class TokenType(GenericObjectType):
    category: Literal['token'] = 'token'
    consumable: GameObjectId = ''
    chance: float = 0
    tasks: list[str] = field(default_factory = list)
    unlimited: bool = False
    no_reset: bool = False
    special: int = 0

@dataclass
class AvatarType(GenericObjectType):
    category: Literal['avatar'] = 'avatar'
    image: ImageBase[Literal['preview']] = field(default_factory = dict)
    is_default: bool = False
    pony: str | None = None
    animated: bool = False

@dataclass
class AvatarFrameType(GenericObjectType):
    category: Literal['avatar_frame'] = 'avatar_frame'
    image: ImageBase[Literal['preview']] = field(default_factory = dict)
    is_default: bool = False
    animated: bool = False

@dataclass
class BackgroundType(GenericObjectType):
    category: Literal['background'] = 'background'
    image: ImageBase[Literal['preview']] = field(default_factory = dict)
    is_default: bool = False

@dataclass
class BackgroundFrameType(GenericObjectType):
    category: Literal['background_frame'] = 'background_frame'
    image: ImageBase[Literal['preview']] = field(default_factory = dict)
    is_default: bool = False

@dataclass
class CutieMarkType(GenericObjectType):
    category: Literal['cutie_mark'] = 'cutie_mark'
    pony: GameObjectId = ''
    is_default: bool = False

@dataclass
class PetType(GenericObjectType):
    category: Literal['pet'] = 'pet'
    pony: GameObjectId = ''
    flying: bool = False
    task_bonus: int = 0
    minecart_bonus: int = 0

@dataclass
class ThemeType(GenericObjectType):
    category: Literal['theme'] = 'theme'
    location: Location = 'UNKNOWN'
    season: str = ''
    shop_bonus: int = 0
    quest: str = ''
    texture_suffix: str = ''

@dataclass
class PathType(GenericObjectType):
    category: Literal['path'] = 'path'
    location: Location = 'UNKNOWN'
    sprite: str = ''

@dataclass
class BoosterType(GenericObjectType):
    category: Literal['booster'] = 'booster'
    type: Literal['xp', 'bits'] | None = None
    time: int = 0
    multiplier: int = 0

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
    critter: GameObjectId
    main_feed: GameObjectId
    additional_feed: GameObjectId
    phases: list[dict[Literal['main', 'additional'], int]]
    upgrade: CritterUpgrade
    final_cooldown: int
    final_reward: dict[Literal['gems', 'xp'], int]

@dataclass
class ConsumableType(GenericObjectType):
    category: Literal['consumable'] = 'consumable'
    consume: dict[Literal['xp', 'bits', 'gems', 'hearts', 'wheels', 'blitz_energy', 'tls'], int] = field(default_factory = dict)
    time: int = 0
    skip_cost: int = 0
    farm: Optional[list[FarmCost]] = OptionalField()
    critter: Optional[ConsumableCritter] = OptionalField()

@dataclass
class CostumeBonus(DataClassJsonMixin):
    type: Literal['MineCart', 'ShopProduction', 'MiniGames', ''] = ''
    amount: int = 0

@dataclass
class CostumeType(GenericObjectType):
    category: Literal['costume'] = 'costume'
    image: ImageBase[Literal['alt']] = field(default_factory = dict)
    enabled: bool = False
    can_be_new: bool = False
    is_subset: bool = False
    is_only_alternate_mesh: bool = False
    parts: dict[Literal['body', 'mane', 'tail'], GameObjectId | None] = field(default_factory = dict)
    bonus: CostumeBonus = field(default_factory = CostumeBonus)
    tls_background: RenamedFile | None = None
    subsets: list[GameObjectId] = field(default_factory = list)

@dataclass
class CostumePartType(DataClassJsonMixin):
    index: int
    id: GameObjectId
    category: Literal['costume_part'] = 'costume_part'
    image: ImageBase[Literal['alt']] = field(default_factory = dict)
    model_name: str = ''
    linked_part: GameObjectId | None = None
    type: Literal['body', 'mane', 'tail'] = 'body'
    apply_time: int = 0
    ingredients: list[int] = field(default_factory = list)
    gem_price: int = 0


@dataclass
class QuestDetail(DataClassJsonMixin):
    name: TranslatableString
    description: TranslatableString
    pro: list[str] = field(default_factory = list)
    special: Literal['seasonal', 'tutorial'] | None = None

@dataclass
class GroupQuests(DataClassJsonMixin):
    file_version: int = 1
    random_pros: list[str] = field(default_factory = list)
    quests: dict[str, QuestDetail] = field(default_factory = dict)


type FortuneShopRarities = Literal['common', 'uncommon', 'rare']
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
    cutie_mark: CategoryData[CutieMarkType] = field(default_factory = CategoryData[CutieMarkType])
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
