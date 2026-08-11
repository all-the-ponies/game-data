from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import html
import os

import google_play_scraper as gplay
from playstoreapi.config import config, getDevicesCodenames, getDevicesReadableNames
from playstoreapi.googleplay import GooglePlayAPI, LoginError
import requests
import json

from luna_kit.api import Version

from .console import console
from .s3 import get_secret_s3_client
from .utils import json_dumps_compact


PACKAGE_NAME = "com.gameloft.android.ANMP.GloftPOHM"
GPLAY_CONFIG_PATH = '.playstoreapi'
GPLAY_CONFIG_KEY = 'gplay/gplay_config.json'

def unescape_text(s: str):
    return html.unescape(s.replace("<br>", "\n"))

@dataclass
class AppInfo:
    version: str
    release_notes: str
    raw_release_notes: str
    icon_url: str

def get_gplay_api(bucket: str | None):
    api = GooglePlayAPI('en_US', 'UTC', device_codename = 'gplayapi_px_9a')

    s3_client = get_secret_s3_client(bucket = bucket) if bucket else None

    config: dict | None = None

    if os.path.exists(GPLAY_CONFIG_PATH):
        with open(GPLAY_CONFIG_PATH, 'r') as file:
            config = json.load(file)

    elif s3_client and bucket:
        try:
            config_object = s3_client.get_object(
                Bucket = bucket,
                Key = GPLAY_CONFIG_KEY,
            )

            config = json.load(config_object['Body'])
        except:
            console.print('Cannot get google play config')
    
    dispenser_url = os.environ.get('PLAYSTORE_DISPENSER_URL')
    
    try:
        logged_in = False
        if config:
            try:
                api.login(
                    gsfId = config['gsfId'],
                    authSubToken = config['authSubToken'],
                    check = True,
                    deviceCheckinConsistencyToken = config['deviceCheckinConsistencyToken'],
                    deviceConfigToken = config['deviceConfigToken'],
                    dfeCookie = config['dfeCookie'],
                )
                logged_in = True
            except:
                pass

        if not logged_in and dispenser_url:
            api.login(
                anonymous = True,
                tokenDispenser = dispenser_url,
            )
        elif not api.gsfId:
            console.print('Cannot log into google play')
            return

        console.print('Logged into google play')
        
            
    except LoginError as e:
        if not dispenser_url:
            console.print('[red]Cannot use google play api[/]')
            return
        
        e.add_note(f'Dispenser: {dispenser_url}')

        raise
    
    config = {
        "authSubToken": api.authSubToken,
        "gsfId": api.gsfId,
        "deviceCheckinConsistencyToken": api.deviceCheckinConsistencyToken,
        "deviceConfigToken": api.deviceConfigToken,
        "dfeCookie": api.dfeCookie,
    }

    config_data = json_dumps_compact(config)
    with open(GPLAY_CONFIG_PATH, 'w', encoding = 'utf-8') as file:
        file.write(config_data)
    
    if s3_client and bucket:
        console.print('Saving gplay config to s3')
        s3_client.put_object(
            Bucket = bucket,
            Key = GPLAY_CONFIG_KEY,
            Body = config_data.encode('utf-8'),
            ContentType = 'application/json',
        )
    else:
        console.print('Cannot save gplay config to s3', s3_client, bucket)
    
    return api

def get_gplay_api_details(bucket: str | None = None):

    api = get_gplay_api(bucket = bucket)

    if not api:
        return
    

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


def get_app_info(bucket: str | None = None):
    with ThreadPoolExecutor(max_workers = 3) as threader:
        futures = [
            threader.submit(get_gplay_api_details, bucket = bucket),
            threader.submit(get_gplay_scrape_details),
            threader.submit(get_apkmirror_details),
        ]

        infos = filter(lambda details: details is not None, [future.result() for future in futures])

    return sorted(
        infos,
        key = lambda details: Version.parse(details.version),
        reverse = True,
    )[0]
