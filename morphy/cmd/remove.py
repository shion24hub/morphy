import datetime
import os
from typing import Annotated

import pandas as pd
import typer
from rich import print

from .. import config
from . import util

app = typer.Typer()


@app.command("item", help="Remove data from morphy storage.")
def remove(
    exchange: Annotated[str, typer.Argument(..., help="Exchange name")],
    symbol: Annotated[str, typer.Argument(..., help="Symbol")],
    begin: Annotated[str, typer.Argument(..., help="Date(YYYYMMDD)")],
    end: Annotated[str, typer.Argument(..., help="Date(YYYYMMDD)")],
) -> None:
    """ 
    An implementation of the remove item command of the Morphy CLI.
    Remove specified data from morphy storage.

    Args:
        exchange(str): Exchange name
        symbol(str): Symbol
        begin(str): Begin date(YYYYMMDD)
        end(str): End date(YYYYMMDD)
    
    """

    global storage_dir_path
    storage_dir_path = util.find_storage_path()

    # <-- Input Validation -->
    try:
        fbegin = datetime.datetime.strptime(begin, "%Y%m%d")
        fend = datetime.datetime.strptime(end, "%Y%m%d")
    except ValueError:
        err = f"Invalid date format. Use YYYYMMDD."
        raise ValueError(err)

    if fbegin > fend:
        err = "Begin date should be earlier than end date."
        raise ValueError(err)

    # <-- Confirm -->
    print("[bold red][ Confirm ][/bold red]")
    y_or_n = typer.prompt(
        f"Do you really want to remove {fbegin.strftime('%Y%m%d')} - {fend.strftime('%Y%m%d')} data for {symbol}? (y/n)"
    )
    if y_or_n.lower() != "y":
        print("Canceled.")
        return

    # <-- Main Logic -->
    date_range = pd.date_range(fbegin, fend, freq="D")
    for date in date_range:
        target = os.path.join(
            storage_dir_path, exchange, symbol, f"{date.strftime('%Y%m%d')}.csv.gz"
        )

        if not os.path.exists(target):
            continue

        os.remove(target)

    print("All processes are completed.")
