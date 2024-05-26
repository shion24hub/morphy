import os
from pathlib import Path

import typer
from rich import print

from .cmd import make, remove, show, update
from . import config

app = typer.Typer()
app.add_typer(update.app, name="update")
app.add_typer(make.app, name="make")
app.add_typer(show.app, name="show")
app.add_typer(remove.app, name="remove")

@app.callback()
def callback() -> None:

    if not os.path.exists(config.PROJECT_DIR):
        print('\n[bold green]<-- Morphy CLI Callback -->[/bold green]\n')
        print('The Morphy\'s project directory does NOT seem to exist.')
        print('If you are running this app for the first time, no problem.')
        print('If not, the directory may have been accidentally deleted. Please check.\n')

        print('Create a new project directory at $HOME/.morphy.')
        prj_dir = Path(config.PROJECT_DIR)
        os.makedirs(prj_dir, exist_ok=True)
        print('    - Done.')
        
        print('Create a new storage directory at $HOME/.morphy/storage.')
        strg_dir = Path(config.STORAGE_DIR)
        os.makedirs(strg_dir, exist_ok=True)
        print('    - Done.')

        inifile = os.path.join(prj_dir, 'morphy.ini')
        with open(inifile, 'w') as f:
            f.write(f'[paths]\n')
            f.write(f'project_dir = {config.PROJECT_DIR}\n')
            f.write(f'storage_dir = {config.STORAGE_DIR}\n')
        
        print('\nIf you want to change the storage directory, use `morphy setup`.')
        print("All processes are completed.")
        print('\n[bold green]<-- Morphy CLI Callback -->[/bold green]\n')

    