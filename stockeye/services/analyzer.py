from stockeye.config import PERIOD, DMA_SHORT, DMA_LONG
from stockeye.services.data_fetcher import fetch_stock
from stockeye.core.fundamentals import fundamental_score, get_sector_from_industry
from stockeye.core.rating import rating
from stockeye.core.indicators import (
    add_dma, add_rsi, add_macd, analyze_volume,
    add_bollinger_bands, add_supertrend, add_adx,
    detect_cross_age, cross_signal,
    get_rsi_signal, get_macd_signal, get_volume_signal,
    get_bollinger_signal, get_supertrend_signal, get_adx_signal,
    fetch_india_vix, detect_market_regime
)

def analyze_symbol(sym, vix_value=None, market_regime=None):
    """
    Worker function to process a single symbol with sector and enhanced signals
    """
    try:
        # Fetch data
        df, info = fetch_stock(sym, PERIOD)
        
        if df is None or df.empty:
            return {"sym": sym, "error": "No data found"}
        
        # Add all indicators
        df = add_dma(df, DMA_SHORT, DMA_LONG)
        df = add_rsi(df)
        df = add_macd(df)
        df = analyze_volume(df)
        df = add_bollinger_bands(df)
        df = add_supertrend(df)
        df = add_adx(df)
        
        last = df.iloc[-1]
        
        # Fundamentals & Sector
        fscore = fundamental_score(info)
        industry = info.get("industry")
        sector = get_sector_from_industry(industry)
        
        # Get indicator signals
        rsi = last.get("RSI")
        rsi_signal = get_rsi_signal(rsi)
        
        macd_val = last.get("MACD")
        macd_sig = last.get("MACD_Signal")
        macd_hist = last.get("MACD_Hist")
        macd_signal = get_macd_signal(macd_val, macd_sig, macd_hist)
        
        volume_ratio = last.get("Volume_Ratio")
        volume_signal = get_volume_signal(volume_ratio)
        
        # New Signals
        bb_pos = last.get("BB_Position")
        bb_signal = get_bollinger_signal(bb_pos)
        
        st_val = last.get("Supertrend")
        st_dir = last.get("Supertrend_Direction")
        st_signal = get_supertrend_signal(last["Close"], st_val, st_dir)
        
        adx_val = last.get("ADX")
        adx_signal = get_adx_signal(adx_val)
        
        # Detect cross
        cross_info = detect_cross_age(df)
        immediate_cross = cross_signal(df)
        if immediate_cross:
            cross_info['type'] = immediate_cross
            cross_info['days_ago'] = 0
            
        # Context fallbacks
        if vix_value is None:
            vix_value = fetch_india_vix()
            
        # Generate enhanced rating
        decision = rating(
            price=last["Close"], 
            dma50=last["DMA50"], 
            dma200=last["DMA200"], 
            fscore=fscore, 
            cross_info=cross_info,
            rsi=rsi,
            macd_signal=macd_signal,
            volume_signal=volume_signal,
            bb_signal=bb_signal,
            supertrend_signal=st_signal,
            adx_signal=adx_signal,
            vix_value=vix_value,
            market_regime=market_regime
        )
        
        return {
            "sym": sym,
            "sector": sector, # Added Sector
            "close": last["Close"],
            "dma50": last["DMA50"],
            "dma200": last["DMA200"],
            "rsi": rsi,
            "rsi_signal": rsi_signal,
            "macd_signal": macd_signal,
            "volume_signal": volume_signal,
            "bb_signal": bb_signal,
            "supertrend_signal": st_signal,
            "adx_signal": adx_signal,
            "fscore": fscore,
            "cross_info": cross_info,
            "decision": decision,
            "error": None
        }
    except Exception as e:
        return {"sym": sym, "error": str(e)}
    