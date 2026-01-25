import yfinance as yf

def fetch_stock(symbol, period):
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)
    info = stock.info
    return df, info
