import pandas as pd
import pandas_ta as ta
import yfinance as yf


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
    """Add RSI with null safety"""
    if df is None or df.empty:
        return df
        
    try:
        df["RSI"] = ta.rsi(df["Close"], length=period)
    except Exception as e:
        print(f"Error adding RSI: {str(e)}")
        df["RSI"] = None
        
    return df


def add_macd(df, fast=12, slow=26, signal=9):
    """Add MACD with null safety"""
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


def add_bollinger_bands(df, period=20, std_dev=2):
    """
    Add Bollinger Bands - popular in Indian intraday trading
    """
    if df is None or df.empty:
        return df
        
    try:
        df["BB_Middle"] = ta.sma(df["Close"], length=period)
        df["BB_Std"] = df["Close"].rolling(window=period).std()
        df["BB_Upper"] = df["BB_Middle"] + (std_dev * df["BB_Std"])
        df["BB_Lower"] = df["BB_Middle"] - (std_dev * df["BB_Std"])
        
        # BB position indicator (0-100)
        df["BB_Position"] = None
        valid_mask = (df["BB_Upper"] - df["BB_Lower"]) != 0
        df.loc[valid_mask, "BB_Position"] = (
            (df.loc[valid_mask, "Close"] - df.loc[valid_mask, "BB_Lower"]) / 
            (df.loc[valid_mask, "BB_Upper"] - df.loc[valid_mask, "BB_Lower"])
        ) * 100
        
    except Exception as e:
        print(f"Error adding Bollinger Bands: {str(e)}")
        df["BB_Middle"] = None
        df["BB_Upper"] = None
        df["BB_Lower"] = None
        df["BB_Position"] = None
    
    return df


def add_supertrend(df, period=10, multiplier=3):
    """
    Add Supertrend indicator - very popular in Indian market
    """
    if df is None or df.empty:
        return df
        
    try:
        supertrend = ta.supertrend(df["High"], df["Low"], df["Close"], 
                                    length=period, multiplier=multiplier)
        if supertrend is not None and not supertrend.empty:
            df["Supertrend"] = supertrend[f"SUPERT_{period}_{multiplier}"]
            df["Supertrend_Direction"] = supertrend[f"SUPERTd_{period}_{multiplier}"]
        else:
            df["Supertrend"] = None
            df["Supertrend_Direction"] = None
    except Exception as e:
        print(f"Error adding Supertrend: {str(e)}")
        df["Supertrend"] = None
        df["Supertrend_Direction"] = None
    
    return df


def add_adx(df, period=14):
    """
    Add ADX (Average Directional Index) - measures trend strength
    ADX > 25 = Strong trend
    ADX < 20 = Weak trend
    """
    if df is None or df.empty:
        return df
        
    try:
        adx = ta.adx(df["High"], df["Low"], df["Close"], length=period)
        if adx is not None and not adx.empty:
            df["ADX"] = adx[f"ADX_{period}"]
            df[f"DMP_{period}"] = adx[f"DMP_{period}"]  # Positive directional movement
            df[f"DMN_{period}"] = adx[f"DMN_{period}"]  # Negative directional movement
        else:
            df["ADX"] = None
    except Exception as e:
        print(f"Error adding ADX: {str(e)}")
        df["ADX"] = None
    
    return df


def analyze_volume(df, period=20):
    """Volume analysis with null safety"""
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
    """Get RSI trading signal with null safety"""
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
    """Get MACD trading signal with null safety"""
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
    """Get volume analysis signal with null safety"""
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


def get_bollinger_signal(bb_position):
    """
    Get Bollinger Band signal
    Returns: 'OVERSOLD' | 'OVERBOUGHT' | 'NEUTRAL' | None
    """
    if bb_position is None or pd.isna(bb_position):
        return None
    
    try:
        bb_position = float(bb_position)
        if bb_position < 20:
            return "OVERSOLD"
        elif bb_position > 80:
            return "OVERBOUGHT"
        else:
            return "NEUTRAL"
    except (ValueError, TypeError):
        return None


def get_supertrend_signal(price, supertrend, direction):
    """
    Get Supertrend signal
    Returns: 'BULLISH' | 'BEARISH' | None
    """
    if any(x is None or pd.isna(x) for x in [price, supertrend, direction]):
        return None
    
    try:
        direction = float(direction)
        if direction == 1:
            return "BULLISH"
        elif direction == -1:
            return "BEARISH"
        else:
            return None
    except (ValueError, TypeError):
        return None


def get_adx_signal(adx):
    """
    Get ADX trend strength signal
    Returns: 'STRONG_TREND' | 'WEAK_TREND' | 'MODERATE' | None
    """
    if adx is None or pd.isna(adx):
        return None
    
    try:
        adx = float(adx)
        if adx > 25:
            return "STRONG_TREND"
        elif adx < 20:
            return "WEAK_TREND"
        else:
            return "MODERATE"
    except (ValueError, TypeError):
        return None


def detect_cross_age(df):
    """Detect Golden/Death Cross with null safety"""
    default_result = {'type': None, 'days_ago': None, 'cross_price': None}
    
    if df is None or df.empty or len(df) < 2:
        return default_result
    
    if "DMA50" not in df.columns or "DMA200" not in df.columns:
        return default_result
        
    if df["DMA50"].isna().all() or df["DMA200"].isna().all():
        return default_result
    
    try:
        valid_df = df.dropna(subset=["DMA50", "DMA200"]).copy()
        
        if len(valid_df) < 2:
            return default_result
        
        valid_df["signal"] = 0
        valid_df.loc[valid_df["DMA50"] > valid_df["DMA200"], "signal"] = 1
        valid_df.loc[valid_df["DMA50"] < valid_df["DMA200"], "signal"] = -1
        
        valid_df["cross"] = valid_df["signal"].diff()
        
        golden_crosses = valid_df[valid_df["cross"] > 0]
        death_crosses = valid_df[valid_df["cross"] < 0]
        
        most_recent_golden = golden_crosses.index[-1] if len(golden_crosses) > 0 else None
        most_recent_death = death_crosses.index[-1] if len(death_crosses) > 0 else None
        
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
    """Check for immediate cross with null safety"""
    if df is None or df.empty or len(df) < 2:
        return None

    if "DMA50" not in df.columns or "DMA200" not in df.columns:
        return None

    try:
        valid_df = df.dropna(subset=["DMA50", "DMA200"])
        
        if len(valid_df) < 2:
            return None
        
        prev = valid_df.iloc[-2]
        curr = valid_df.iloc[-1]
        
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


def fetch_india_vix():
    """
    Fetch India VIX (volatility index)
    Returns current VIX value or None
    """
    try:
        vix = yf.Ticker("^INDIAVIX")
        hist = vix.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception as e:
        print(f"Error fetching India VIX: {str(e)}")
    return None


def calculate_relative_strength(stock_df, nifty_df, period=90):
    """
    Calculate Relative Strength vs Nifty 50
    Returns (status, percentage) tuple
    """
    try:
        if len(stock_df) < period or len(nifty_df) < period:
            return None, None
        
        stock_start = stock_df["Close"].iloc[-period]
        stock_end = stock_df["Close"].iloc[-1]
        nifty_start = nifty_df["Close"].iloc[-period]
        nifty_end = nifty_df["Close"].iloc[-1]
        
        stock_change = ((stock_end - stock_start) / stock_start) * 100
        nifty_change = ((nifty_end - nifty_start) / nifty_start) * 100
        
        relative_strength = stock_change - nifty_change
        
        if relative_strength > 10:
            return "OUTPERFORMING", relative_strength
        elif relative_strength < -10:
            return "UNDERPERFORMING", relative_strength
        else:
            return "INLINE", relative_strength
    except Exception as e:
        print(f"Error calculating relative strength: {str(e)}")
        return None, None


def detect_market_regime(nifty_data):
    """
    Detect if market is in bull/bear/sideways phase
    """
    try:
        if len(nifty_data) < 200:
            return "UNKNOWN"
        
        sma_50 = nifty_data["Close"].rolling(50).mean().iloc[-1]
        sma_200 = nifty_data["Close"].rolling(200).mean().iloc[-1]
        current_price = nifty_data["Close"].iloc[-1]
        
        # Bull market
        if current_price > sma_50 > sma_200:
            return "BULL"
        # Bear market  
        elif current_price < sma_50 < sma_200:
            return "BEAR"
        # Sideways
        else:
            return "SIDEWAYS"
    except Exception as e:
        print(f"Error detecting market regime: {str(e)}")
        return "UNKNOWN"


def get_calendar_month_signal(month):
    """
    Get calendar effect for Indian market
    Returns: 'FAVORABLE' | 'UNFAVORABLE' | 'NEUTRAL' | 'VOLATILE'
    """
    # Based on research: January-February volatile (budget), 
    # March & September unfavorable, December favorable
    if month in [1, 2]:
        return "VOLATILE"  # Budget season
    elif month == 12:
        return "FAVORABLE"  # Good prospects
    elif month in [3, 9]:
        return "UNFAVORABLE"  # Poor performance historically
    else:
        return "NEUTRAL"


def check_liquidity(avg_volume, avg_value_traded):
    """
    Check if stock has adequate liquidity
    Returns: 'OK' | 'LOW_LIQUIDITY'
    """
    MIN_VOLUME = 100000  # 1 lakh shares
    MIN_VALUE = 5000000  # Rs 50 lakhs
    
    if avg_volume is None or avg_value_traded is None:
        return "UNKNOWN"
    
    try:
        if avg_volume < MIN_VOLUME or avg_value_traded < MIN_VALUE:
            return "LOW_LIQUIDITY"
        return "OK"
    except:
        return "UNKNOWN"
    