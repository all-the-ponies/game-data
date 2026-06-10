# PYTHON_ARGCOMPLETE_OK

from argparse import ArgumentParser
import os
import shutil
from pathlib import Path

import argcomplete

from .console import console
from .downloader import download
from .extractor import extract
from .transformer import Transformer


def build_cdn(
    raw_dir: str,
    out_dir: str,
    version: str,
    upload: bool,
    overrides_dir: str,
    skip_download: bool = False,
):
    arks_dir = Path(raw_dir, 'arks')
    extracted_dir = Path(raw_dir, 'extracted')

    if not skip_download:
        shutil.rmtree(arks_dir, ignore_errors = True)
    
    shutil.rmtree(out_dir, ignore_errors = True)
    shutil.rmtree(extracted_dir, ignore_errors = True)

    os.makedirs(out_dir, exist_ok = True)
    
    if not skip_download:
        console.print('Downloading files')
        download(arks_dir, version)
        console.line()

    console.print('Extracting files')
    extract(arks_dir, extracted_dir)

    console.line()
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
        '--skip-download',
        dest = 'skip_download',
        help = 'Skip download',
        action = 'store_true',
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
                skip_download = args.skip_download,
            )
