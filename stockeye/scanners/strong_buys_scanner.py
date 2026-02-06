from stockeye.config import BATCH_SIZE, PERIOD
from stockeye.core.indicators import detect_market_regime, fetch_india_vix
from stockeye.data.load_data import load_nse_symbols
from stockeye.services.analyzer import analyze_stock
from stockeye.services.data_fetcher import clear_expired_cache, fetch_stock, fetch_stock_batch
from stockeye.utils.utilities import safe_get


def scan_for_strong_buys(index="NIFTY_50", limit=1000, period="1y"):
    """
    Scan for top STRONG BUY/BUY stocks using enhanced logic
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
            # Rating score >= 6 corresponds to BUY and STRONG BUY
            if analyzed_stock and safe_get(analyzed_stock, "rating_score", 0) >= 6:
                results.append(analyzed_stock)
    
    # Sort by rating score (desc) then fscore (desc)
    results.sort(key=lambda x: (x.get("rating_score", 0), x.get("fscore", 0)), reverse=True)
    return results[:limit]
