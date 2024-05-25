import datetime
import os

import pandas as pd

class Bybit:
    def __init__(self) -> None:
        self.name = "Bybit"
        self.base_url = "https://public.bybit.com/trading/"

    def make_url(self, symbol: str, date: datetime.datetime) -> str:
        """ make_url
        Args:
            symbol (str): symbol
            date (datetime.datetime): date
        Returns:
            str: URL to download. e.g. https://public.bybit.com/trading/BTCUSDT/BTCUSDT2021-09-01.csv.gz
        
        """

        return os.path.join(
            self.base_url, symbol, f"{symbol}{date.strftime('%Y-%m-%d')}.csv.gz"
        )

    def download(self, url: str) -> pd.DataFrame | None:
        """ download
        Args:
            url (str): URL to download
        Returns:
            pd.DataFrame | None: DataFrame if success, None if failed. df.columns = ["timestamp", "datetime", ""] 

        """

        try:
            df = pd.read_csv(url, compression="gzip")
            df.loc[:, ["datetime"]] = pd.to_datetime(df["timestamp"], unit="s")
            return df
        except Exception as e:
            raise e
