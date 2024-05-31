import datetime
import os
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer
from rich import print
from rich.progress import track

from . import util

app = typer.Typer()


def resample_to_Nsec(df: pd.DataFrame, interval: int) -> pd.DataFrame:
    """
    Resample the DataFrame to N-second data.

    Args:
        df(pd.DataFrame): DataFrame
        interval(int): Interval in seconds

    Returns:
        pd.DataFrame: Resampled DataFrame

    """

    df["datetime"] = pd.to_datetime(df["datetime"])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    df["buyVolume"] = df["buyVolume"].astype(float)
    df["sellVolume"] = df["sellVolume"].astype(float)

    df = df.set_index("datetime")
    df = df.resample(f"{interval}s").agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "buyVolume": "sum",
            "sellVolume": "sum",
        }
    )

    df = df.dropna()

    return df


@app.command(
    "item", help="Make N-second ohlcv data from original data in morphy storage."
)
@util.timer
def make(
    exchange: Annotated[str, typer.Argument(..., help="Exchange name")],
    symbol: Annotated[str, typer.Argument(..., help="Symbol")],
    begin: Annotated[str, typer.Argument(..., help="Begin date(YYYYMMDD)")],
    end: Annotated[str, typer.Argument(..., help="End date(YYYYMMDD)")],
    interval: Annotated[str, typer.Argument(..., help="Interval(sec)")],
    to: Annotated[str, typer.Option(..., help="Savepath")] = ".",
) -> None:
    """
    An implementation of the make item command of the Morphy CLI.

    """

    global storage_dir_path
    storage_dir_path = util.find_storage_path()
    os.makedirs(storage_dir_path, exist_ok=True)

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

    # posix path
    to = Path(to)
    if not to.exists():
        raise ValueError(f"Path {to} does not exist.")

    file_name = f"{exchange}_{symbol}_{fbegin.strftime('%Y%m%d')}_{fend.strftime('%Y%m%d')}_{interval}s.csv.gz"

    # <-- Main Logic -->
    date_range = pd.date_range(fbegin, fend, freq="D")
    dfs = []

    for date in track(date_range, description="Making..."):
        target = os.path.join(
            storage_dir_path, exchange, symbol, f"{date.strftime('%Y%m%d')}.csv.gz"
        )
        if not os.path.exists(target):
            # skip
            continue

        df = pd.read_csv(target, compression="gzip")
        df = resample_to_Nsec(df, int(interval))
        dfs.append(df)

    if len(dfs) == 0:
        print("No data to make. Use `morphy update` to download data.")
        return

    final_df = pd.concat(dfs)
    savepath = os.path.join(to, file_name)
    final_df.to_csv(savepath, compression="gzip")

    print("All processes are completed.")

@app.command('items')
def make_items(file: Annotated[str, typer.Argument(..., help='File path')]) -> None:
    """
    An implementation of the make items command of the Morphy CLI.
    Each line of the procedure file must contain the arguments for the `make item` command.
    
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
            make(*args)
