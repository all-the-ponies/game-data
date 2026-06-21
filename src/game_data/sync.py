from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import mimetypes
import os
from pathlib import Path
from typing import Literal, TYPE_CHECKING, TypedDict

from PIL import Image
import botocore.exceptions
from botocore.exceptions import ClientError
from rich.progress import Progress

from .GameDataTypes import GameVersion, CategoryName, GameObjects, CATEGORY_NAMES, GameObjectId, GenericObjectType
from .console import COLUMNS, console, track
from .s3 import BUCKET, get_s3_client

if TYPE_CHECKING:
    from types_boto3_s3.client import S3Client

MAX_WORKERS = 10


def get_image_metadata(path: str | Path) -> dict[Literal['width', 'height'], str]:
    image = Image.open(path)
    return {
        'width': str(image.width),
        'height': str(image.height),
    }

def upload_single_file(client: 'S3Client', bucket: str, filepath: Path, key: str):
    content_type, _ = mimetypes.guess_type(filepath)

    metadata = {}

    extra_args = {}

    if content_type:
        extra_args['ContentType'] = content_type
        if content_type.startswith('image/'):
            metadata.update(get_image_metadata(filepath))
    
    file_data = filepath.read_bytes()
    
    if filepath.suffix == '.json':
        data = json.loads(file_data)
        file_data = json.dumps(data, ensure_ascii = False, separators=(",", ":")).encode('utf-8')
    
    hash = hashlib.sha256(file_data).hexdigest()

    metadata['hash'] = hash

    upload = True

    try:
        object = client.head_object(Bucket = bucket, Key = key)
        if object['Metadata'].get('hash') == hash:
            upload = False
    except botocore.exceptions.ClientError as e:
        if e.response.get('Error', {}).get('Code', '') == '404':
            upload = True
        else:
            raise

    if upload:
        try:
            client.put_object(
                Bucket = bucket,
                Key = key,
                Body = file_data,
                Metadata = metadata,
                **extra_args,
            )


        except Exception as e:
            e.add_note(f'File: {filepath}')
            console.print_exception()



def sync(dist_folder: str | Path):
    generate_diff(dist_folder)

    console.print('Uploading files')

    client = get_s3_client(MAX_WORKERS)

    dist_folder = Path(dist_folder)

    upload_tasks: list[tuple[Path, str]] = []

    for file_path in dist_folder.rglob('*'):
        if file_path.is_file():
            key = file_path.relative_to(dist_folder).as_posix()
            upload_tasks.append((file_path, key))


    executor = ThreadPoolExecutor(max_workers = MAX_WORKERS)

    try:
        futures = {
            executor.submit(upload_single_file, client, BUCKET, local, key): key 
            for local, key in upload_tasks
        }
        
        with Progress(
            *COLUMNS,
            console = console,
        ) as progress:
            progress_task = progress.add_task('Uploading...', total = len(upload_tasks))
            for future in as_completed(futures):
                progress.advance(progress_task)
    except KeyboardInterrupt:
        executor.shutdown(wait = True, cancel_futures = True)
        console.print('[red]Operation canceled[/]')
    finally:
        executor.shutdown(wait = True)


"""
{
    '11.1.1a': {
        '11.1.1.20': {
            'game_objects': {
                'added': ['Pony_Twilight'],
                'changed': ['Pony_Twilight'],
                'removed': ['Pony_Twilight'],
            }
        }
    }
}
"""

type Changelog = dict[
    str,
    dict[
        str,
        dict[
            Literal['game_objects'],
            dict[
                CategoryName,
                dict[
                    Literal['added', 'changed', 'removed'],
                    list[str]
                ]
            ]
        ]
    ]
]


def generate_diff(dist_folder: str | Path):
    dist_folder = Path(dist_folder)
    
    client = get_s3_client()

    with open(dist_folder/'game_version.json', 'r', encoding = 'utf-8') as file:
        current_version = GameVersion.model_validate_json(file.read())

    try:
        last_version = GameVersion.model_validate_json(
            client.get_object(
                Bucket = BUCKET,
                Key = 'game_version.json',
            )['Body'].read(),
        )
    except ClientError:
        last_version = current_version
    
    changelog: Changelog = {}

    try:
        changelog = json.load(
            client.get_object(
                Bucket = BUCKET,
                Key = 'changelog.json',
            )['Body']
        )
    except ClientError:
        pass

    if current_version != last_version:
        console.print('Generating diff')

        try:
            last_game_objects = GameObjects.model_validate_json(
                client.get_object(
                    Bucket = BUCKET,
                    Key = 'game_objects.json',
                )['Body'].read(),
            )
        except ClientError:
            return

        with open(dist_folder/'game_objects.json', 'r', encoding = 'utf-8') as file:
            current_game_objects = GameObjects.model_validate_json(file.read())
        
        game_objects_diff: dict[CategoryName, dict[Literal['added', 'changed', 'removed'], list[str]]] = {}
        
        for category in CATEGORY_NAMES:
            if not hasattr(last_game_objects, category) or not hasattr(current_game_objects, category):
                continue

            last_objects: dict[GameObjectId, GenericObjectType] = getattr(last_game_objects, category).objects
            current_objects: dict[GameObjectId, GenericObjectType] = getattr(current_game_objects, category).objects

            added = set(current_objects) - set(last_objects)
            removed = set(last_objects) - set(current_objects)

            changed = set[GameObjectId]()

            for gameObject in current_objects.values():
                if gameObject.id not in last_objects:
                    continue

                if gameObject != last_objects[gameObject.id]:
                    changed.add(gameObject.id)
                
            game_objects_diff[category] = {
                'added': list(added),
                'changed': list(changed),
                'removed': list(removed),
            }
            
        changelog.setdefault(
            current_version.game_version,
            {},
        ).setdefault(
            current_version.content_version,
            {},
        )['game_objects'] = game_objects_diff

    with open(dist_folder/'changelog.json', 'w', encoding = 'utf-8') as file:
        json.dump(changelog, file, indent = 2, ensure_ascii = False)
