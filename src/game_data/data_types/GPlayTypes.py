from typing import TypedDict

class GPlayFile(TypedDict):
    url: str
    cookies: dict[str, str]

class GPlayAPKSplit(TypedDict):
    name: str
    sha1: str
    sha256: str
    downloadSize: int
    compressedSize: int
    file: GPlayFile

class GPlayAPKDetails(TypedDict):
    docid: str
    additionalData: list
    splits: list[GPlayAPKSplit]
    file: GPlayFile
