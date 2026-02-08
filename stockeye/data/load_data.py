import pandas as pd

from importlib.resources import files


def load_nse_symbols(index: str = "NIFTY_50") -> list[str]:
    try:
        filename = f"{index.replace('_', '-')}.csv"
        path = files("stockeye.data").joinpath(filename)
        df = pd.read_csv(path)

        df.columns = (
            df.columns
            .str.strip()
            .str.replace("\n", "", regex=False)
            .str.lower()
        )

        if "symbol" not in df.columns:
            raise ValueError(f"'symbol' column not found in {path}")

        suffix = "-SM.NS" if ("SME" in index.upper()) else ".NS"
        symbols = (
            df["symbol"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .loc[lambda s: ~s.str.contains("NIFTY", na=False)]
            .add(suffix)
            .unique()
            .tolist()
        )

        return symbols
    
    except Exception as e:
        print(f"Error loading stock index {index}: {str(e)}")
        return []
