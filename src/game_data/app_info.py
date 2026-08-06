from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import html
import os

import google_play_scraper as gplay
from playstoreapi.config import config, getDevicesCodenames, getDevicesReadableNames
from playstoreapi.googleplay import GooglePlayAPI, LoginError
import requests

from luna_kit.api import Version

from .console import console


PACKAGE_NAME = "com.gameloft.android.ANMP.GloftPOHM"
GPLAY_CONFIG_PATH = 'config/gplay.json'

def unescape_text(s: str):
    return html.unescape(s.replace("<br>", "\n"))

@dataclass
class AppInfo:
    version: str
    release_notes: str
    raw_release_notes: str
    icon_url: str

def get_gplay_api_details():
    api = GooglePlayAPI('en_US', 'UTC', device_codename = 'gplayapi_px_9a')
    
    try:
        api.envLogin(config_paths = [GPLAY_CONFIG_PATH], quiet = True)
        console.print('Logged into google play')
        if not os.path.exists(GPLAY_CONFIG_PATH):
            api.saveConfig(config_path = GPLAY_CONFIG_PATH)
            console.print(f'[green]Google play api config saved to "{GPLAY_CONFIG_PATH}"[/]')
            
    except LoginError:
        if not os.path.exists(GPLAY_CONFIG_PATH):
            console.print('[red]Cannot use google play api[/]')
            return
        
        raise

    details = api.details(PACKAGE_NAME)
    icon_url: str = ''

    for image in details['image']:
        if image.get('imageType') == 4:
            if image.get('imageUrl'):
                icon_url = image['imageUrl']
                break

    return AppInfo(
        version = details['details']['appDetails']['versionString'],
        raw_release_notes = details['details']['appDetails']['recentChangesHtml'],
        release_notes = unescape_text(details['details']['appDetails']['recentChangesHtml']),
        icon_url = icon_url,
    )

def get_gplay_scrape_details():
    app_info = gplay.app(PACKAGE_NAME)

    return AppInfo(
        version = app_info['version'],
        raw_release_notes = app_info['recentChanges'],
        release_notes = app_info['recentChangesHTML'],
        icon_url = app_info['icon'],
    )

def get_apkmirror_details():
    response = requests.post(
        "https://www.apkmirror.com/wp-json/apkm/v1/app_exists?pnames=com.gameloft.android.ANMP.GloftPOHM",
        headers = {
            "User-Agent": "APKUpdater-v3.0.3",
            # This is a key from APKUpdater https://github.com/rumboalla/apkupdater/issues/58#issuecomment-309238684
            "Authorization": "Basic YXBpLWFwa3VwZGF0ZXI6cm01cmNmcnVVakt5MDRzTXB5TVBKWFc4"
        }
    )
    response.raise_for_status()

    raw_app_info = response.json()
    return AppInfo(
        version = raw_app_info['data'][0]['release']['version'],
        raw_release_notes = raw_app_info['data'][0]['release']['whats_new'],
        release_notes = unescape_text(raw_app_info['data'][0]['release']['whats_new']),
        icon_url = raw_app_info['data'][0]['app']['icon_url'],
    )


def get_app_info():
    with ThreadPoolExecutor(max_workers = 3) as threader:
        futures = [
            threader.submit(get_gplay_api_details),
            threader.submit(get_gplay_scrape_details),
            threader.submit(get_apkmirror_details),
        ]

        infos = filter(lambda details: details is not None, [future.result() for future in futures])

    return sorted(
        infos,
        key = lambda details: Version.parse(details.version),
        reverse = True,
    )[0]
