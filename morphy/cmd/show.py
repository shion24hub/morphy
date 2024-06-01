import datetime
import os

import typer
from rich import print

from . import util

app = typer.Typer()


@app.command("items")
def show() -> None:
    """
    An implementation of the show items command of the Morphy CLI.
    Show information of items in morphy storage.
    Displayed are the size of storage directory, exchange name, symbol,
    and the date range of the data.

    """

    global storage_dir_path
    storage_dir_path = util.find_storage_path()
    os.makedirs(storage_dir_path, exist_ok=True)

    # <-- Main Logic -->
    # get the size of the storage directory
    total_size = 0
    for root, _, files in os.walk(storage_dir_path):
        for file in files:
            total_size += os.path.getsize(os.path.join(root, file))
    
    print(f"Total size: {total_size / 1024 / 1024:.2f} MB\n")

    # get the list of items
    print('{:<10} {:<10} {:<10} {:<10}'.format('Exchange', 'Symbol', 'Begin', 'End'))
    for ex_d in storage_dir_path.iterdir():
        if not ex_d.is_dir():
            continue
        
        for sym_d in ex_d.iterdir():
            if not sym_d.is_dir():
                continue
            
            items = []
            for item in sym_d.iterdir():
                if not item.is_file():
                    continue
                if not item.name.endswith('.csv.gz'):
                    continue

                items.append(item.name.strip('.csv.gz'))
            
            if not items:
                continue

            dts = [datetime.datetime.strptime(item, '%Y%m%d') for item in items]
            begin = min(dts).strftime('%Y-%m-%d')
            end = max(dts).strftime('%Y-%m-%d')
            
            print(f'{ex_d.name:<10} {sym_d.name:<10} {begin:<10} {end:<10}')
