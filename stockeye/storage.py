import json
import os
from pathlib import Path

WATCHLIST_FILE = "/app/data/watchlist.json"

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    Path("data").mkdir(exist_ok=True)

def load_watchlist():
    """Load watchlist from JSON file"""
    ensure_data_dir()
    
    if not os.path.exists(WATCHLIST_FILE):
        return []
    
    try:
        with open(WATCHLIST_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_watchlist(symbols):
    """Save watchlist to JSON file"""
    ensure_data_dir()
    
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(symbols, f, indent=2)

def add_symbols(symbols):
    """Add symbols to watchlist"""
    watchlist = load_watchlist()
    
    added = []
    for symbol in symbols:
        symbol = symbol.upper()
        if symbol not in watchlist:
            watchlist.append(symbol)
            added.append(symbol)
    
    save_watchlist(watchlist)
    return added

def remove_symbols(symbols):
    """Remove symbols from watchlist"""
    watchlist = load_watchlist()
    
    removed = []
    for symbol in symbols:
        symbol = symbol.upper()
        if symbol in watchlist:
            watchlist.remove(symbol)
            removed.append(symbol)
    
    save_watchlist(watchlist)
    return removed

def clear_watchlist():
    """Clear entire watchlist"""
    save_watchlist([])
    return True
