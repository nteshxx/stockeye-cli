import os
import random
import yfinance as yf
import pandas as pd
import time
import pickle
from pathlib import Path
from typing import Dict, Tuple, Optional
import threading

from concurrent.futures import ThreadPoolExecutor, as_completed

CACHE_DIR = Path("/app/data/cache")
INFO_CACHE_DURATION = 300  # 5 minutes for stock info
HISTORY_CACHE_DURATION = 60  # 1 minute for historical data

# In-memory caches
_info_cache: Dict[str, Tuple[float, dict]] = {}
_history_cache: Dict[Tuple[str, str], Tuple[float, pd.DataFrame]] = {}
_batch_history_cache: Dict[Tuple[tuple, str], Tuple[float, pd.DataFrame]] = {}
_cache_lock = threading.Lock()

def ensure_cache_dir():
    """Create cache directory if it doesn't exist"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _is_cache_valid(timestamp: float, duration: int) -> bool:
    """Check if cache entry is still valid"""
    return time.time() - timestamp < duration

def _load_disk_cache(cache_file: Path) -> dict:
    """Load cache from disk"""
    if cache_file.exists():
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return {}
    return {}

def _save_disk_cache(cache_file: Path, data: dict):
    """Save cache to disk asynchronously"""
    ensure_cache_dir()
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Failed to save cache: {e}")

def fetch_stock_info(symbol: str, use_cache: bool = True) -> Tuple[str, dict]:
    """
    Fetch stock info with caching
    
    Args:
        symbol: Stock ticker symbol
        use_cache: Whether to use cached data (default: True)
    
    Returns:
        Tuple of (symbol, info_dict)
    """
    global _info_cache
    
    with _cache_lock:
        # Check in-memory cache
        if use_cache and symbol in _info_cache:
            timestamp, info = _info_cache[symbol]
            if _is_cache_valid(timestamp, INFO_CACHE_DURATION):
                return symbol, info
    
    time.sleep(random.uniform(0.2, 1))
    # Fetch from API
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Update cache
        with _cache_lock:
            _info_cache[symbol] = (time.time(), info)
        
        return symbol, info
    except Exception as e:
        print(f"Failed to fetch info for {symbol}: {e}")
        return symbol, {}

def fetch_stock_history(symbol: str, period: str, use_cache: bool = True) -> pd.DataFrame:
    """
    Fetch stock history with caching
    
    Args:
        symbol: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        use_cache: Whether to use cached data (default: True)
    
    Returns:
        DataFrame with historical data
    """
    global _history_cache
    
    cache_key = (symbol, period)
    
    with _cache_lock:
        # Check in-memory cache
        if use_cache and cache_key in _history_cache:
            timestamp, hist = _history_cache[cache_key]
            if _is_cache_valid(timestamp, HISTORY_CACHE_DURATION):
                return hist.copy()
    
    # Fetch from API
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        # Update cache
        with _cache_lock:
            _history_cache[cache_key] = (time.time(), hist)
        
        return hist
    except Exception as e:
        print(f"Failed to fetch history for {symbol}: {e}")
        return pd.DataFrame()

def fetch_stock_history_batch(symbols: list, period: str, use_cache: bool = True) -> pd.DataFrame:
    """
    Fetch batch stock history with caching
    
    Args:
        symbols: List of stock ticker symbols
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        use_cache: Whether to use cached data (default: True)
    
    Returns:
        DataFrame with historical data for all symbols
    """
    global _batch_history_cache
    
    cache_key = (tuple(sorted(symbols)), period)
    
    with _cache_lock:
        # Check in-memory cache
        if use_cache and cache_key in _batch_history_cache:
            timestamp, hist = _batch_history_cache[cache_key]
            if _is_cache_valid(timestamp, HISTORY_CACHE_DURATION):
                return hist.copy()
    
    # Fetch from API
    try:
        data = yf.download(
            tickers=symbols, 
            period=period, 
            group_by='ticker', 
            threads=True,
            progress=False
        )
        
        # Update cache
        with _cache_lock:
            _batch_history_cache[cache_key] = (time.time(), data)
        
        return data
    except Exception as e:
        print(f"Batch history download failed: {e}")
        return pd.DataFrame()

def clear_cache():
    """Clear all in-memory caches"""
    global _info_cache, _history_cache, _batch_history_cache
    
    with _cache_lock:
        _info_cache.clear()
        _history_cache.clear()
        _batch_history_cache.clear()

def clear_expired_cache():
    """Remove expired entries from cache"""
    global _info_cache, _history_cache, _batch_history_cache
    
    current_time = time.time()
    
    with _cache_lock:
        # Clear expired info cache
        _info_cache = {
            k: v for k, v in _info_cache.items()
            if _is_cache_valid(v[0], INFO_CACHE_DURATION)
        }
        
        # Clear expired history cache
        _history_cache = {
            k: v for k, v in _history_cache.items()
            if _is_cache_valid(v[0], HISTORY_CACHE_DURATION)
        }
        
        # Clear expired batch history cache
        _batch_history_cache = {
            k: v for k, v in _batch_history_cache.items()
            if _is_cache_valid(v[0], HISTORY_CACHE_DURATION)
        }

def get_cache_stats() -> dict:
    """Get cache statistics"""
    with _cache_lock:
        return {
            'info_cache_size': len(_info_cache),
            'history_cache_size': len(_history_cache),
            'batch_history_cache_size': len(_batch_history_cache),
            'info_cache_duration': INFO_CACHE_DURATION,
            'history_cache_duration': HISTORY_CACHE_DURATION
        }

def save_cache_to_disk():
    """Persist all caches to disk"""
    ensure_cache_dir()
    
    with _cache_lock:
        _save_disk_cache(CACHE_DIR / "info_cache.pkl", _info_cache)
        _save_disk_cache(CACHE_DIR / "history_cache.pkl", _history_cache)
        _save_disk_cache(CACHE_DIR / "batch_history_cache.pkl", _batch_history_cache)

def load_cache_from_disk():
    """Load caches from disk"""
    global _info_cache, _history_cache, _batch_history_cache
    
    with _cache_lock:
        _info_cache = _load_disk_cache(CACHE_DIR / "info_cache.pkl")
        _history_cache = _load_disk_cache(CACHE_DIR / "history_cache.pkl")
        _batch_history_cache = _load_disk_cache(CACHE_DIR / "batch_history_cache.pkl")
    
    # Clean up expired entries
    clear_expired_cache()

# Auto-save cache on exit
import atexit
atexit.register(save_cache_to_disk)

# Load cache on import
try:
    load_cache_from_disk()
except Exception:
    pass      

def fetch_stock(symbol, period):
    """
    Fetch stock data with null safety
    
    Args:
        symbol: Stock symbol
        period: Time period for historical data
        
    Returns:
        tuple: (DataFrame, info_dict) or (None, None) on error
    """
    try:
        df = fetch_stock_history(symbol, period)
        sym, info = fetch_stock_info(symbol)

        # Validate DataFrame
        if df is None or df.empty or len(df) == 0:
            return None, None
            
        # Validate info
        if info is None:
            info = {}
            
        return df, info
    except Exception as e:
        print(f"[bold red]Error[/bold red] analyzing {symbol}: {e}")
        return None, None


def fetch_stock_batch(symbols, period):
    """
    Fetches price history and metadata simultaneously using parallel execution.
    
    Args:
        symbols (list): List of stock symbols (e.g., ['AAPL', 'MSFT'])
        period (str): Time period (e.g., '1y', '1mo')
        
    Returns:
        dict: {symbol: (DataFrame, info_dict)}
    """
    results = {}
    info_data = {}
    history_data = pd.DataFrame()

    # Calculate optimal thread count
    # We need enough threads to handle the info requests while download runs
    max_workers = min((os.cpu_count() or 4), len(symbols) + 1)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # --- PHASE 1: SUBMIT ALL TASKS ---
        
        # Submit the heavy bulk history download as one task
        future_history = executor.submit(fetch_stock_history_batch, symbols, period)
        
        # Submit individual info fetch tasks
        future_to_symbol = {
            executor.submit(fetch_stock_info, sym): sym 
            for sym in symbols
        }

        # --- PHASE 2: GATHER RESULTS AS THEY ARRIVE ---
        
        # Collect Info (Metadata)
        for future in as_completed(future_to_symbol):
            sym, info = future.result()
            if info:
                info_data[sym] = info
        
        # Collect History (Wait for the bulk download to finish)
        try:
            history_data = future_history.result()
        except Exception as e:
            print(f"Error retrieving history result: {e}")

    # --- PHASE 3: MERGE DATA ---

    for symbol in symbols:
        try:
            # Extract DataFrame for this specific symbol
            if history_data.empty:
                df = pd.DataFrame()
            else:
                try:
                    df = history_data if len(symbols) == 1 else history_data[symbol]
                except KeyError:
                    df = pd.DataFrame() # Symbol failed to download

            # Skip if no data found
            if df.empty and symbol not in info_data:
                continue

            # Get the info we fetched earlier (default to empty dict)
            info = info_data.get(symbol, {})

            results[symbol] = (df, info)
            
        except Exception as e:
            print(f"Error merging data for {symbol}: {e}")
            continue

    return results
