from dataclasses import dataclass, field
from glob import glob
import json
import os
from pathlib import Path
from typing import Literal

from PIL import Image
from lxml import etree

from luna_kit.gameobjectdata import GameObjectData
from luna_kit.loc import LOC
from luna_kit.pvr import PVR
from luna_kit.typings import DefaultGameCampaignType
from luna_kit.xml import parse_xml

from .GameDataTypes import GameDataType, GameObjects, GroupQuests, FortuneShop
from .console import console
from .crop import crop_image


@dataclass
class GameData:
    game_version: dict[Literal['game_version', 'content_version'], str]
    game_objects: GameObjects
    group_quests: GroupQuests
    fortune_shop: FortuneShop

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
        self.override_folder = Path(override_folder)

        self.gameObjectData = GameObjectData(
            self.game_folder/'gameobjectdata.xml',
            os.path.join(self.game_folder, 'shopdata.xml'),
            os.path.join(self.game_folder, 'gameobjectcategorydata.xml'),
        )

        with open(
            self.game_folder/'defaultGameCampaign.json',
            'r',
            encoding = 'utf-8',
        ) as file:
            self.defaultGameCampaign: DefaultGameCampaignType = json.load(file)
        
        self.locs: list[LOC] = [LOC(filename) for filename in self.game_folder.glob('*.loc')]

        self.override_data = {}
        if (self.override_folder/'game-data.json').exists():
            with (self.override_folder/'game-data.json').open('r', encoding = 'utf-8') as file:
                self.override_data = json.load(file)
        
        content_version: str = parse_xml(self.game_folder/'data_ver.xml')[0].get('Value')
        
        self.game_data = GameData(
            game_version = {
                'game_version': version,
                'content_version': content_version,
            },
            game_objects = {
                'pony': {'objects': {}},
                'house': {'objects': {}},
                'shop': {'objects': {}},
                'decor': {'objects': {}},
                'avatar': {'objects': {}},
                'avatar_frame': {'objects': {}},
                'background': {'objects': {}},
                'background_frame': {'objects': {}},
                'pet': {'objects': {}},
                'theme': {'objects': {}},
                'path': {'objects': {}},
                'item': {'objects': {}},
                'booster': {'objects': {}},
                'token': {'objects': {}},
                'consumable': {'objects': {}},
                'costume': {'objects': {}},
                'costume_part': {'objects': {}},
            },
            group_quests = {
                'random_pros': [],
                'quests': {},
            },
            fortune_shop = {
                'max_items_in_shop': 6,
                'refresh_cost': 50,
                'item_price_chances': {},
                'item_rarity_chances': {},
                'items': {},
            }
        )

        
        
