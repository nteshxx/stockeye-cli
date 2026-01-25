"""
Market Scanner - Find top stocks across different categories
"""
from stockeye.core.data_fetcher import fetch_stock
from stockeye.core.indicators import (
    add_dma, add_rsi, add_macd, analyze_volume,
    detect_cross_age, get_rsi_signal, get_macd_signal, get_volume_signal
)
from stockeye.core.fundamentals import fundamental_score
from stockeye.core.rating import rating, get_rating_score

# Popular stock universes for different markets
INDIAN_NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "HCLTECH.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
    "WIPRO.NS", "ADANIPORTS.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS",
    "M&M.NS", "TECHM.NS", "BAJAJFINSV.NS", "TATASTEEL.NS",
    "INDUSINDBK.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "CIPLA.NS",
    "COALINDIA.NS", "BPCL.NS", "GRASIM.NS", "BRITANNIA.NS", "SHRIRAMFIN.NS",
    "APOLLOHOSP.NS", "TATACONSUM.NS", "ADANIENT.NS", "HINDALCO.NS", "JSWSTEEL.NS",
    "HEROMOTOCO.NS", "UPL.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS", "LTIM.NS"
]

INDIAN_NIFTY_NEXT_50 = [
    "ADANIGREEN.NS", "ADANIPOWER.NS", "BANKBARODA.NS", "BOSCHLTD.NS", "CHOLAFIN.NS",
    "COLPAL.NS", "DABUR.NS", "DLF.NS", "GAIL.NS", "GODREJCP.NS",
    "HDFCLIFE.NS", "HAVELLS.NS", "ICICIPRULI.NS", "INDIGO.NS", "JINDALSTEL.NS",
    "MOTHERSON.NS", "MUTHOOTFIN.NS", "NMDC.NS", "OFSS.NS", "PAGEIND.NS",
    "PIDILITIND.NS", "PNB.NS", "SIEMENS.NS", "SRF.NS", "TATAPOWER.NS",
    "TORNTPHARM.NS", "TRENT.NS", "VEDL.NS", "VOLTAS.NS", "ZOMATO.NS",
    "AUROPHARMA.NS", "BAJAJHLDNG.NS", "BERGEPAINT.NS", "BEL.NS", "CANBK.NS",
    "RECLTD.NS", "DIXON.NS", "DMART.NS", "HAL.NS", "ICICIGI.NS",
    "IRCTC.NS", "JIOFIN.NS", "MAXHEALTH.NS", "NAUKRI.NS", "POLICYBZR.NS",
    "PFC.NS", "SAIL.NS", "SHREECEM.NS", "TVSMOTOR.NS", "ZYDUSLIFE.NS"
]

US_SP500_MEGA_CAPS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "LLY", "AVGO", "V", "JPM", "WMT", "XOM", "UNH", "MA", "ORCL",
    "COST", "HD", "PG", "JNJ", "NFLX", "BAC", "ABBV", "CRM",
    "KO", "MRK", "CVX", "AMD", "PEP", "ADBE", "TMO", "ACN",
    "MCD", "CSCO", "ABT", "DHR", "WFC", "LIN", "TXN", "INTU",
    "QCOM", "IBM", "VZ", "AMGN", "PM", "CAT", "NOW", "GE", "ISRG"
]


def get_stock_universe(universe="NIFTY50"):
    """
    Get predefined stock universe
    
    Args:
        universe: "NIFTY50", "NIFTY_NEXT_50", "US_MEGA_CAPS", or "ALL_INDIAN"
    
    Returns:
        list: Stock symbols
    """
    universes = {
        "NIFTY50": INDIAN_NIFTY_50,
        "NIFTY_NEXT_50": INDIAN_NIFTY_NEXT_50,
        "ALL_INDIAN": INDIAN_NIFTY_50 + INDIAN_NIFTY_NEXT_50,
        "US_MEGA_CAPS": US_SP500_MEGA_CAPS
    }
    
    return universes.get(universe.upper(), INDIAN_NIFTY_50)


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


def scan_for_strong_buys(universe="NIFTY50", limit=50, period="1y"):
    """
    Scan for top STRONG BUY stocks
    
    Args:
        universe: Stock universe to scan
        limit: Maximum number of results
        period: Data period
    
    Returns:
        list: Top strong buy stocks sorted by rating score
    """
    symbols = get_stock_universe(universe)
    results = []
    
    for symbol in symbols:
        stock_data = analyze_stock(symbol, period)
        if stock_data and stock_data["rating_score"] >= 6:  # BUY or STRONG BUY
            results.append(stock_data)
    
    # Sort by rating score (descending), then by fscore
    results.sort(key=lambda x: (x["rating_score"], x["fscore"]), reverse=True)
    
    return results[:limit]


def scan_for_fundamentally_strong(universe="NIFTY50", limit=50, period="1y"):
    """
    Scan for fundamentally strong stocks (high F-Score)
    
    Args:
        universe: Stock universe to scan
        limit: Maximum number of results
        period: Data period
    
    Returns:
        list: Top fundamental stocks sorted by F-Score
    """
    symbols = get_stock_universe(universe)
    results = []
    
    for symbol in symbols:
        stock_data = analyze_stock(symbol, period)
        if stock_data and stock_data["fscore"] >= 5:  # Good fundamentals
            results.append(stock_data)
    
    # Sort by fscore (descending), then by rating score
    results.sort(key=lambda x: (x["fscore"], x["rating_score"]), reverse=True)
    
    return results[:limit]


def scan_for_value_opportunities(universe="NIFTY50", limit=50, period="1y"):
    """
    Scan for value opportunities (strong fundamentals but temporarily weak price)
    
    Args:
        universe: Stock universe to scan
        limit: Maximum number of results
        period: Data period
    
    Returns:
        list: Value opportunity stocks
    """
    symbols = get_stock_universe(universe)
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
    