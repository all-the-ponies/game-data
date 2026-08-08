from typing import Literal, Optional

from pydantic import BaseModel


type GameObjectId = str
type StringId = str
type CinematicId = str

type Language = Literal[
    "arabic",
    "chinese",
    "english",
    "french",
    "german",
    "italian",
    "japanese",
    "korean",
    "brazilian portuguese",
    "russian",
    "spanish",
    "thai",
    "turkish",
]

LANGUAGES: dict[Language, str] = {
    "english": "en",
    "arabic": "ar",
    "chinese": "zh",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "japanese": "ja",
    "korean": "ko",
    "brazilian portuguese": "pt-BR",
    "russian": "ru",
    "spanish": "es",
    "thai": "th",
    "turkish": "tr",
}

type Location = Literal[
    "PONYVILLE",
    "CANTERLOT",
    "SWEET_APPLE_ACRES",
    "EVERFREE_FOREST",
    "CRYSTAL_EMPIRE",
    "CHANGELING_KINGDOM",
    "KLUGETOWN",
    "MAZE",
    "UNKNOWN",
]

type Currency = Literal["Gems", "Bits"] | GameObjectId

type TranslatableString = dict[Language, str]
type AltName = dict[Language, list[str]]


class RenamedFile(BaseModel):
    path: str = ""
    original: Optional[str] = None


type ImageBase[T] = dict[T | Literal["main"], RenamedFile]
