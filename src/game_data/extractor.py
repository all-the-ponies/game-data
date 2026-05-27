import os

from luna_kit.ark import ARK

from .console import console, track
from rich.progress import TextColumn, BarColumn, MofNCompleteColumn, TimeRemainingColumn

def extract(arks_dir: str, output: str):
    for filename in os.listdir(arks_dir):
        with ARK(os.path.join(arks_dir, filename)) as ark:
            console.print(f'Extracting [yellow]{filename}[/]')

            for filename in track(
                ark.namelist(),
                description = 'Extracting...',
                transient = True,
                columns = [
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    MofNCompleteColumn(),
                    TimeRemainingColumn(),
                ]
            ):
                try:
                    ark.extract(filename, output)
                except Exception as e:
                    e.add_note(f'filename: {filename}')
                    console.print(e)
            
    console.print('[green]Done![/]')

