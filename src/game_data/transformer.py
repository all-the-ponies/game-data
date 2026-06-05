from dataclasses import dataclass, field
from glob import glob
import json
import os
from pathlib import Path
from typing import Literal
import urllib.parse

from PIL import Image
from lxml import etree

from luna_kit.gameobjectdata import GameObjectData, ShopItem
from luna_kit.loc import LOC
from luna_kit.pvr import PVR
from luna_kit.typings import DefaultGameCampaignType
from luna_kit.xml import parse_xml

from .GameDataTypes import *
from .console import console, track
from .crop import crop_image
from .utils import strToInt


@dataclass
class GameData:
    game_version: GameVersion = field(default_factory = GameVersion)
    game_objects: GameObjects = field(default_factory = GameObjects)
    group_quests: GroupQuests = field(default_factory = GroupQuests)
    fortune_shop: FortuneShop = field(default_factory = FortuneShop)


NPC_PONIES = [
    "Pony_Derpy", # derpy box, not playable muffins
    'Pony_Disguised_Spike',
    "Pony_Chest",
    'Pony_Tirek', # Not the playable tirek
    'Pony_Tirek_TOTB',
    'Pony_Windigo', # unobtainable
]

QUEST_PONIES = [
    'Pony_Quest_Duplicate_Starlight',
    'Pony_Quest_Duplicate_Discord',
    'Pony_Quest_Duplicate_Trixie',
    'Pony_Quest_Duplicate_Thorax',
    'Pony_Quest_Fluttershy_Duplicate',
    'Pony_Quest_Duplicate_Scootaloo',
    'Pony_Quest_Duplicate_Sweetiebelle',
    'Pony_Quest_Duplicate_Apple_Bloom',
    'Pony_Quest_Changeling_Runaway_01',
    'Pony_Quest_Changeling_Runaway_02',
]

UNUSED_PONIES = [
    'Pony_Twilight_Sneak_Le',
    'Pony_Camo_Dash',
    'Pony_Wingless_Rainbow_Dash',
    'Pony_Crystal_Luna_Hair_Test',
    'Pony_Token_Test',
]

LOCATIONS = {
    0: 'PONYVILLE',
    1: 'CANTERLOT',
    2: 'SWEET_APPLE_ACRES',
    3: 'EVERFREE_FOREST',
    4: 'CRYSTAL_EMPIRE',
    5: 'CHANGELING_KINGDOM',
    6: 'KLUGETOWN',
}

CURRENCY = {
    1: 'Bits',
    2: 'Gems',
}


def encode_wiki_path(name: str) -> str:
    return urllib.parse.quote(name.replace(' ', '_'))


class Transformer:
    game_data: GameData
    
    def __init__(
        self,
        game_folder: str | Path,
        output_folder: str | Path,
        override_folder: str | Path,
        version: str,
    ) -> None:
        self.game_folder = Path(game_folder)
        self.output_folder = Path(output_folder)
        self.images_folder = self.output_folder/'images'
        self.game_objects_folder = self.images_folder/'game_objects'
        self.override_folder = Path(override_folder)

        self.output_folder.mkdir(parents = True, exist_ok = True)
        self.images_folder.mkdir(parents = True, exist_ok = True)
        self.game_objects_folder.mkdir(parents = True, exist_ok = True)

        self.gameObjectData = GameObjectData(
            self.game_folder/'gameobjectdata.xml',
            self.game_folder/'shopdata.xml',
            self.game_folder/'gameobjectcategorydata.xml',
        )

        with open(
            self.game_folder/'defaultGameCampaign.json',
            'r',
            encoding = 'utf-8',
        ) as file:
            self.defaultGameCampaign: DefaultGameCampaignType = json.load(file)
        
        self.locs: dict[Language, LOC] = {(loc := LOC(str(filename)))['DEV_ID']: loc for filename in self.game_folder.glob('*.loc')}

        self.daily_goals_shop = {
            item['item_id']: item['cost']
            for item in self.defaultGameCampaign.get('mini_games', {}).get('dailygoals', {}).get('itemshop', [])
        }

        self.override_data = {}
        if (self.override_folder/'game-data.json').exists():
            with (self.override_folder/'game-data.json').open('r', encoding = 'utf-8') as file:
                self.override_data = json.load(file)
        
        content_version: str = parse_xml(self.game_folder/'data_ver.xml')[0].get('Value')
        
        self.game_data = GameData()
        self.game_data.game_version.game_version = version
        self.game_data.game_version.content_version = content_version

    def start(self):
        self.get_game_objects()

    def save(self):
        console.log('Saving files')
        with open(self.output_folder/'game_version.json', 'w', encoding = 'utf-8') as file:
            file.write(self.game_data.game_version.to_json(ensure_ascii = False))
        with open(self.output_folder/'game_objects.json', 'w', encoding = 'utf-8') as file:
            file.write(self.game_data.game_objects.to_json(ensure_ascii = False, indent = 2))
    
    def get_game_objects(self):
        self.get_category_pony()
        self.get_category_house()
        self.get_category_shop()
        self.get_category_decor()
        self.get_category_avatar()
        self.get_category_avatar_frame()
        self.get_category_background()
        self.get_category_background_frame()
        self.get_category_pet()
        self.get_category_theme()
        self.get_category_path()
        self.get_category_item()
        self.get_category_booster()
        self.get_category_token()
        self.get_category_consumable()
        self.get_category_costume()
        self.get_category_costume_part()
    
    def get_category_pony(self):
        ponies = self.game_data.game_objects.pony.objects

        
        for hidden_pony in self.gameObjectData['HiddenPony'].values():
            pony_id = hidden_pony.get('Parent', {}).get('PonyName')
            if pony_id and pony_id not in NPC_PONIES:
                NPC_PONIES.append(pony_id)
            
        main_images = self.game_objects_folder/'pony/main'
        portrait_images = self.game_objects_folder/'pony/portrait'
        main_images.mkdir(parents = True, exist_ok = True)
        portrait_images.mkdir(parents = True, exist_ok = True)

        groups = {}

        for index, pony in enumerate(track(
            self.gameObjectData['Pony'].values(),
            description = 'Getting ponies...',
        )):
            try:
                shop_data = self.gameObjectData.get_object_shopdata(pony.id)
                pony_info = PonyType(
                    index = index,
                    id = pony.id,
                    name = self.translate_string(pony.get('Name', {}).get('Unlocal', pony.id)),
                    description = self.translate_string(pony.get('Description', {}).get('Unlocal', '')),
                    image = {},
                    alt_name = {},
                    preferred_name = {},
                )

                ponies[pony.id] = pony_info


                if pony.id in UNUSED_PONIES and 'unused' not in pony_info.tags:
                    pony_info.tags.append('unused')
                if pony.id in NPC_PONIES and 'npc' not in pony_info.tags:
                    pony_info.tags.append('npc')
                if pony.id in QUEST_PONIES and 'quest' not in pony_info.tags:
                    pony_info.tags.append('quest')

                # images

                pony_info.image['portrait'] = self.add_image(
                    [pony.get('Icon', {}).get('Url', '')],
                    portrait_images/(pony.id + '.png'),
                )

                pony_info.image['main'] = self.add_image(
                    [pony.get('Shop', {}).get('Icon', '')],
                    main_images/(pony.id + '.png'),
                )


                # General stuff

                location: int = -1
                if shop_data is not None:
                    shopdata_location: str = shop_data.get('MapZone', '-1')
                    shopdata_location = shopdata_location.split(',')[0]
                    location = strToInt(shopdata_location)
                else:
                    location = pony.get('House', {}).get('HomeMapZone', -1)

                pony_info.location = LOCATIONS.get(
                    location, # type: ignore
                    'UNKNOWN',
                )
                pony_info.house = pony.get('House', {}).get('Type')

                
                changeling = pony.get('IsChangelingWithSet', {}).get('AltPony', None)
                if changeling:
                    pony_info.changeling.id = changeling
                    pony_info.changeling.IAmAlterSet = pony.get('IsChangelingWithSet', {}).get('IAmAlterSet', False)

                group: list[str] = pony.get('Friends', {}).get('Friend', [])
                group = list(filter(lambda id: id != '', group))
                if len(group):
                    group.insert(0, pony.id)
                    pony_info.group_master = True
                
                for id in group:
                    groups[id] = group
                
                pony_info.group = group

                pony_info.ai_type = pony.get('AI', {}).get('Special_AI', 0)
                pony_info.max_level = pony.get('AI', {}).get('Max_Level', False)

                for prize_id, amount in zip(
                    pony.get('StarRewards', {}).get('ID', []),
                    pony.get('StarRewards', {}).get('Amount', []),
                ):
                    pony_info.rewards.append(StarReward(
                        item = prize_id,
                        amount = amount,
                    ))
                
                # extra metadata

                
                pony_info.minigame.can_play_minecart = pony.get('Minigames', {}).get('CanPlayMineCart', True)
                pony_info.minigame.hard_lock = pony.get('MGHardLock', {}).get('Lock', False)
                pony_info.minigame.cooldown = pony.get('Minigames', {}).get('TimeBetweenPlayActions', 0)
                pony_info.minigame.skip_cost = pony.get('Minigames', {}).get('PlayActionSkipAgainCost', 0)
                pony_info.minigame.exp_rank = pony.get('Minigames', {}).get('EXP_Rank', 0) # Not sure what this is, but I'll keep it
                pony_info.minigame.has_wings = not pony.get('Minigames', {}).get('NoWings', True)

                pony_info.arrival_xp = pony.get('OnArrive', {}).get('EarnXP', 0)
                pony_info.unlock_level = shop_data.get('UnlockValue', 0)
                pony_info.not_pony = pony.get('Misc', {}).get('IsNotPony', False)
                pony_info.ban_pets = pony.get('Misc', {}).get('BenPets', False)

                if shop_data:
                    pony_info.price = self.get_price(shop_data)
                
                pony_info.wiki_path = encode_wiki_path(pony_info.name['english'])


            except Exception as e:
                e.add_note(f'Pony: {pony.id}')
        
        for pony_id, group in groups.items():
            ponies[pony_id].group = group

    def get_category_house(self):
        ...

    def get_category_shop(self):
        ...

    def get_category_decor(self):
        ...

    def get_category_avatar(self):
        ...

    def get_category_avatar_frame(self):
        ...

    def get_category_background(self):
        ...

    def get_category_background_frame(self):
        ...

    def get_category_pet(self):
        ...

    def get_category_theme(self):
        ...

    def get_category_path(self):
        ...

    def get_category_item(self):
        ...

    def get_category_booster(self):
        ...

    def get_category_token(self):
        ...

    def get_category_consumable(self):
        ...

    def get_category_costume(self):
        ...

    def get_category_costume_part(self):
        ...

    
    def translate_string(self, key: str) -> TranslatableString:
        return {lang: loc.translate(key).strip().replace('|', '') for lang, loc in self.locs.items()}
    
    def add_image(self, game_paths: list[str], dest: str | Path) -> RenamedFile:
        used_game_name: str | None = None
        dest = Path(dest)
        image: Image.Image | None = None

        for filename in game_paths:
            name = os.path.splitext(filename)[0]

            if os.path.exists(self.game_folder/(name + '.png')):
                image = Image.open(self.game_folder/(name + '.png'))
            elif os.path.exists(self.game_folder/(name + '.pvr')):
                image = PVR(self.game_folder/(name + '.png')).image
            
            if image is not None:
                used_game_name = filename
                break
        
        if image is not None:
            image = crop_image(image)
            image.save(dest)
        
        return RenamedFile(dest.relative_to(self.output_folder).as_posix(), used_game_name)
    
    def get_price(self, shopdata: ShopItem):
        price = Price()

        price.base.currency = CURRENCY.get(shopdata.get('CurrencyType', 0))
        price.base.amount = shopdata.get('Cost', 0)

        price.token = shopdata.get('TaskTokenID')
        price.daily_goals = self.daily_goals_shop.get(shopdata.id, 0)

