from stockeye.config import PERIOD, DMA_SHORT, DMA_LONG
from stockeye.services.data_fetcher import fetch_stock
from stockeye.core.fundamentals import fundamental_score
from stockeye.core.rating import rating
from stockeye.core.indicators import (
    add_dma, add_rsi, add_macd, analyze_volume,
    detect_cross_age, cross_signal,
    get_rsi_signal, get_macd_signal, get_volume_signal
)

def analyze_symbol(sym):
    """Worker function to process a single symbol"""
    try:
        # Fetch data
        df, info = fetch_stock(sym, PERIOD)
        
        # Add all indicators
        df = add_dma(df, DMA_SHORT, DMA_LONG)
        df = add_rsi(df)
        df = add_macd(df)
        df = analyze_volume(df)
        
        last = df.iloc[-1]
        fscore = fundamental_score(info)
        
        # Get indicator signals
        rsi = last.get("RSI")
        rsi_signal = get_rsi_signal(rsi)
        
        macd_val = last.get("MACD")
        macd_sig = last.get("MACD_Signal")
        macd_hist = last.get("MACD_Hist")
        macd_signal = get_macd_signal(macd_val, macd_sig, macd_hist)
        
        volume_ratio = last.get("Volume_Ratio")
        volume_signal = get_volume_signal(volume_ratio)
        
        # Detect cross and calculate age
        cross_info = detect_cross_age(df)
        
        # Check for immediate cross
        immediate_cross = cross_signal(df)
        if immediate_cross:
            cross_info['type'] = immediate_cross
            cross_info['days_ago'] = 0
        
        # Generate rating
        decision = rating(
            last["Close"], 
            last["DMA50"], 
            last["DMA200"], 
            fscore, 
            cross_info,
            rsi,
            macd_signal,
            volume_signal
        )
        
        # Return a dictionary of results for the table
        return {
            "sym": sym,
            "close": last["Close"],
            "dma50": last["DMA50"],
            "dma200": last["DMA200"],
            "rsi": rsi,
            "rsi_signal": rsi_signal,
            "macd_signal": macd_signal,
            "volume_signal": volume_signal,
            "fscore": fscore,
            "cross_info": cross_info,
            "decision": decision,
            "error": None
        }
    except Exception as e:
        return {"sym": sym, "error": str(e)}
    
