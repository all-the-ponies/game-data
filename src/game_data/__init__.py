# PYTHON_ARGCOMPLETE_OK

import resource

from argparse import ArgumentParser
import json
import os
from pathlib import Path
import shutil

import argcomplete
from botocore.exceptions import ClientError
import google_play_scraper as gplay

from luna_kit.api import API
from luna_kit.typings import DLCManifest

from .console import console
from .env import set_mode, load_env, GAME_DATA_ENV_VAR
from .downloader import download
from .extractor import extract
from .notify import Notifier
from .s3 import BUCKET, get_s3_client
from .sync import sync
from .transformer import Transformer

PACKAGE_NAME = "com.gameloft.android.ANMP.GloftPOHM"


def build_cdn(
    raw_dir: str | Path,
    dist_dir: str | Path,
    version: str,
    upload: bool,
    overrides_dir: str | Path,
    skip: list[str] | None = None,
    ffdec: str = 'ffdec',
):
    if skip is None:
        skip = []

    dist_dir = Path(dist_dir)
    raw_dir = Path(raw_dir)
    arks_dir = raw_dir/'arks'
    extracted_dir = raw_dir/'extracted'

    latest_dlc_manifest: DLCManifest | None = None
    s3_client = get_s3_client()

    notifier = Notifier()

    if version == 'latest':
        last_version: str | None = None
        try:
            version_file = s3_client.get_object(
                Bucket = BUCKET,
                Key = 'game_version.json',
            )
            last_version = json.load(version_file['Body'])['game_version']
        except:
            try:
                with open(dist_dir/'game_version.json', 'r') as file:
                    last_version = json.load(file)['game_version']
            except:
                console.print('Could not get current version')
        
        app_info = gplay.app(PACKAGE_NAME)
        latest_version = app_info['version']

        notifier.version = latest_version
        notifier.release_notes = app_info['recentChanges']
        notifier.app_icon = app_info['icon']

        version = latest_version
        if not last_version or latest_version != last_version:
            console.print(f'New app version found: [yellow]{latest_version}[/]')
            notifier.notify('app')
        else:
            api = API('android', last_version)

            try:
                last_dlc_manifest_file = s3_client.get_object(
                    Bucket = BUCKET,
                    Key = 'current_dlc_manifest.json',
                )
                last_dlc_manifest = json.load(last_dlc_manifest_file['Body'])

                api = API('android', latest_version)
                latest_dlc_manifest = api.get_dlc_manifest()

                if last_dlc_manifest == latest_dlc_manifest:
                    console.print('[green]All up to date![/]')
                    return
                else:
                    console.print('New content update found!')
                    notifier.notify('content')

            except ClientError:
                console.print('Could not check dlc_manifest')
                notifier.notify('content')
            
        console.print(f'[green]Found version {version}[/]')
    else:
        console.print(f'version: {version}')
        


    if 'download' not in skip:
        shutil.rmtree(arks_dir, ignore_errors = True)
    if 'extract' not in skip:
        shutil.rmtree(extracted_dir, ignore_errors = True)
    if 'transform' not in skip:
        shutil.rmtree(dist_dir, ignore_errors = True)

    os.makedirs(dist_dir, exist_ok = True)
    
    if 'download' not in skip:
        console.print('Downloading files')
        download(arks_dir, version)
        console.line()

    if 'extract' not in skip:
        console.print('Extracting files')
        extract(arks_dir, extracted_dir)

        console.line()
    
    if 'transform' not in skip:
        console.print('Transforming data')
        transformer = Transformer(
            extracted_dir,
            dist_dir,
            overrides_dir,
            version,
            ffdec = ffdec,
        )

        transformer.start()
        transformer.save()

        console.line()

    if upload:
        sync(dist_folder = dist_dir)
        
        api = API('android', version)
        dlc_manifest = api.get_dlc_manifest()
        try:
            s3_client.put_object(
                Bucket = BUCKET,
                Key = 'current_dlc_manifest.json',
                Body = json.dumps(dlc_manifest).encode('utf-8'),
            )
        except:
            console.print('[red]Failed to save dlc_manifest[/]')
    

def main() -> None:
    argparser = ArgumentParser()

    argparser.add_argument(
        '--env',
        dest = 'env',
        choices = ['dev', 'prod'],
        default = None,
        help = f'The environment to use. Can be set with {GAME_DATA_ENV_VAR}. Note: this is more for loading .env and different notifications.json files in development.',
    )

    command = argparser.add_subparsers(
        title = 'command',
        dest = 'command',
    )

    build = command.add_parser(
        'build',
        description = 'Build cdn',
    )

    build.add_argument(
        '-v', '--version',
        dest = 'version',
        help = 'Game version to download. If "latest" it will check if it can download the latest version, and will exit if already on the latest version.',
        default = 'latest',
    )

    build.add_argument(
        '-r', '--raw',
        dest = 'raw',
        help = 'Raw output folder',
        default = 'raw',
    )

    build.add_argument(
        '-o', '--output',
        dest = 'output',
        help = 'Output destination',
        default = 'dist',
    )

    build.add_argument(
        '--overrides',
        help = 'Path to overrides folder',
        default = 'overrides',
    )

    build.add_argument(
        '-u', '--upload',
        dest = 'upload',
        action = 'store_true',
        help = 'Upload the files to R2',
    )

    build.add_argument(
        '--skip',
        dest = 'skip',
        nargs = '+',
        choices = ['download', 'extract', 'transform'],
        help = 'Skip action',
        default = [],
    )

    build.add_argument(
        '--ffdec',
        dest = 'ffdec',
        help = 'Path to ffdec.jar',
        default = 'ffdec',
    )

    argcomplete.autocomplete(argparser)

    args = argparser.parse_args()

    if args.env:
        set_mode(prod = args.env == 'prod')
    load_env()

    match args.command:
        case 'build':
            build_cdn(
                raw_dir = args.raw,
                dist_dir = args.output,
                version = args.version,
                upload = args.upload,
                overrides_dir = args.overrides,
                skip = args.skip,
                ffdec = args.ffdec,
            )
    
    peak_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    print(f"Peak Memory Usage: {peak_memory:.2f} MB")
