from stockeye.core.indicators import detect_market_regime, fetch_india_vix
from stockeye.data.load_data import load_nse_symbols
from stockeye.services.analyzer import analyze_stock
from stockeye.services.data_fetcher import fetch_stock


def scan_for_strong_buys(index="NIFTY_50", limit=50, period="1y"):
    """
    Scan for top STRONG BUY/BUY stocks using enhanced logic
    """
    results = []
    symbols = load_nse_symbols(index)
    
    # Fetch market context once
    vix = fetch_india_vix()
    try:
        nifty, _ = fetch_stock("^NSEI", "1y")
        regime = detect_market_regime(nifty)
    except:
        regime = "UNKNOWN"

    for symbol in symbols:
        stock_data = analyze_stock(symbol, period, vix, regime)
        # Score >= 6 corresponds to BUY and STRONG BUY
        if stock_data and stock_data.get("rating_score", 0) >= 6:
            results.append(stock_data)
    
    # Sort by rating score (desc) then fscore (desc)
    results.sort(key=lambda x: (x.get("rating_score", 0), x.get("fscore", 0)), reverse=True)
    return results[:limit]
