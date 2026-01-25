import pandas as pd
import pandas_ta as ta


def add_dma(df, short, long):
    """Add DMA (Daily Moving Average) indicators"""
    df["DMA50"] = ta.sma(df["Close"], length=short)
    df["DMA200"] = ta.sma(df["Close"], length=long)
    return df


def add_rsi(df, period=14):
    """
    Add RSI (Relative Strength Index) indicator
    
    RSI Interpretation:
    - RSI > 70: Overbought (potential sell signal)
    - RSI < 30: Oversold (potential buy signal)
    - 30-70: Neutral zone
    """
    df["RSI"] = ta.rsi(df["Close"], length=period)
    return df


def add_macd(df, fast=12, slow=26, signal=9):
    """
    Add MACD (Moving Average Convergence Divergence) indicator
    
    Returns MACD line, Signal line, and Histogram
    
    MACD Interpretation:
    - MACD > Signal: Bullish momentum
    - MACD < Signal: Bearish momentum
    - Histogram > 0: Bullish
    - Histogram < 0: Bearish
    """
    macd = ta.macd(df["Close"], fast=fast, slow=slow, signal=signal)
    
    if macd is not None and not macd.empty:
        df["MACD"] = macd[f"MACD_{fast}_{slow}_{signal}"]
        df["MACD_Signal"] = macd[f"MACDs_{fast}_{slow}_{signal}"]
        df["MACD_Hist"] = macd[f"MACDh_{fast}_{slow}_{signal}"]
    else:
        df["MACD"] = None
        df["MACD_Signal"] = None
        df["MACD_Hist"] = None
    
    return df


def analyze_volume(df, period=20):
    """
    Analyze volume patterns and add volume indicators
    
    Returns:
    - Volume SMA (average volume)
    - Volume ratio (current vs average)
    - Volume trend
    """
    df["Volume_SMA"] = ta.sma(df["Volume"], length=period)
    df["Volume_Ratio"] = df["Volume"] / df["Volume_SMA"]
    
    return df


def get_rsi_signal(rsi):
    """
    Get RSI trading signal
    
    Returns: 'OVERSOLD' | 'OVERBOUGHT' | 'NEUTRAL' | None
    """
    if pd.isna(rsi):
        return None
    
    if rsi < 30:
        return "OVERSOLD"
    elif rsi > 70:
        return "OVERBOUGHT"
    else:
        return "NEUTRAL"


def get_macd_signal(macd, macd_signal, macd_hist):
    """
    Get MACD trading signal
    
    Returns: 'BULLISH' | 'BEARISH' | 'NEUTRAL' | None
    """
    if pd.isna(macd) or pd.isna(macd_signal):
        return None
    
    if macd > macd_signal and macd_hist > 0:
        return "BULLISH"
    elif macd < macd_signal and macd_hist < 0:
        return "BEARISH"
    else:
        return "NEUTRAL"


def get_volume_signal(volume_ratio):
    """
    Get volume analysis signal
    
    Returns: 'HIGH' | 'NORMAL' | 'LOW' | None
    """
    if pd.isna(volume_ratio):
        return None
    
    if volume_ratio > 1.5:
        return "HIGH"
    elif volume_ratio < 0.5:
        return "LOW"
    else:
        return "NORMAL"


def detect_cross_age(df):
    """
    Detect the most recent Golden/Death Cross and calculate days since occurrence
    
    Returns:
        dict: {
            'type': 'GOLDEN_CROSS' | 'DEATH_CROSS' | None,
            'days_ago': int | None,
            'cross_price': float | None
        }
    """
    if len(df) < 2 or df["DMA50"].isna().all() or df["DMA200"].isna().all():
        return {'type': None, 'days_ago': None, 'cross_price': None}
    
    # Create a valid dataframe without NaN values for both DMAs
    valid_df = df.dropna(subset=["DMA50", "DMA200"]).copy()
    
    if len(valid_df) < 2:
        return {'type': None, 'days_ago': None, 'cross_price': None}
    
    # Calculate crossover signals
    valid_df["signal"] = 0
    valid_df.loc[valid_df["DMA50"] > valid_df["DMA200"], "signal"] = 1
    valid_df.loc[valid_df["DMA50"] < valid_df["DMA200"], "signal"] = -1
    
    # Detect changes in signal (crossover events)
    valid_df["cross"] = valid_df["signal"].diff()
    
    # Find the most recent cross
    golden_crosses = valid_df[valid_df["cross"] > 0]
    death_crosses = valid_df[valid_df["cross"] < 0]
    
    most_recent_golden = golden_crosses.index[-1] if len(golden_crosses) > 0 else None
    most_recent_death = death_crosses.index[-1] if len(death_crosses) > 0 else None
    
    # Determine which cross happened most recently
    if most_recent_golden is None and most_recent_death is None:
        return {'type': None, 'days_ago': None, 'cross_price': None}
    
    latest_date = valid_df.index[-1]
    
    if most_recent_golden and most_recent_death:
        if most_recent_golden > most_recent_death:
            cross_type = "GOLDEN_CROSS"
            cross_date = most_recent_golden
        else:
            cross_type = "DEATH_CROSS"
            cross_date = most_recent_death
    elif most_recent_golden:
        cross_type = "GOLDEN_CROSS"
        cross_date = most_recent_golden
    else:
        cross_type = "DEATH_CROSS"
        cross_date = most_recent_death
    
    days_ago = (latest_date - cross_date).days
    cross_price = valid_df.loc[cross_date, "Close"]
    
    return {
        'type': cross_type,
        'days_ago': days_ago,
        'cross_price': cross_price
    }


def cross_signal(df):
    """
    Check if a cross happened in the last trading day (immediate cross detection)
    
    Returns:
        str: 'GOLDEN_CROSS' | 'DEATH_CROSS' | None
    """
    if len(df) < 2:
        return None

    # Get last two valid rows
    valid_df = df.dropna(subset=["DMA50", "DMA200"])
    
    if len(valid_df) < 2:
        return None
    
    prev = valid_df.iloc[-2]
    curr = valid_df.iloc[-1]

    if prev["DMA50"] < prev["DMA200"] and curr["DMA50"] > curr["DMA200"]:
        return "GOLDEN_CROSS"
    if prev["DMA50"] > prev["DMA200"] and curr["DMA50"] < curr["DMA200"]:
        return "DEATH_CROSS"
    return None