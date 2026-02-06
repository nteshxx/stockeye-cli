from stockeye.config import BATCH_SIZE, PERIOD
from stockeye.core.indicators import detect_market_regime, fetch_india_vix
from stockeye.data.load_data import load_nse_symbols
from stockeye.services.analyzer import analyze_stock
from stockeye.services.data_fetcher import clear_expired_cache, fetch_stock, fetch_stock_batch
from stockeye.utils.utilities import safe_get


def scan_for_fundamentally_strong(index="NIFTY_50", limit=50, period="1y"):
    """
    Scan for fundamentally strong stocks (F-Score >= 8 out of 12)
    """
    results = []
    symbols = load_nse_symbols(index)
    symbols = sorted(symbols)
    total_symbols = len(symbols)

    clear_expired_cache()
    
    # Fetch market context once
    vix = fetch_india_vix()
    try:
        nifty, _ = fetch_stock("^NSEI", "1y")
        regime = detect_market_regime(nifty)
    except:
        regime = "UNKNOWN"

    for i in range(0, total_symbols, BATCH_SIZE):
        current_batch = symbols[i : i + BATCH_SIZE]
        stock_data = fetch_stock_batch(current_batch, period=PERIOD)
        
        for symbol in current_batch:
            df, info = safe_get(stock_data, symbol)
            analyzed_stock = analyze_stock(symbol, df, info, vix, regime)
            # Fundamental score >= 9 corresponds to Strong Fundamentals
            if analyzed_stock and safe_get(analyzed_stock, "fscore", 0) >= 9:
                results.append(analyzed_stock)
    
    results.sort(key=lambda x: (x.get("fscore", 0), x.get("rating_score", 0)), reverse=True)
    return results[:limit]
