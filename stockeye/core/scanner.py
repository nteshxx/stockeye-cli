"""
Market Scanner - Find top stocks across different categories
"""
import pandas as pd
from stockeye.core.data_fetcher import fetch_stock
from stockeye.core.indicators import (
    add_dma, add_rsi, add_macd, analyze_volume,
    detect_cross_age, get_rsi_signal, get_macd_signal, get_volume_signal
)
from stockeye.core.fundamentals import fundamental_score
from stockeye.core.rating import rating, get_rating_score
from stockeye.data.load_data import load_nse_data


def get_stock_index(index="NIFTY_50"):
    """
    Get predefined stock indexes
    
    Args:
        index: "NIFTY_50", "NIFTY_NEXT_50", "NIFTY_500"
    
    Returns:
        list: Stock symbols
    """
    return load_nse_data(index.upper())


def analyze_stock(symbol, period="1y"):
    """
    Analyze a single stock and return all metrics
    
    Returns:
        dict or None: Stock analysis data or None if error
    """
    try:
        df, info = fetch_stock(symbol, period)
        
        if df is None or len(df) < 50:
            return None
        
        # Add all indicators
        df = add_dma(df, 50, 200)
        df = add_rsi(df)
        df = add_macd(df)
        df = analyze_volume(df)
        
        last = df.iloc[-1]
        fscore = fundamental_score(info)
        
        # Get indicator signals
        rsi = last.get("RSI")
        rsi_signal = get_rsi_signal(rsi)
        
        macd_val = last.get("MACD")
        macd_sig = last.get("MACD_Signal")
        macd_hist = last.get("MACD_Hist")
        macd_signal = get_macd_signal(macd_val, macd_sig, macd_hist)
        
        volume_ratio = last.get("Volume_Ratio")
        volume_signal = get_volume_signal(volume_ratio)
        
        # Detect cross
        cross_info = detect_cross_age(df)
        
        # Generate rating
        stock_rating = rating(
            last["Close"],
            last["DMA50"],
            last["DMA200"],
            fscore,
            cross_info,
            rsi,
            macd_signal,
            volume_signal
        )
        
        return {
            "symbol": symbol,
            "price": last["Close"],
            "dma50": last["DMA50"],
            "dma200": last["DMA200"],
            "rsi": rsi,
            "rsi_signal": rsi_signal,
            "macd_signal": macd_signal,
            "volume_signal": volume_signal,
            "fscore": fscore,
            "cross_info": cross_info,
            "rating": stock_rating,
            "rating_score": get_rating_score(stock_rating),
            "market_cap": info.get("marketCap", 0),
            "company_name": info.get("longName", symbol)
        }
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {str(e)}")
        return None


def scan_for_strong_buys(index="NIFTY_50", limit=50, period="1y"):
    """
    Scan for top STRONG BUY stocks
    
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
        if stock_data and stock_data["rating_score"] >= 6:  # BUY or STRONG BUY
            results.append(stock_data)
    
    # Sort by rating score (descending), then by fscore
    results.sort(key=lambda x: (x["rating_score"], x["fscore"]), reverse=True)
    
    return results[:limit]


def scan_for_fundamentally_strong(index="NIFTY_50", limit=50, period="1y"):
    """
    Scan for fundamentally strong stocks (high F-Score)
    
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
        if stock_data and stock_data["fscore"] >= 5:  # Good fundamentals
            results.append(stock_data)
    
    # Sort by fscore (descending), then by rating score
    results.sort(key=lambda x: (x["fscore"], x["rating_score"]), reverse=True)
    
    return results[:limit]


def scan_for_value_opportunities(index="NIFTY_50", limit=50, period="1y"):
    """
    Scan for value opportunities (strong fundamentals but temporarily weak price)
    
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
            # Strong fundamentals (≥6) but oversold or ADD rating
            if stock_data["fscore"] >= 6:
                if (stock_data["rsi"] and stock_data["rsi"] < 40) or \
                   stock_data["rating"] in ["ADD 🔵", "BUY 🟢"]:
                    results.append(stock_data)
    
    # Sort by fscore, prioritizing oversold conditions
    results.sort(key=lambda x: (x["fscore"], -x["rsi"] if x["rsi"] else 0), reverse=True)
    
    return results[:limit]
    