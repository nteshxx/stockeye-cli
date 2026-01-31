"""
Market Scanner - Find top stocks across different categories
"""
import pandas as pd
from stockeye.services.data_fetcher import fetch_stock
from stockeye.core.indicators import (
    add_dma, add_rsi, add_macd, analyze_volume,
    detect_cross_age, get_rsi_signal, get_macd_signal, get_volume_signal
)
from stockeye.core.margin_of_safety import (
    calculate_growth,
    intrinsic_value,
    margin_of_safety,
    graham_rating,
    conservative_intrinsic_value
)
from stockeye.core.fundamentals import fundamental_score
from stockeye.core.rating import rating, get_rating_score
from stockeye.data.load_data import load_nse_data


def safe_get(data, key, default=None):
    """Safely get value from dict/Series with null checking"""
    if data is None:
        return default
    try:
        value = data.get(key, default) if hasattr(data, 'get') else data[key]
        if pd.isna(value):
            return default
        return value
    except (KeyError, TypeError, AttributeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert to float"""
    if value is None or pd.isna(value):
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """Safely convert to int"""
    if value is None or pd.isna(value):
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def get_stock_index(index="NIFTY_50"):
    """
    Get predefined stock indexes
    
    Args:
        index: "NIFTY_50", "NIFTY_NEXT_50", "NIFTY_500"
    
    Returns:
        list: Stock symbols
    """
    try:
        return load_nse_data(index.upper())
    except Exception as e:
        print(f"Error loading stock index {index}: {str(e)}")
        return []


def analyze_stock(symbol, period="1y"):
    """
    Analyze a single stock and return all metrics with comprehensive null safety
    
    Returns:
        dict or None: Stock analysis data or None if error
    """
    try:
        df, info = fetch_stock(symbol, period)
        
        if df is None or info is None or len(df) < 50:
            return None
        
        # Add all indicators
        df = add_dma(df, 50, 200)
        df = add_rsi(df)
        df = add_macd(df)
        df = analyze_volume(df)
        
        if df is None or df.empty:
            return None
        
        last = df.iloc[-1]
        fscore = fundamental_score(info)
        
        # Get indicator signals with null safety
        rsi = safe_get(last, "RSI")
        rsi_signal = get_rsi_signal(rsi)
        
        macd_val = safe_get(last, "MACD")
        macd_sig = safe_get(last, "MACD_Signal")
        macd_hist = safe_get(last, "MACD_Hist")
        macd_signal = get_macd_signal(macd_val, macd_sig, macd_hist)
        
        volume_ratio = safe_get(last, "Volume_Ratio")
        volume_signal = get_volume_signal(volume_ratio)
        
        # Detect cross
        cross_info = detect_cross_age(df)
        if cross_info is None:
            cross_info = {'type': None, 'days_ago': None, 'cross_price': None}
        
        # Get values with null safety
        close_price = safe_float(safe_get(last, "Close"))
        dma50_val = safe_float(safe_get(last, "DMA50"))
        dma200_val = safe_float(safe_get(last, "DMA200"))
        
        # Generate rating
        stock_rating = rating(
            close_price,
            dma50_val,
            dma200_val,
            fscore,
            cross_info,
            rsi,
            macd_signal,
            volume_signal
        )
        
        return {
            "symbol": symbol,
            "price": close_price,
            "dma50": dma50_val,
            "dma200": dma200_val,
            "rsi": rsi,
            "rsi_signal": rsi_signal,
            "macd_signal": macd_signal,
            "volume_signal": volume_signal,
            "fscore": fscore,
            "cross_info": cross_info,
            "rating": stock_rating,
            "rating_score": get_rating_score(stock_rating),
            "market_cap": safe_int(info.get("marketCap", 0)),
            "company_name": info.get("longName", symbol)
        }
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {str(e)}")
        return None


def analyze_stock_mos_value(symbol, period="5y", conservative=False):
    """
    Analyze a single stock for Graham-style value with null safety
    
    Returns:
        dict or None: Value analysis data or None if error
    """
    try:
        df, info = fetch_stock(symbol, period)
        
        if df is None or info is None or len(df) < 50:
            return None
        
        price = safe_float(df['Close'].iloc[-1])
        
        if price <= 0:
            return None
        
        # Get EPS data with null safety
        trailing_eps = safe_float(info.get('trailingEps'), None)
        forward_eps = safe_float(info.get('forwardEps'), None)
        
        # Use average of available EPS
        eps_values = [e for e in [trailing_eps, forward_eps] if e is not None and e > 0]
        
        if not eps_values:
            return None
        
        avg_eps = sum(eps_values) / len(eps_values)
        
        # Estimate growth from revenue growth and earnings growth
        revenue_growth = safe_float(info.get('revenueGrowth'), 0) * 100
        earnings_growth = safe_float(info.get('earningsGrowth'), 0) * 100
        
        # Conservative growth estimate
        if revenue_growth != 0 or earnings_growth != 0:
            growth = (revenue_growth + earnings_growth) / 2
        else:
            growth = 0
            
        growth = max(-20, min(25, growth))  # Cap between -20% and 25%
        
        # Calculate intrinsic value
        if conservative:
            intrinsic = conservative_intrinsic_value(avg_eps, growth)
        else:
            intrinsic = intrinsic_value(avg_eps, growth)
        
        # Calculate margin of safety
        mos_value, mos_pct = margin_of_safety(intrinsic, price)
        
        return {
            "symbol": symbol,
            "company_name": info.get('longName', symbol),
            "price": price,
            "eps": avg_eps,
            "growth": growth,
            "intrinsic": intrinsic,
            "mos_value": mos_value,
            "mos_pct": mos_pct,
            "rating": graham_rating(mos_pct),
            "market_cap": safe_int(info.get("marketCap", 0)),
            "fscore": fundamental_score(info)
        }
        
    except Exception as e:
        print(f"Error analyzing value for {symbol}: {str(e)}")
        return None


def scan_for_strong_buys(index="NIFTY_50", limit=50, period="1y"):
    """
    Scan for top STRONG BUY stocks with null safety
    
    Args:
        index: Stock index to scan
        limit: Maximum number of results
        period: Data period
    
    Returns:
        list: Top strong buy stocks sorted by rating score
    """
    symbols = get_stock_index(index)
    results = []
    
    for symbol in symbols:
        stock_data = analyze_stock(symbol, period)
        if stock_data and stock_data.get("rating_score", 0) >= 6:  # BUY or STRONG BUY
            results.append(stock_data)
    
    # Sort by rating score (descending), then by fscore
    results.sort(key=lambda x: (x.get("rating_score", 0), x.get("fscore", 0)), reverse=True)
    
    return results[:limit]


def scan_for_fundamentally_strong(index="NIFTY_50", limit=50, period="1y"):
    """
    Scan for fundamentally strong stocks (high F-Score) with null safety
    
    Args:
        index: Stock index to scan
        limit: Maximum number of results
        period: Data period
    
    Returns:
        list: Top fundamental stocks sorted by F-Score
    """
    symbols = get_stock_index(index)
    results = []
    
    for symbol in symbols:
        stock_data = analyze_stock(symbol, period)
        if stock_data and stock_data.get("fscore", 0) >= 5:  # Good fundamentals
            results.append(stock_data)
    
    # Sort by fscore (descending), then by rating score
    results.sort(key=lambda x: (x.get("fscore", 0), x.get("rating_score", 0)), reverse=True)
    
    return results[:limit]


def scan_for_value_opportunities(index="NIFTY_50", limit=50, period="1y"):
    """
    Scan for value opportunities (strong fundamentals but temporarily weak price)
    with null safety
    
    Args:
        index: Stock index to scan
        limit: Maximum number of results
        period: Data period
    
    Returns:
        list: Value opportunity stocks
    """
    symbols = get_stock_index(index)
    results = []
    
    for symbol in symbols:
        stock_data = analyze_stock(symbol, period)
        if stock_data:
            fscore = stock_data.get("fscore", 0)
            rsi = stock_data.get("rsi")
            stock_rating = stock_data.get("rating", "")
            
            # Strong fundamentals (≥6) but oversold or ADD rating
            if fscore >= 6:
                if (rsi is not None and rsi < 40) or stock_rating in ["ADD 🔵", "BUY 🟢"]:
                    results.append(stock_data)
    
    # Sort by fscore, prioritizing oversold conditions
    def sort_key(x):
        fscore = x.get("fscore", 0)
        rsi = x.get("rsi")
        rsi_val = -rsi if rsi is not None else 0
        return (fscore, rsi_val)
    
    results.sort(key=sort_key, reverse=True)
    
    return results[:limit]


def scan_for_graham_value(index="NIFTY_50", limit=50, min_mos=30, conservative=False):
    """
    Scan for Graham-style value stocks (Margin of Safety analysis) with null safety
    
    Args:
        index: Stock index to scan
        limit: Maximum number of results
        min_mos: Minimum Margin of Safety percentage
        conservative: Use conservative valuation method
    
    Returns:
        list: Value stocks sorted by MOS percentage
    """
    symbols = get_stock_index(index)
    results = []
    
    for symbol in symbols:
        value_data = analyze_stock_mos_value(symbol, period="5y", conservative=conservative)
        if value_data and value_data.get("mos_pct", 0) >= min_mos:
            results.append(value_data)
    
    # Sort by MOS percentage (descending)
    results.sort(key=lambda x: x.get("mos_pct", 0), reverse=True)
    
    return results[:limit]
