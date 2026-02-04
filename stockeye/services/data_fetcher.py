import os
import time
import yfinance as yf
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_stock_info(symbol):
    try:
        time.sleep(0.1)
        ticker = yf.Ticker(symbol)
        return symbol, ticker.info
    except Exception:
        return symbol, {}


def fetch_stock_history(symbol, period):
    try:
        ticker = yf.Ticker(symbol)
        return ticker.history(period=period)
    except Exception:
        return pd.DataFrame()


def fetch_stock_history_batch(symbols, period):
    try:
        return yf.download(
            tickers=symbols, 
            period=period, 
            group_by='ticker', 
            threads=True,
            progress=False
        )
    except Exception as e:
            print(f"Batch history download failed: {e}")
            return pd.DataFrame()
        

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
        print(f"Error fetching stock {symbol}: {str(e)}")
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
    max_workers = min((os.cpu_count() or 4) * 2, len(symbols) + 1)
    
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
