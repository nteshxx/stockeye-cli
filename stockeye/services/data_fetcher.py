import yfinance as yf

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
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        info = stock.info
        
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
