from typing import Any, Literal, TypedDict, NotRequired, TypeVarTuple, TypeVar


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

class RenamedFile(TypedDict):
    path: str
    original: str

type ImageBase[T] = dict[T | Literal['main'], RenamedFile]

class StarReward(TypedDict):
    item: str
    amount: int

class PriceBase(TypedDict):
    currency: Currency | None
    amount: int

class Price(TypedDict):
    base: PriceBase
    token: GameObjectId | None
    daily_goals: int

class GenericObjectType(TypedDict):
    index: int
    id: str
    name: TranslatableString
    preferred_name: NotRequired[TranslatableString]
    alt_name: NotRequired[AltName]
    price: NotRequired[Price]
    tags: NotRequired[list[str]]
    image: ImageBase

# class PonyImage(ImageBase):
#     portrait: RenamedFile

class ChangelingData(TypedDict):
    id: str
    IAmAlterSet: bool

class MinigameData(TypedDict):
    can_play_minecart: bool
    can_play_minigames: bool
    cooldown: int
    skip_cost: int
    exp_rank: int
    has_wings: bool

class TaskData(TypedDict):
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
    category: Literal['pony']
    note: dict[str, Any]
    description: TranslatableString
    image: ImageBase[Literal['portrait']]
    location: Location
    house: str
    inns: list[GameObjectId]
    changeling: ChangelingData
    group_master: bool
    group: list[str]
    max_level: bool
    rewards: list[StarReward]
    minigame: MinigameData
    arrival_xp: int
    unlock_level: int
    tasks: list[str]
    pro: str | None
    collections: list[str]
    wiki_path: str

class HouseBuild(TypedDict):
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

class ShopProduct(TypedDict):
    name: TranslatableString
    image: str
    time: int
    skip_cost: int
    xp: int
    bits: int
    gems: int
    tls: int

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

class DecorPro(TypedDict):
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

class FarmCost(TypedDict):
    shard: GameObjectId
    shard_cost: int
    item: GameObjectId
    item_cost: int

class CritterUpgrade(TypedDict):
    currency: GameObjectId
    cost: int
    shard: GameObjectId
    shard_cost: int

class ConsumableCritter(TypedDict):
    main_feed: GameObjectId
    additional_feed: GameObjectId
    phases: list[dict[Literal['main', 'additional'], int]]
    upgrade: CritterUpgrade
    final_cooldown: int

class ConsumableType(GenericObjectType):
    category: Literal['consumable']
    consume: dict[Literal['xp', 'bits', 'gems', 'hearts', 'wheels', 'blitz_energy', 'tls'], int]
    farm: NotRequired[list[FarmCost]]
    critter: NotRequired[ConsumableCritter]

class CostumeBonus(TypedDict):
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

class CostumePartType(TypedDict):
    category: Literal['costume_part']
    image: ImageBase[Literal['alt']]
    model_name: str
    LinkedPart: GameObjectId | None
    type: Literal['body', 'mane', 'tail']
    apply_time: int
    gem_price: int


type GameObject = PonyType | HouseType | ShopType | DecorType | ItemType | TokenType | AvatarType | GenericObjectType


class QuestDetail(TypedDict):
    name: TranslatableString
    description: TranslatableString
    pro: list[str]
    special: Literal['seasonal', 'tutorial'] | None

class GroupQuests(TypedDict):
    random_pros: list[str]
    quests: dict[str, QuestDetail]


type FortuneShopRarities = Literal['rare', 'common', 'uncommon']
type FortuneShopPrices = Literal['regular', 'discount', 'super', 'ultra']

class FortuneShopItemPricesList(TypedDict):
    regular: dict[FortuneShopPrices, int]
    royal: dict[FortuneShopPrices, int]

class FortuneShopItem(TypedDict):
    id: GameObjectId
    rarity: FortuneShopRarities
    amount: int
    prices: FortuneShopItemPricesList

class FortuneShop(TypedDict):
    max_items_in_shop: int
    refresh_cost: int
    item_rarity_chances: dict[FortuneShopRarities, float]
    item_price_chances: dict[FortuneShopPrices, float]
    items: dict[FortuneShopRarities, dict[GameObjectId, FortuneShopItem]]


class CategoryData[T](TypedDict):
    objects: dict[GameObjectId, T]

class CategoryDataPony(CategoryData[PonyType]):
    # clones: dict[str, Any]
    pass

class GameObjects(TypedDict):
    pony: CategoryData[PonyType]
    house: CategoryData[HouseType]
    shop: CategoryData[ShopType]
    decor: CategoryData[DecorType]
    avatar: CategoryData[AvatarType]
    avatar_frame: CategoryData[AvatarFrameType]
    background: CategoryData[BackgroundType]
    background_frame: CategoryData[BackgroundFrameType]
    pet: CategoryData[PetType]
    theme: CategoryData[ThemeType]
    path: CategoryData[PathType]
    item: CategoryData[ItemType]
    booster: CategoryData[BoosterType]
    token: CategoryData[TokenType]
    consumable: CategoryData[ConsumableType]
    costume: CategoryData[CostumeType]
    costume_part: CategoryData[CostumePartType]

class GameDataType(TypedDict):
    file_version: int
    game_version: str
    content_version: str
    categories: GameObjects
    group_quests: GroupQuests
    fortune_shop: FortuneShop
