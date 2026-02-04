from stockeye.config import PERIOD, DMA_SHORT, DMA_LONG
from stockeye.services.data_fetcher import fetch_stock
from stockeye.core.fundamentals import fundamental_score, get_sector_from_industry
from stockeye.core.rating import get_rating_score, rating
from stockeye.core.indicators import (
    add_dma, add_rsi, add_macd, analyze_volume,
    add_bollinger_bands, add_supertrend, add_adx,
    detect_cross_age, cross_signal,
    get_rsi_signal, get_macd_signal, get_volume_signal,
    get_bollinger_signal, get_supertrend_signal, get_adx_signal,
    fetch_india_vix, detect_market_regime
)
from stockeye.utils.utilities import safe_float, safe_get, safe_int

    
def analyze_stock(symbol, period="1y", vix_value=None, market_regime=None):
    """
    Analyze a single stock with enhanced indicators
    """
    try:
        df, info = fetch_stock(symbol, period)
        
        if df is None or info is None or len(df) < 50:
            return None
        
        # Add all indicators
        df = add_dma(df, 50, 200)
        df = add_rsi(df)
        df = add_macd(df)
        df = analyze_volume(df)
        df = add_bollinger_bands(df)
        df = add_supertrend(df)
        df = add_adx(df)
        
        if df is None or df.empty:
            return None
        
        last = df.iloc[-1]
        fscore = fundamental_score(info) # 0-12 scale
        
        # Extract Signals
        rsi = safe_get(last, "RSI")
        rsi_signal = get_rsi_signal(rsi)
        
        macd_val = safe_get(last, "MACD")
        macd_sig = safe_get(last, "MACD_Signal")
        macd_hist = safe_get(last, "MACD_Hist")
        macd_signal = get_macd_signal(macd_val, macd_sig, macd_hist)
        
        volume_ratio = safe_get(last, "Volume_Ratio")
        volume_signal = get_volume_signal(volume_ratio)

        bb_pos = safe_get(last, "BB_Position")
        bb_signal = get_bollinger_signal(bb_pos)

        st_val = safe_get(last, "Supertrend")
        st_dir = safe_get(last, "Supertrend_Direction")
        st_signal = get_supertrend_signal(safe_get(last, "Close"), st_val, st_dir)

        adx_val = safe_get(last, "ADX")
        adx_signal = get_adx_signal(adx_val)
        
        # Detect cross
        cross_info = detect_cross_age(df)
        if cross_info is None:
            cross_info = {'type': None, 'days_ago': None, 'cross_price': None}
        
        close_price = safe_float(safe_get(last, "Close"))
        dma50_val = safe_float(safe_get(last, "DMA50"))
        dma200_val = safe_float(safe_get(last, "DMA200"))
        
        # Fetch context if not provided (rarely used in loops to save time)
        if vix_value is None:
            vix_value = fetch_india_vix()

        # Generate enhanced rating
        stock_rating = rating(
            close_price, dma50_val, dma200_val, fscore, cross_info,
            rsi, macd_signal, volume_signal, bb_signal, st_signal, adx_signal,
            vix_value, market_regime
        )
        
        return {
            "symbol": symbol,
            "price": close_price,
            "dma50": dma50_val,
            "dma200": dma200_val,
            "rsi": rsi,
            "rsi_signal": rsi_signal,
            "macd_signal": macd_signal,
            "volume_signal": volume_signal,
            "bb_signal": bb_signal,
            "supertrend_signal": st_signal,
            "adx_signal": adx_signal,
            "fscore": fscore,
            "cross_info": cross_info,
            "rating": stock_rating,
            "rating_score": get_rating_score(stock_rating),
            "market_cap": safe_int(info.get("marketCap", 0)),
            "company_name": info.get("longName", symbol)
        }
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {str(e)}")
        return {"sym": symbol, "error": str(e)}
