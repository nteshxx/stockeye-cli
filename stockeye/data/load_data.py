import pandas as pd
from importlib.resources import files

def load_nse_data(index: str = "NIFTY_50") -> list[str]:

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
        raise ValueError(f"'symbol' column not found in {csv_file}")

    symbols = (
        df["symbol"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .loc[lambda s: ~s.str.contains("NIFTY", na=False)]
        .add(".NS")
        .unique()
        .tolist()
    )

    return symbols
