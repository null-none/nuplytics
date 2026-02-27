import pandas as pd
import yfinance as yf
from datetime import datetime


class NUPLCalculator:
    def __init__(self, ticker="BTC-USD", supply=19_000_000, window=180):
        self.ticker = ticker
        self.supply = supply
        self.window = window
        self.data = None
        self.latest_result = None

    def download_data(self, start="2020-01-01"):
        end = datetime.today().strftime("%Y-%m-%d")
        # Fetch extra history before `start` to warm up the rolling window
        warmup_start = (
            pd.to_datetime(start) - pd.DateOffset(days=self.window * 2)
        ).strftime("%Y-%m-%d")
        self._requested_start = pd.to_datetime(start).date()
        raw = yf.download(
            self.ticker, start=warmup_start, end=end, interval="1d", progress=False
        )
        if raw.empty:
            raise ValueError(f"No data returned by yfinance for ticker '{self.ticker}'")
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        # squeeze() ensures we get a Series, not a single-column DataFrame
        close = raw[["Close"]].squeeze()
        df = close.to_frame("price")
        df.index.name = "date"
        df.reset_index(inplace=True)
        self.data = df

    def calculate_nupl(self):
        df = self.data.copy()
        df["supply"] = self.supply
        df["price"] = df["price"].squeeze()  # ensure Series, not DataFrame
        df["realized_price"] = df["price"].rolling(window=self.window).mean()
        df["market_cap"] = df["price"] * df["supply"]
        df["realized_cap"] = df["realized_price"] * df["supply"]
        df["nupl"] = (df["market_cap"] - df["realized_cap"]) / df["market_cap"]
        result = df.dropna()
        # Trim warmup rows — keep only data from the originally requested start date
        result = result[result["date"].dt.date >= self._requested_start]
        if result.empty:
            raise ValueError(
                f"No data available from {self._requested_start} for ticker '{self.ticker}'."
            )
        self.data = result

    def interpret_latest(self):
        latest = self.data.iloc[-1]
        nupl_value = latest["nupl"]
        date = latest["date"].strftime("%Y-%m-%d")

        if nupl_value < 0:
            status = "Capitulation"
            message = "The market is at a loss. Possible bottom opportunity."
            signal = "BUY"
        elif nupl_value < 0.25:
            status = "Fear"
            message = "The market is fearful. Potential accumulation phase."
            signal = "BUY"
        elif nupl_value < 0.5:
            status = "Hope / Optimism"
            message = "Moderate growth. Market shows healthy optimism."
            signal = "HOLD"
        elif nupl_value < 0.75:
            status = "Greed"
            message = "Market is overheating. Be cautious."
            signal = "SELL"
        else:
            status = "Euphoria"
            message = "Market is extremely greedy. High risk of correction."
            signal = "DANGER"

        self.latest_result = {
            "date": date,
            "price": round(latest["price"], 2),
            "realized_price": round(latest["realized_price"], 2),
            "nupl": round(nupl_value, 4),
            "status": status,
            "message": message,
            "signal": signal,
        }

    def calculate(self, start="2020-01-01"):
        self.download_data(start)
        self.calculate_nupl()
        self.interpret_latest()

    def get_latest_json(self):
        return self.latest_result

    def get_data(self):
        return self.data
