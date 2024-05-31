import datetime
import os
from concurrent import futures
from typing import Annotated

import numpy as np
import pandas as pd
import typer
from rich import print
from rich.progress import track

from . import util
from .model.bybit import Bybit

app = typer.Typer()

# constants
MAX_WORKERS = 20


def make_1s_candle(df: pd.DataFrame) -> pd.DataFrame:
    """
    convert trading data to ohlcv data.
    required columns of df: ['datetime', 'side', 'size', 'price']
    df:
    - datetime(pd.datetime64[ns]): timestamp of the trade
    - side(str): 'Buy' or 'Sell'
    - size(float): size of the trade
    - price(float): price of the trade

    Args:
        df(pd.DataFrame): trading data

    Returns:
        df(pd.DataFrame): ohlcv data

    """

    df = df[["datetime", "side", "size", "price"]]

    df.loc[:, ["buySize"]] = np.where(df["side"] == "Buy", df["size"], 0)
    df.loc[:, ["sellSize"]] = np.where(df["side"] == "Sell", df["size"], 0)
    df.loc[:, ["datetime"]] = df["datetime"].dt.floor("1s")

    df = df.groupby("datetime").agg(
        {
            "price": ["first", "max", "min", "last"],
            "size": "sum",
            "buySize": "sum",
            "sellSize": "sum",
        }
    )

    # multiindex to single index
    df.columns = ["_".join(col) for col in df.columns]
    df = df.rename(
        columns={
            "price_first": "open",
            "price_max": "high",
            "price_min": "low",
            "price_last": "close",
            "size_sum": "volume",
            "buySize_sum": "buyVolume",
            "sellSize_sum": "sellVolume",
        }
    )

    return df


def make_savepath(exchange: str, symbol: str, date: datetime.datetime) -> str:
    """
    Make savepath for each ohlcv data.
    This function defines how savepath is calculated.

    Args:
        exchange(str): exchange name
        symbol(str): symbol
        date(datetime.datetime): date

    Returns:
        str: savepath

    """
    return os.path.join(
        storage_dir_path, exchange, symbol, f"{date.strftime('%Y%m%d')}.csv.gz"
    )


def download_and_save(url: str, exc: Bybit, savepath: str) -> None:
    """
    Download data from the url and save it to the savepath.
    This function is used in ThreadPoolExecutor.

    Args:
        url(str): URL to download
        exc(Bybit): exchange object
        savepath(str): savepath

    """

    if os.path.exists(savepath):
        # skip
        return

    df = exc.download(url)
    df = make_1s_candle(df)
    os.makedirs(os.path.dirname(savepath), exist_ok=True)
    df.to_csv(savepath, compression="gzip")


@app.command("item", help="Update an item in morphy storage.")
@util.timer
def update(
    exchange: Annotated[str, typer.Argument(..., help="Exchange name")],
    symbol: Annotated[str, typer.Argument(..., help="Symbol")],
    begin: Annotated[str, typer.Argument(..., help="Begin date(YYYYMMDD)")],
    end: Annotated[str, typer.Argument(..., help="End date(YYYYMMDD)")],
) -> None:
    """
    An implementation of the update item command of the Morphy CLI.
    This function downloads trading data and saves it to the storage directory.
    Downloading is done in a concurrent process.

    Args:
        exchange(str): exchange name
        symbol(str): symbol
        begin(str): begin date(YYYYMMDD)
        end(str): end date(YYYYMMDD)

    """

    global storage_dir_path
    storage_dir_path = util.find_storage_path()
    os.makedirs(storage_dir_path, exist_ok=True)

    # <-- Input Validation -->
    if exchange.lower() == "bybit":
        exc = Bybit()
    else:
        raise ValueError(f"Exchange {exchange} is not supported.")

    try:
        fbegin = datetime.datetime.strptime(begin, "%Y%m%d")
        fend = datetime.datetime.strptime(end, "%Y%m%d")
    except ValueError:
        err = f"Invalid date format. Use YYYYMMDD."
        raise ValueError(err)

    if fbegin > fend:
        err = "Begin date should be earlier than end date."
        raise ValueError(err)

    # <-- Main Logic -->
    date_range = pd.date_range(fbegin, fend, freq="D")

    urls = [exc.make_url(symbol, date) for date in date_range]
    excs = [exc] * len(urls)
    savepaths = [make_savepath(exchange, symbol, date) for date in date_range]

    workers = min(MAX_WORKERS, len(urls))

    with futures.ThreadPoolExecutor(workers) as executor:
        list(
            track(
                executor.map(download_and_save, urls, excs, savepaths),
                total=len(urls),
                description="Downloading...",
            )
        )

    print("All processes are completed.")


@app.command('items')
def update_items(file: Annotated[str, typer.Argument(..., help='File path')]) -> None:
    """
    An implementation of the update items command of the Morphy CLI.
    Each line of the procedure file must contain the arguments for the `update item` command.
    
    """
    
    # <-- Input Validation -->
    if not os.path.exists(file):
        err = f"{file} does not exist."
        raise typer.BadParameter(err)
    
    # <-- Main Logic -->
    with open(file, "r") as f:
        lines = f.readlines()
        for line in lines:
            # if the line is empty, skip
            if line == "\n":
                continue
            args = line.split()
            update(*args)
