from typing import TypedDict, Literal, NotRequired

class DiscordField(TypedDict):
    name: str
    value: str
    inline: bool

class DiscordMessage(TypedDict):
    roles: list[str]
    title: str
    message: str
    fields: NotRequired[list[DiscordField]]

class DiscordConfig(TypedDict):
    name: str
    webhook: str
    message: dict[Literal['app', 'content'], DiscordMessage]

class NotificationConfig(TypedDict):
    discord: NotRequired[list[DiscordConfig]]
