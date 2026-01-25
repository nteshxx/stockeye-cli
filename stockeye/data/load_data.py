import pandas as pd
from pathlib import Path

def load_nse_data(index: str = "NIFTY_50") -> list[str]:
    csv_file = Path("stockeye/data") / f"{index.replace('_', '-')}.csv"
    df = pd.read_csv(csv_file)

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
