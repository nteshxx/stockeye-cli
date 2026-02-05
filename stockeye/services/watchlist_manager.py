import json
import os
import asyncio
from pathlib import Path
from typing import List
import threading
from concurrent.futures import ThreadPoolExecutor

from stockeye.config import WATCHLIST_FILE

# In-memory cache
_watchlist_cache: List[str] | None = None
_cache_lock = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=1)
_pending_write = None

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    Path("/app/data").mkdir(parents=True, exist_ok=True)

def _sync_load_from_disk() -> List[str]:
    """Internal function to load from disk synchronously"""
    if not os.path.exists(WATCHLIST_FILE):
        return []
    
    try:
        with open(WATCHLIST_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def _sync_save_to_disk(symbols: List[str]):
    """Internal function to save to disk synchronously"""
    ensure_data_dir()
    
    # Write to temporary file first, then rename for atomicity
    temp_file = WATCHLIST_FILE + ".tmp"
    with open(temp_file, 'w') as f:
        json.dump(symbols, f, indent=2)
    os.replace(temp_file, WATCHLIST_FILE)

def _async_save_to_disk(symbols: List[str]):
    """Asynchronously save to disk without blocking"""
    global _pending_write
    
    # Cancel any pending write
    if _pending_write is not None:
        _pending_write.cancel()
    
    # Schedule new write
    _pending_write = _executor.submit(_sync_save_to_disk, symbols.copy())

def load_watchlist() -> List[str]:
    """Load watchlist from cache or disk"""
    global _watchlist_cache
    
    with _cache_lock:
        if _watchlist_cache is None:
            # First time loading - read from disk
            _watchlist_cache = _sync_load_from_disk()
        
        return _watchlist_cache.copy()

def save_watchlist(symbols: List[str]):
    """Save watchlist to cache and asynchronously to disk"""
    global _watchlist_cache
    
    with _cache_lock:
        _watchlist_cache = symbols.copy()
    
    # Async write to disk (non-blocking)
    _async_save_to_disk(symbols)

def add_symbols(symbols: List[str]) -> List[str]:
    """Add symbols to watchlist"""
    watchlist = load_watchlist()
    
    added = []
    for symbol in symbols:
        symbol = symbol.upper()
        if symbol not in watchlist:
            watchlist.append(symbol)
            added.append(symbol)
    
    if added:
        save_watchlist(watchlist)
    
    return added

def remove_symbols(symbols: List[str]) -> List[str]:
    """Remove symbols from watchlist"""
    watchlist = load_watchlist()
    
    removed = []
    for symbol in symbols:
        symbol = symbol.upper()
        if symbol in watchlist:
            watchlist.remove(symbol)
            removed.append(symbol)
    
    if removed:
        save_watchlist(watchlist)
    
    return removed

def clear_watchlist() -> bool:
    """Clear entire watchlist"""
    save_watchlist([])
    return True

def flush_watchlist():
    """Force immediate write of any pending changes to disk"""
    global _pending_write
    
    if _pending_write is not None:
        _pending_write.result()  # Wait for write to complete
        _pending_write = None

def get_cached_watchlist() -> List[str]:
    """Get watchlist directly from cache without disk access"""
    global _watchlist_cache
    
    with _cache_lock:
        if _watchlist_cache is None:
            return load_watchlist()
        return _watchlist_cache.copy()

# Cleanup on module unload
import atexit
atexit.register(flush_watchlist)
