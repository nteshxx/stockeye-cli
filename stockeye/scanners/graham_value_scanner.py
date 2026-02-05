

from stockeye.core.fundamentals import fundamental_score
from stockeye.core.margin_of_safety import conservative_intrinsic_value, graham_rating, intrinsic_value, margin_of_safety
from stockeye.data.load_data import load_nse_symbols
from stockeye.services.data_fetcher import clear_expired_cache, fetch_stock_batch
from stockeye.utils.utilities import safe_float, safe_get, safe_int


def analyze_stock_mos_value(symbol, df, info, conservative=False):
    """
    Analyze a single stock for Graham-style value with null safety
    
    Returns:
        dict or None: Value analysis data or None if error
    """
    try:
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
    

def scan_for_graham_value(index="NIFTY_50", limit=50, min_mos=30, conservative=False, batch_size=50):
    """
    Scan for Graham-style value stocks (Margin of Safety analysis) with null safety
    
    Args:
        index: Stock index to scan
        limit: Maximum number of results
        min_mos: Minimum Margin of Safety percentage
        conservative: Use conservative valuation method
        batch_size: Number of stocks to process in one memory cycle
    
    Returns:
        list: Value stocks sorted by MOS percentage
    """
    results = []
    symbols = load_nse_symbols(index)
    symbols = sorted(symbols)
    total_symbols = len(symbols)

    clear_expired_cache()

    for i in range(0, total_symbols, batch_size):
        current_batch = symbols[i : i + batch_size]
        stock_data = fetch_stock_batch(current_batch, period="5y")
    
        for symbol in current_batch:
            df, info = safe_get(stock_data, symbol)
            value_data = analyze_stock_mos_value(symbol, df, info, conservative=conservative)
            if value_data and value_data.get("mos_pct", 0) >= min_mos:
                results.append(value_data)
    
    # Sort by MOS percentage (descending)
    results.sort(key=lambda x: x.get("mos_pct", 0), reverse=True)
    
    return results[:limit]
