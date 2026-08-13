
from dataclasses import dataclass, field
import json
import os
from pathlib import Path

from .GameDataTypes import (
    CATEGORY_NAMES,
    CategoryData,
    CollectionData,
    FortuneShop,
    GameObject,
    GameObjects,
    GameVersion,
    GroupQuests,
    MazeData,
    TasksData,
)
from .common_types import GameObjectId, LANGUAGES, Language
from . import QuestDataTypes
from . import CinematicTypes

@dataclass
class GameData:
    game_version: GameVersion = field(default_factory = GameVersion)
    game_objects: GameObjects = field(default_factory = GameObjects)
    group_quests: GroupQuests = field(default_factory = GroupQuests)
    fortune_shop: FortuneShop = field(default_factory = FortuneShop)
    tasks_data: TasksData = field(default_factory = TasksData)
    collection_data: CollectionData = field(default_factory = CollectionData)
    maze_data: MazeData = field(default_factory = MazeData)

    quest_data: QuestDataTypes.QuestData = field(default_factory = QuestDataTypes.QuestData)
    cinematic_data: CinematicTypes.CinematicData = field(default_factory = CinematicTypes.CinematicData)

    locales: dict[Language, dict[str, str]] = field(default_factory = lambda: {lang: {} for lang in LANGUAGES})

    def save(self, dist_folder: str | Path):
        dist_folder = Path(dist_folder)
        locales_folder = dist_folder/'locales'

        locales_folder.mkdir(parents = True, exist_ok = True)
        
        for lang, strings in self.locales.items():
            with open(locales_folder/f'{LANGUAGES[lang]}.json', 'w') as file:
                json.dump(strings, file, indent = 2, ensure_ascii = False)
        
        with open(dist_folder/'game_version.json', 'w', encoding = 'utf-8') as file:
            file.write(self.game_version.model_dump_json(ensure_ascii = False))
        with open(dist_folder/'game_objects.json', 'w', encoding = 'utf-8') as file:
            file.write(self.game_objects.model_dump_json(ensure_ascii = False, indent = 2))
        with open(dist_folder/'group_quests.json', 'w', encoding = 'utf-8') as file:
            file.write(self.group_quests.model_dump_json(ensure_ascii = False, indent = 2))
        with open(dist_folder/'fortune_shop.json', 'w', encoding = 'utf-8') as file:
            file.write(self.fortune_shop.model_dump_json(ensure_ascii = False, indent = 2))
        with open(dist_folder/'tasks_data.json', 'w', encoding = 'utf-8') as file:
            file.write(self.tasks_data.model_dump_json(ensure_ascii = False, indent = 2))
        with open(dist_folder/'collection_data.json', 'w', encoding = 'utf-8') as file:
            file.write(self.collection_data.model_dump_json(ensure_ascii = False, indent = 2))
        with open(dist_folder/'maze_data.json', 'w', encoding = 'utf-8') as file:
            file.write(self.maze_data.model_dump_json(ensure_ascii = False, indent = 2))

        with open(dist_folder/'quest_data.json', 'w', encoding = 'utf-8') as file:
            file.write(self.quest_data.model_dump_json(ensure_ascii = False, indent = 2))
        with open(dist_folder/'cinematic_data.json', 'w', encoding = 'utf-8') as file:
            file.write(self.cinematic_data.model_dump_json(ensure_ascii = False, indent = 2))
    
    @classmethod
    def load(cls, dist_folder: str | Path):
        dist_folder = Path(dist_folder)
        locales_folder = dist_folder/'locales'

        locales: dict[Language, dict[str, str]] = {}

        for lang, code in LANGUAGES.items():
            if (locales_folder/f'{code}.json').is_file():
                with open(locales_folder/f'{code}.json', 'r') as file:
                    locales[lang] = json.load(file)
            else:
                locales[lang] = {}

        game_version = GameVersion.model_validate_json((dist_folder/'game_version.json').read_bytes())
        game_objects = GameObjects.model_validate_json((dist_folder/'game_objects.json').read_bytes())
        group_quests = GroupQuests.model_validate_json((dist_folder/'group_quests.json').read_bytes())
        fortune_shop = FortuneShop.model_validate_json((dist_folder/'fortune_shop.json').read_bytes())
        tasks_data = TasksData.model_validate_json((dist_folder/'tasks_data.json').read_bytes())
        collection_data = CollectionData.model_validate_json((dist_folder/'collection_data.json').read_bytes())
        maze_data = MazeData.model_validate_json((dist_folder/'maze_data.json').read_bytes())
        quest_data = QuestDataTypes.QuestData.model_validate_json((dist_folder/'quest_data.json').read_bytes())
        cinematic_data = CinematicTypes.CinematicData.model_validate_json((dist_folder/'cinematic_data.json').read_bytes())
        
        return cls(
            game_version = game_version,
            game_objects = game_objects,
            group_quests = group_quests,
            fortune_shop = fortune_shop,
            tasks_data = tasks_data,
            collection_data = collection_data,
            maze_data = maze_data,

            quest_data = quest_data,
            cinematic_data = cinematic_data,

            locales = locales,
        )
    
    def get_object(self, id: GameObjectId) -> GameObject | None:
        result: GameObject | None = None

        for category_name in CATEGORY_NAMES:
            category: CategoryData = getattr(self.game_objects, category_name)

            if id in category.objects:
                result = category.objects[id]
                break
        
        return result
