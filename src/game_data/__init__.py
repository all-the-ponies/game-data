# PYTHON_ARGCOMPLETE_OK

from argparse import ArgumentParser
import os
from pathlib import Path
import shutil

import argcomplete
from dotenv import load_dotenv

from .console import console
from .downloader import download
from .extractor import extract
from .sync import sync
from .transformer import Transformer

load_dotenv()

def build_cdn(
    raw_dir: str,
    out_dir: str,
    version: str,
    upload: bool,
    overrides_dir: str,
    skip: list[str] | None = None,
):
    if skip is None:
        skip = []

    arks_dir = Path(raw_dir, 'arks')
    extracted_dir = Path(raw_dir, 'extracted')

    if 'download' not in skip:
        shutil.rmtree(arks_dir, ignore_errors = True)
    if 'extract' not in skip:
        shutil.rmtree(extracted_dir, ignore_errors = True)
    if 'transform' not in skip:
        shutil.rmtree(out_dir, ignore_errors = True)

    os.makedirs(out_dir, exist_ok = True)
    
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
            out_dir,
            overrides_dir,
            version,
        )

        transformer.start()
        transformer.save()

        console.line()

    if upload:
        sync(dist_folder = out_dir)
    

def main() -> None:
    argparser = ArgumentParser()

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
        help = 'Game version to download',
        required = True,
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

    argcomplete.autocomplete(argparser)

    args = argparser.parse_args()

    match args.command:
        case 'build':
            build_cdn(
                raw_dir = args.raw,
                out_dir = args.output,
                version = args.version,
                upload = args.upload,
                overrides_dir = args.overrides,
                skip = args.skip,
            )
