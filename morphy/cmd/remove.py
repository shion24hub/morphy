import datetime
import os
from typing import Annotated

import pandas as pd
import typer
from rich import print

from .. import config

app = typer.Typer()


@app.command("item", help="Remove data from morphy storage.")
def remove(
    exchange: Annotated[str, typer.Argument(..., help="Exchange name")],
    symbol: Annotated[str, typer.Argument(..., help="Symbol")],
    begin: Annotated[str, typer.Argument(..., help="Date(YYYYMMDD)")],
    end: Annotated[str, typer.Argument(..., help="Date(YYYYMMDD)")],
) -> None:
    """ """

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
            config.STORAGE_DIR, exchange, symbol, f"{date.strftime('%Y%m%d')}.csv.gz"
        )

        if not os.path.exists(target):
            continue

        os.remove(target)

    print("All processes are completed.")
