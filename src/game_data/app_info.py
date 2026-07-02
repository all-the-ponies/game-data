from dataclasses import dataclass
import html

import google_play_scraper as gplay
import requests

PACKAGE_NAME = "com.gameloft.android.ANMP.GloftPOHM"

def unescape_text(s: str):
    return html.unescape(s.replace("<br>", "\r\n"))

@dataclass
class AppInfo:
    version: str
    release_notes: str
    raw_release_notes: str
    icon_url: str

def get_app_info():
    try:
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

    except requests.HTTPError:
        app_info = gplay.app(PACKAGE_NAME)

        return AppInfo(
            version = app_info['version'],
            raw_release_notes = app_info['recentChanges'],
            release_notes = app_info['recentChangesHTML'],
            icon_url = app_info['icon'],
        )
