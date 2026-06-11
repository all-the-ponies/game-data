from typing import TypedDict, Literal, NotRequired, Any

type UpdateType = Literal['app', 'content']

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
    message: dict[UpdateType, DiscordMessage]

class NtfyConfig(TypedDict):
    name: str
    token: NotRequired[str]
    topic: str
    message: dict[UpdateType, dict[str, Any]]


class NotificationConfig(TypedDict):
    discord: NotRequired[list[DiscordConfig]]
    ntfy: NotRequired[list[NtfyConfig]]

