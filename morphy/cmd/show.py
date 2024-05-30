import os
import datetime

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

    # get the list of items
    items = []
    for exchange in os.listdir(storage_dir_path):
        if exchange.startswith("."):
            continue

        for symbol in os.listdir(os.path.join(storage_dir_path, exchange)):
            if symbol.startswith("."):
                continue

            dates = os.listdir(os.path.join(storage_dir_path, exchange, symbol))
            dates = [date.split(".")[0] for date in dates]
            if len(dates) == 0:
                continue

            begin = min(dates)
            end = max(dates)
            items.append((exchange, symbol, begin, end))

    # <-- Output -->
    print(f"Total size: {total_size / 1024 / 1024:.2f} MB\n")
    print(f"{'Exchange':<10} {'Symbol':<10} {'Begin':<10} {'End':<10}")
    for item in items:
        formatted_start = datetime.datetime.strptime(item[2], "%Y%m%d").strftime('%Y-%m-%d')
        formatted_end = datetime.datetime.strptime(item[3], "%Y%m%d").strftime('%Y-%m-%d')
        print(f"{item[0]:<10} {item[1]:<10} {formatted_start:<10} {formatted_end:<10}")
