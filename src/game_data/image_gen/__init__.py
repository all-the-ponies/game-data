from pathlib import Path

from ..data_types import GameData
from .collection import CollectionImageGenerator

def generate_images(game_data: GameData, dist: str | Path):
    CollectionImageGenerator(game_data, dist)
