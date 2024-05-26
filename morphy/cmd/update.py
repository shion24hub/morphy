import datetime
import os
from concurrent import futures
from typing import Annotated
from functools import wraps
import time

import numpy as np
import pandas as pd
import typer
from rich import print
from rich.progress import track

from .. import config
from .model.bybit import Bybit

app = typer.Typer()

# constants
MAX_WORKERS = 20


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"Elapsed time: {elapsed:.2f} sec")
        return result
    return wrapper


def make_1s_candle(df: pd.DataFrame) -> pd.DataFrame:
    """
    convert trading data to ohlcv data.
    required columns of df: ['datetime', 'side', 'size', 'price']

    df:
    - datetime(pd.datetime64[ns]): timestamp of the trade
    - side(str): 'Buy' or 'Sell'
    - size(float): size of the trade
    - price(float): price of the trade

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
    return os.path.join(
        config.STORAGE_DIR, exchange, symbol, f"{date.strftime('%Y%m%d')}.csv.gz"
    )


# rename this function to process
def download_and_save(url: str, exc: Bybit, savepath: str) -> None:
    if os.path.exists(savepath):
        # skip
        return

    df = exc.download(url)
    df = make_1s_candle(df)
    os.makedirs(os.path.dirname(savepath), exist_ok=True)
    df.to_csv(savepath, compression="gzip")


@app.command("item")
@timer
def update(
    exchange: Annotated[str, typer.Argument(..., help="Exchange name")],
    symbol: Annotated[str, typer.Argument(..., help="Symbol")],
    begin: Annotated[str, typer.Argument(..., help="Begin date(YYYYMMDD)")],
    end: Annotated[str, typer.Argument(..., help="End date(YYYYMMDD)")],
) -> None:
    """
    Update an item in morphy storage.

    """

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