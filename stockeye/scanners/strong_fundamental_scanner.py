from stockeye.core.indicators import fetch_india_vix
from stockeye.data.load_data import load_nse_symbols
from stockeye.services.analyzer import analyze_stock


def scan_for_fundamentally_strong(index="NIFTY_50", limit=50, period="1y"):
    """
    Scan for fundamentally strong stocks (F-Score >= 8 out of 12)
    """
    results = []
    symbols = load_nse_symbols(index)
    
    # Fetch VIX once
    vix = fetch_india_vix()

    for symbol in symbols:
        stock_data = analyze_stock(symbol, period, vix_value=vix)
        # Threshold updated for 12-point scale (approx 66% quality)
        if stock_data and stock_data.get("fscore", 0) >= 8:
            results.append(stock_data)
    
    results.sort(key=lambda x: (x.get("fscore", 0), x.get("rating_score", 0)), reverse=True)
    return results[:limit]
