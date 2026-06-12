import json
import os
import random
from typing import Literal
import uuid

import requests

from .console import console
from .env import is_dev
from .notifyTypes import NotificationConfig, UpdateType


class Notifier:
    config: NotificationConfig | None = None
    
    def __init__(
        self,
        version: str = '',
        release_notes: str = '',
        app_icon: str | None = None,
    ) -> None:
        self.version: str = version
        self.release_notes: str = release_notes
        self.app_icon = app_icon

        self.get_notification_config()


    def get_notification_config(self):
        raw_config = os.environ.get('NOTIFICATION_CONFIG')
        if not raw_config:
            config_file = 'notifications.dev.json' if is_dev() else 'notifications.json'
            if not os.path.exists(config_file):
                return
            
            with open(config_file, 'r', encoding = 'utf-8') as file:
                raw_config = file.read()
        
        self.config = json.loads(raw_config)
    
    def format_string[T: str | dict | list](self, string: T) -> T:
        if isinstance(string, str):
            return string.format(
                version = self.version,
                release_notes = self.release_notes,
            ) # type: ignore
        elif isinstance(string, dict):
            new = {}
            for key, value in string.items():
                if isinstance(value, (str, dict, list)):
                    value = self.format_string(value)
                new[key] = value
            return new # type: ignore
        elif isinstance(string, list):
            new = []
            for value in string:
                if isinstance(value, (str, dict, list)):
                    value = self.format_string(value)
                new.append(value)
            return new # type: ignore
        
        return string
    
    def notify(self, type: UpdateType):
        if not self.config:
            return
        
        self.notify_ntfy(type)
        self.notify_discord(type)
        
    def notify_ntfy(self, type: UpdateType):
        if not self.config:
            return
        
        for ntfy_config in self.config.get('ntfy', []):
            message_config = ntfy_config['message'].get(type)
            if not message_config:
                continue
            
            console.print(f'[yellow]ntfy {ntfy_config["name"]}[/]')
            
            body = {
                'topic': ntfy_config['topic'],
                **self.format_string(message_config),
            }


            headers = {
                'Content-Type': 'application/json'
            }
            if 'token' in ntfy_config:
                headers['Authorization'] = f'Bearer {ntfy_config["token"]}'

            failed = False
            try:
                response = requests.post('https://ntfy.sh/', data = json.dumps(body).encode(), headers = headers)
                failed = not response.ok
            except requests.HTTPError as e:
                failed = True
                console.print(e)
            
            if failed:
                console.print(body)
                console.print(f'[red]Failed to send to {ntfy_config['name']}[/]')

            
    
    def notify_discord(self, type: UpdateType):
        if not self.config:
            return
        
        for server in self.config.get('discord', []):
            message_config = server['message'].get(type)
            if not message_config or not server.get('webhook'):
                continue
            
            console.print(f'Notifying [yellow]{server['name']}[/]')

            body = {
                "username": "All The Ponies",
                'content': ' '.join(f'<@&{role}>' for role in message_config['roles']),
                "avatar_url": "https://all-the-ponies.com/favicon/favicon.png",
                "allowed_mentions": {
                    "parse": ["roles"],
                    "roles": []
                },
            }

            embed = {
                'title': self.format_string(message_config['title']),
                'description': self.format_string(message_config['message']),
                "color": 16739227,
                "thumbnail": {
                    "url": self.app_icon,
                },
                "fields": [],
            }

            for field in message_config.get("fields", []):
                embed['fields'].append({
                    'name': self.format_string(field.get('name')),
                    'value': self.format_string(field.get('value')),
                    'inline': field.get('inline'),
                })
            
            body['embeds'] = [embed]

            if type == 'app':
                body['components'] = [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "style": 5,
                                "label": "Google Play",
                                "url": "https://play.google.com/store/apps/details?id=com.gameloft.android.ANMP.GloftPOHM",
                                # "custom_id": str(uuid.uuid4()),
                            },
                            {
                                "type": 2,
                                "style": 5,
                                "label": "iOS App Store",
                                "url": "https://apps.apple.com/us/app/my-little-pony-magic-princess/id533173905",
                                # "custom_id": str(uuid.uuid4()),
                            }
                        ]
                    }
                ]
            
            failed = False
            try:
                response = requests.post(f'{server["webhook"]}?with_components=true', json = body)
                failed = not response.ok
            except requests.HTTPError as e:
                failed = True
                console.print(e)
            
            if failed:
                console.print(f'[red]Failed to send to {server['name']}[/]')
