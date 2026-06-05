import os
from requests import HTTPError

from luna_kit.api import API

from .console import console

def download(output: str, version: str):
    os.makedirs(output, exist_ok = True)
    
    api = API('android', version)

    manifest = api.get_dlc_manifest()
    
    for file_info in manifest['dlc_items']:
        if not file_info['filename'].endswith('.ark'):
            console.print(f'Skipping {file_info['filename']}')
            continue
        
        if file_info['device_calibre'] not in ['all', 'veryhigh'] or not file_info['enabled']:
            continue

        output_path = os.path.join(output, file_info['filename'])
        try:
            console.print(f'Downloading [yellow]{file_info['filename']}[/]')
            with api.download_asset(
                file_info['filename'],
                output_path,
                stream = True,
                asset_hash = file_info['asset_hash'],
            ) as downloader:
                downloader.response.raise_for_status()
                downloader.full_download(console)
        except HTTPError:
            console.print(f'[red]Failed to download {file_info['filename']}[/]')
        
    extras = ['000_and_startup_common.ark']

    for filename in extras:
        output_path = os.path.join(output, filename)

        try:
            console.print(f'Downloading [yellow]{filename}[/]')
            with api.download_asset(
                filename,
                output_path,
                stream = True,
            ) as downloader:
                downloader.response.raise_for_status()
                downloader.full_download(console)
        except HTTPError:
            console.print(f'[red]Failed to download {filename}[/]')

