"""
Graham Bargain Type Scanner
Scans stocks for classic Graham value opportunities across multiple scenarios
"""

from typing import List, Dict, Optional
from stockeye.config import BATCH_SIZE
from stockeye.data.load_data import load_nse_symbols
from stockeye.services.bargain_analyzer import GrahamScenario, analyze_graham_bargain
from stockeye.services.data_fetcher import clear_expired_cache, fetch_stock_batch
from stockeye.utils.utilities import safe_get


def scan_graham_bargains(
    index: str = "NIFTY_50",
    limit: int = 100,
    min_graham_score: int = 50,
    scenarios: Optional[List[str]] = None,
    min_scenario_score: int = 60
) -> List[Dict]:
    """
    Scan for Graham-style bargain opportunities
    
    Args:
        index: Stock index to scan (NIFTY_50, NIFTY_500, etc)
        limit: Maximum number of results
        min_graham_score: Minimum overall Graham score (0-100)
        scenarios: Filter by specific scenarios (None = all)
        min_scenario_score: Minimum scenario-specific score
        
    Returns:
        List of bargain stocks sorted by Graham score
    """
    results = []
    symbols = load_nse_symbols(index)
    symbols = sorted(symbols)
    total_symbols = len(symbols)
    
    # Clear expired cache entries
    clear_expired_cache()
    
    # Process in batches
    for i in range(0, total_symbols, BATCH_SIZE):
        current_batch = symbols[i : i + BATCH_SIZE]
        stock_data = fetch_stock_batch(current_batch, period="5y")
        
        for symbol in current_batch:
            df, info = safe_get(stock_data, symbol)
            analysis = analyze_graham_bargain(symbol, df, info)
            
            if analysis:
                # Apply filters
                if analysis.get("graham_score", 0) >= min_graham_score:
                    if analysis.get("scenario_score", 0) >= min_scenario_score:
                        if scenarios is None or analysis.get("scenario") in scenarios:
                            results.append(analysis)
    
    # Sort by Graham score (descending)
    results.sort(key=lambda x: x.get("graham_score", 0), reverse=True)
    
    return results[:limit]


def scan_net_nets(
    index: str = "NIFTY_500",
    limit: int = 50,
    max_net_net_ratio: float = 0.67
) -> List[Dict]:
    """
    Scan specifically for Net-Net stocks (Graham's favorite)
    
    Finds stocks trading below 2/3 of Net Current Asset Value
    
    Args:
        index: Stock index to scan
        limit: Maximum results
        max_net_net_ratio: Maximum price/NCAV ratio (default 0.67)
        
    Returns:
        List of net-net stocks sorted by net-net ratio
    """
    results = []
    symbols = load_nse_symbols(index)
    symbols = sorted(symbols)
    total_symbols = len(symbols)
    
    clear_expired_cache()
    
    for i in range(0, total_symbols, BATCH_SIZE):
        current_batch = symbols[i : i + BATCH_SIZE]
        stock_data = fetch_stock_batch(current_batch, period="5y")
        
        for symbol in current_batch:
            df, info = safe_get(stock_data, symbol)
            analysis = analyze_graham_bargain(symbol, df, info)
            
            if analysis and analysis.get("scenario") == GrahamScenario.NET_NET:
                net_net_ratio = analysis.get("net_net_ratio")
                if net_net_ratio and net_net_ratio <= max_net_net_ratio:
                    results.append(analysis)
    
    # Sort by net-net ratio (lower is better)
    results.sort(key=lambda x: x.get("net_net_ratio", 999))
    
    return results[:limit]


def scan_asset_plays(
    index: str = "NIFTY_500",
    limit: int = 50,
    max_pb_ratio: float = 0.8
) -> List[Dict]:
    """
    Scan for Asset Play opportunities
    
    Finds stocks trading below book value or liquidation value
    
    Args:
        index: Stock index to scan
        limit: Maximum results
        max_pb_ratio: Maximum P/B ratio (default 0.8)
        
    Returns:
        List of asset plays sorted by P/B ratio
    """
    results = []
    symbols = load_nse_symbols(index)
    symbols = sorted(symbols)
    total_symbols = len(symbols)
    
    clear_expired_cache()
    
    for i in range(0, total_symbols, BATCH_SIZE):
        current_batch = symbols[i : i + BATCH_SIZE]
        stock_data = fetch_stock_batch(current_batch, period="5y")
        
        for symbol in current_batch:
            df, info = safe_get(stock_data, symbol)
            analysis = analyze_graham_bargain(symbol, df, info)
            
            if analysis and analysis.get("scenario") == GrahamScenario.ASSET_PLAY:
                pb_ratio = analysis.get("pb_ratio")
                if pb_ratio and pb_ratio <= max_pb_ratio:
                    results.append(analysis)
    
    # Sort by P/B ratio (lower is better)
    results.sort(key=lambda x: x.get("pb_ratio", 999))
    
    return results[:limit]


def scan_cigar_butts(
    index: str = "NIFTY_500",
    limit: int = 50,
    min_cigar_score: int = 4
) -> List[Dict]:
    """
    Scan for Cigar Butt opportunities
    
    Finds beaten-down but still profitable stocks
    
    Args:
        index: Stock index to scan
        limit: Maximum results
        min_cigar_score: Minimum cigar butt score (out of 5)
        
    Returns:
        List of cigar butts sorted by cigar score
    """
    results = []
    symbols = load_nse_symbols(index)
    symbols = sorted(symbols)
    total_symbols = len(symbols)
    
    clear_expired_cache()
    
    for i in range(0, total_symbols, BATCH_SIZE):
        current_batch = symbols[i : i + BATCH_SIZE]
        stock_data = fetch_stock_batch(current_batch, period="5y")
        
        for symbol in current_batch:
            df, info = safe_get(stock_data, symbol)
            analysis = analyze_graham_bargain(symbol, df, info)
            
            if analysis and analysis.get("scenario") == GrahamScenario.CIGAR_BUTT:
                cigar_score = analysis.get("cigar_butt_score", 0)
                if cigar_score >= min_cigar_score:
                    results.append(analysis)
    
    # Sort by cigar butt score (higher is better)
    results.sort(key=lambda x: x.get("cigar_butt_score", 0), reverse=True)
    
    return results[:limit]


def scan_defensive_stocks(
    index: str = "NIFTY_50",
    limit: int = 50,
    min_defensive_score: int = 5
) -> List[Dict]:
    """
    Scan for Defensive Investor stocks
    
    Finds quality stocks meeting Graham's defensive criteria
    
    Args:
        index: Stock index to scan
        limit: Maximum results
        min_defensive_score: Minimum defensive score (out of 7)
        
    Returns:
        List of defensive stocks sorted by defensive score
    """
    results = []
    symbols = load_nse_symbols(index)
    symbols = sorted(symbols)
    total_symbols = len(symbols)
    
    clear_expired_cache()
    
    for i in range(0, total_symbols, BATCH_SIZE):
        current_batch = symbols[i : i + BATCH_SIZE]
        stock_data = fetch_stock_batch(current_batch, period="5y")
        
        for symbol in current_batch:
            df, info = safe_get(stock_data, symbol)
            analysis = analyze_graham_bargain(symbol, df, info)
            
            if analysis and analysis.get("scenario") == GrahamScenario.DEFENSIVE:
                defensive_score = analysis.get("defensive_score", 0)
                if defensive_score >= min_defensive_score:
                    results.append(analysis)
    
    # Sort by defensive score (higher is better)
    results.sort(key=lambda x: x.get("defensive_score", 0), reverse=True)
    
    return results[:limit]


def scan_deep_value(
    index: str = "NIFTY_500",
    limit: int = 50,
    min_mos: float = 40.0
) -> List[Dict]:
    """
    Scan for Deep Value opportunities
    
    Finds stocks with high margin of safety (≥40%)
    
    Args:
        index: Stock index to scan
        limit: Maximum results
        min_mos: Minimum margin of safety percentage
        
    Returns:
        List of deep value stocks sorted by MOS%
    """
    results = []
    symbols = load_nse_symbols(index)
    symbols = sorted(symbols)
    total_symbols = len(symbols)
    
    clear_expired_cache()
    
    for i in range(0, total_symbols, BATCH_SIZE):
        current_batch = symbols[i : i + BATCH_SIZE]
        stock_data = fetch_stock_batch(current_batch, period="5y")
        
        for symbol in current_batch:
            df, info = safe_get(stock_data, symbol)
            analysis = analyze_graham_bargain(symbol, df, info)
            
            if analysis and analysis.get("scenario") == GrahamScenario.DEEP_VALUE:
                mos_pct = analysis.get("mos_pct", 0)
                if mos_pct >= min_mos:
                    results.append(analysis)
    
    # Sort by MOS% (higher is better)
    results.sort(key=lambda x: x.get("mos_pct", 0), reverse=True)
    
    return results[:limit]


def scan_by_scenario_type(
    scenario_type: str,
    index: str = "NIFTY_500",
    limit: int = 50
) -> List[Dict]:
    """
    Scan for specific Graham scenario type
    
    Args:
        scenario_type: Scenario to scan for (NET_NET, ASSET_PLAY, etc)
        index: Stock index to scan
        limit: Maximum results
        
    Returns:
        List of stocks matching scenario
    """
    # Use specialized scanner if available
    if scenario_type == GrahamScenario.NET_NET:
        return scan_net_nets(index, limit)
    elif scenario_type == GrahamScenario.ASSET_PLAY:
        return scan_asset_plays(index, limit)
    elif scenario_type == GrahamScenario.CIGAR_BUTT:
        return scan_cigar_butts(index, limit)
    elif scenario_type == GrahamScenario.DEFENSIVE:
        return scan_defensive_stocks(index, limit)
    elif scenario_type == GrahamScenario.DEEP_VALUE:
        return scan_deep_value(index, limit)
    else:
        # Generic scan with scenario filter
        return scan_graham_bargains(
            index=index,
            limit=limit,
            scenarios=[scenario_type],
            min_graham_score=40
        )


def get_scenario_summary(results: List[Dict]) -> Dict:
    """
    Get summary statistics for scan results
    
    Args:
        results: List of analysis results
        
    Returns:
        Dictionary with summary stats
    """
    if not results:
        return {}
    
    # Count by scenario
    scenario_counts = {}
    for result in results:
        scenario = result.get("scenario", "UNKNOWN")
        scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
    
    # Calculate averages
    avg_graham_score = sum(r.get("graham_score", 0) for r in results) / len(results)
    avg_mos = sum(r.get("mos_pct", 0) for r in results) / len(results)
    avg_fscore = sum(r.get("fscore", 0) for r in results) / len(results)
    
    # Count strong buys
    strong_buys = sum(1 for r in results if "STRONG BUY" in r.get("recommendation", ""))
    buys = sum(1 for r in results if r.get("recommendation", "").startswith("BUY"))
    
    # Count debt-free companies
    debt_free = sum(1 for r in results if r.get("is_debt_free", False))
    
    return {
        "total_stocks": len(results),
        "scenario_counts": scenario_counts,
        "avg_graham_score": round(avg_graham_score, 1),
        "avg_mos_pct": round(avg_mos, 1),
        "avg_fscore": round(avg_fscore, 1),
        "strong_buy_count": strong_buys,
        "buy_count": buys,
        "debt_free_count": debt_free,
    }
