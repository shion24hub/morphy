from typing import Annotated
import datetime
import os

import numpy as np
import pandas as pd
import typer
from rich import print
from rich.progress import track

from .. import config
from .model.bybit import Bybit


app = typer.Typer()


@app.command("item")
def update(
    exchange: Annotated[str, typer.Argument(..., help='Exchange name. e.g. "bybit"')],
    symbol: Annotated[str, typer.Argument(..., help='Symbol. e.g. "BTCUSDT"')],
    begin: Annotated[str, typer.Argument(..., help='Begin date(YYYYMMDD). e.g. "20210901"')],
    end: Annotated[str, typer.Argument(..., help='End date(YYYYMMDD). e.g. "20210930"')],
):
    """
    Update an item in morphy storage.

    """
    pass
    

    

    