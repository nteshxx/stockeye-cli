import pandas as pd
import pandas_ta as ta


def add_dma(df, short, long):
    """Add DMA (Daily Moving Average) indicators with null safety"""
    if df is None or df.empty:
        return df
        
    try:
        df["DMA50"] = ta.sma(df["Close"], length=short)
        df["DMA200"] = ta.sma(df["Close"], length=long)
    except Exception as e:
        print(f"Error adding DMA: {str(e)}")
        df["DMA50"] = None
        df["DMA200"] = None
        
    return df


def add_rsi(df, period=14):
    """
    Add RSI (Relative Strength Index) indicator with null safety
    
    RSI Interpretation:
    - RSI > 70: Overbought (potential sell signal)
    - RSI < 30: Oversold (potential buy signal)
    - 30-70: Neutral zone
    """
    if df is None or df.empty:
        return df
        
    try:
        df["RSI"] = ta.rsi(df["Close"], length=period)
    except Exception as e:
        print(f"Error adding RSI: {str(e)}")
        df["RSI"] = None
        
    return df


def add_macd(df, fast=12, slow=26, signal=9):
    """
    Add MACD (Moving Average Convergence Divergence) indicator with null safety
    
    Returns MACD line, Signal line, and Histogram
    
    MACD Interpretation:
    - MACD > Signal: Bullish momentum
    - MACD < Signal: Bearish momentum
    - Histogram > 0: Bullish
    - Histogram < 0: Bearish
    """
    if df is None or df.empty:
        return df
        
    try:
        macd = ta.macd(df["Close"], fast=fast, slow=slow, signal=signal)
        
        if macd is not None and not macd.empty:
            df["MACD"] = macd[f"MACD_{fast}_{slow}_{signal}"]
            df["MACD_Signal"] = macd[f"MACDs_{fast}_{slow}_{signal}"]
            df["MACD_Hist"] = macd[f"MACDh_{fast}_{slow}_{signal}"]
        else:
            df["MACD"] = None
            df["MACD_Signal"] = None
            df["MACD_Hist"] = None
    except Exception as e:
        print(f"Error adding MACD: {str(e)}")
        df["MACD"] = None
        df["MACD_Signal"] = None
        df["MACD_Hist"] = None
    
    return df


def analyze_volume(df, period=20):
    """
    Analyze volume patterns and add volume indicators with null safety
    
    Returns:
    - Volume SMA (average volume)
    - Volume ratio (current vs average)
    - Volume trend
    """
    if df is None or df.empty:
        return df
        
    try:
        df["Volume_SMA"] = ta.sma(df["Volume"], length=period)
        
        # Safely calculate volume ratio
        df["Volume_Ratio"] = None
        valid_mask = (df["Volume_SMA"].notna()) & (df["Volume_SMA"] != 0)
        df.loc[valid_mask, "Volume_Ratio"] = df.loc[valid_mask, "Volume"] / df.loc[valid_mask, "Volume_SMA"]
    except Exception as e:
        print(f"Error analyzing volume: {str(e)}")
        df["Volume_SMA"] = None
        df["Volume_Ratio"] = None
    
    return df


def get_rsi_signal(rsi):
    """
    Get RSI trading signal with null safety
    
    Returns: 'OVERSOLD' | 'OVERBOUGHT' | 'NEUTRAL' | None
    """
    if rsi is None or pd.isna(rsi):
        return None
    
    try:
        rsi = float(rsi)
        if rsi < 30:
            return "OVERSOLD"
        elif rsi > 70:
            return "OVERBOUGHT"
        else:
            return "NEUTRAL"
    except (ValueError, TypeError):
        return None


def get_macd_signal(macd, macd_signal, macd_hist):
    """
    Get MACD trading signal with null safety
    
    Returns: 'BULLISH' | 'BEARISH' | 'NEUTRAL' | None
    """
    if macd is None or macd_signal is None or macd_hist is None:
        return None
        
    if pd.isna(macd) or pd.isna(macd_signal) or pd.isna(macd_hist):
        return None
    
    try:
        macd = float(macd)
        macd_signal = float(macd_signal)
        macd_hist = float(macd_hist)
        
        if macd > macd_signal and macd_hist > 0:
            return "BULLISH"
        elif macd < macd_signal and macd_hist < 0:
            return "BEARISH"
        else:
            return "NEUTRAL"
    except (ValueError, TypeError):
        return None


def get_volume_signal(volume_ratio):
    """
    Get volume analysis signal with null safety
    
    Returns: 'HIGH' | 'NORMAL' | 'LOW' | None
    """
    if volume_ratio is None or pd.isna(volume_ratio):
        return None
    
    try:
        volume_ratio = float(volume_ratio)
        if volume_ratio > 1.5:
            return "HIGH"
        elif volume_ratio < 0.5:
            return "LOW"
        else:
            return "NORMAL"
    except (ValueError, TypeError):
        return None


def detect_cross_age(df):
    """
    Detect the most recent Golden/Death Cross and calculate days since occurrence
    with comprehensive null safety
    
    Returns:
        dict: {
            'type': 'GOLDEN_CROSS' | 'DEATH_CROSS' | None,
            'days_ago': int | None,
            'cross_price': float | None
        }
    """
    default_result = {'type': None, 'days_ago': None, 'cross_price': None}
    
    if df is None or df.empty or len(df) < 2:
        return default_result
    
    if "DMA50" not in df.columns or "DMA200" not in df.columns:
        return default_result
        
    if df["DMA50"].isna().all() or df["DMA200"].isna().all():
        return default_result
    
    try:
        # Create a valid dataframe without NaN values for both DMAs
        valid_df = df.dropna(subset=["DMA50", "DMA200"]).copy()
        
        if len(valid_df) < 2:
            return default_result
        
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
            return default_result
        
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
            'cross_price': float(cross_price) if cross_price is not None else None
        }
    except Exception as e:
        print(f"Error detecting cross age: {str(e)}")
        return default_result


def cross_signal(df):
    """
    Check if a cross happened in the last trading day (immediate cross detection)
    with null safety
    
    Returns:
        str: 'GOLDEN_CROSS' | 'DEATH_CROSS' | None
    """
    if df is None or df.empty or len(df) < 2:
        return None

    if "DMA50" not in df.columns or "DMA200" not in df.columns:
        return None

    try:
        # Get last two valid rows
        valid_df = df.dropna(subset=["DMA50", "DMA200"])
        
        if len(valid_df) < 2:
            return None
        
        prev = valid_df.iloc[-2]
        curr = valid_df.iloc[-1]
        
        # Null safety for comparisons
        prev_dma50 = prev.get("DMA50")
        prev_dma200 = prev.get("DMA200")
        curr_dma50 = curr.get("DMA50")
        curr_dma200 = curr.get("DMA200")
        
        if any(x is None or pd.isna(x) for x in [prev_dma50, prev_dma200, curr_dma50, curr_dma200]):
            return None

        if prev_dma50 < prev_dma200 and curr_dma50 > curr_dma200:
            return "GOLDEN_CROSS"
        if prev_dma50 > prev_dma200 and curr_dma50 < curr_dma200:
            return "DEATH_CROSS"
        return None
    except Exception as e:
        print(f"Error in cross_signal: {str(e)}")
        return None
