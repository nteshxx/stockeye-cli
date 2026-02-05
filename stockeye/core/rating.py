import pandas as pd
from datetime import datetime

from stockeye.utils.utilities import safe_float


def adjust_for_india_vix(rating, vix_value, fscore):
    """
    Adjust rating based on India VIX
    VIX < 15: Low volatility (favorable)
    VIX > 20: High volatility (cautious)
    """
    if vix_value is None:
        return rating
    
    try:
        vix_value = float(vix_value)
        
        # Extreme fear - downgrade aggressive ratings
        if vix_value > 25:
            if rating in ["STRONG BUY 🟢🟢", "BUY 🟢"]:
                return rating + " ⚠️"
        # Low volatility - upgrade quality stocks
        elif vix_value < 12:
            if rating in ["ADD 🔵", "HOLD 🟡"] and fscore >= 6:
                return "BUY 🟢"
    except (ValueError, TypeError):
        pass
    
    return rating


def adjust_for_calendar(rating, fscore):
    """
    Adjust for known calendar effects in Indian market
    """
    current_month = datetime.now().month
    
    # Budget season (Jan-Feb) - higher volatility
    if current_month in [1, 2]:
        if rating in ["STRONG BUY 🟢🟢", "BUY 🟢"] and fscore < 6:
            return "ADD 🔵"
    
    # December - favorable period
    elif current_month == 12:
        if rating == "ADD 🔵" and fscore >= 6:
            return "BUY 🟢"
    
    # March, September - unfavorable
    elif current_month in [3, 9]:
        if rating == "BUY 🟢" and fscore < 7:
            return "ADD 🔵"
    
    return rating


def adjust_for_market_regime(rating, regime, fscore):
    """
    Adjust stock ratings based on overall market condition
    """
    if regime == "BEAR":
        # Be more conservative in bear market
        if rating == "BUY 🟢" and fscore < 7:
            return "HOLD 🟡"
        elif rating == "STRONG BUY 🟢🟢" and fscore < 8:
            return "BUY 🟢"
    elif regime == "BULL":
        # Be more aggressive in bull market
        if rating == "HOLD 🟡" and fscore >= 6:
            return "ADD 🔵"
        elif rating == "ADD 🔵" and fscore >= 7:
            return "BUY 🟢"
    
    return rating


def adjust_for_sector_volatility(rsi_signal, sector_multiplier):
    """
    Adjust RSI thresholds based on sector volatility
    """
    oversold_threshold = 30 * sector_multiplier
    overbought_threshold = 70 / sector_multiplier
    
    return oversold_threshold, overbought_threshold


def rating(price, dma50, dma200, fscore, cross_info, rsi=None, macd_signal=None, volume_signal=None,
          bb_signal=None, supertrend_signal=None, adx_signal=None, vix_value=None, 
          market_regime=None, sector_multiplier=1.0):
    """
    Enhanced trading recommendation with Indian market considerations
    
    New parameters:
        bb_signal: Bollinger Band signal
        supertrend_signal: Supertrend signal
        adx_signal: ADX trend strength
        vix_value: India VIX value
        market_regime: BULL/BEAR/SIDEWAYS
        sector_multiplier: Sector volatility adjustment
    """
    # Null safety for all inputs
    price = safe_float(price)
    dma50 = safe_float(dma50)
    dma200 = safe_float(dma200)
    
    if fscore is None:
        fscore = 0
    try:
        fscore = int(fscore)
    except (ValueError, TypeError):
        fscore = 0
    
    if cross_info is None:
        cross_info = {}
    
    cross_type = cross_info.get('type')
    days_ago = cross_info.get('days_ago')
    
    if days_ago is not None:
        try:
            days_ago = int(days_ago)
        except (ValueError, TypeError):
            days_ago = None
    
    # Calculate enhanced technical score (0-15, increased from 10)
    tech_score = 0
    
    # DMA alignment (0-3 points)
    try:
        if price > 0 and dma50 > 0 and dma200 > 0:
            if price > dma50 > dma200:
                tech_score += 3
            elif price > dma50:
                tech_score += 2
            elif price > dma200:
                tech_score += 1
    except (TypeError, ValueError):
        pass
    
    # RSI scoring (0-2 points) with sector adjustment
    rsi_extreme = None
    rsi_value = safe_float(rsi, None)
    
    if rsi_value is not None:
        try:
            oversold_threshold = 30 * sector_multiplier
            overbought_threshold = 70 / sector_multiplier
            
            neutral_low = max(35, oversold_threshold + 5)
            neutral_high = min(65, overbought_threshold - 5)
            
            if neutral_low <= rsi_value <= neutral_high:
                tech_score += 2
            elif oversold_threshold <= rsi_value < neutral_low:
                tech_score += 1
                rsi_extreme = "oversold"
            elif neutral_high < rsi_value <= overbought_threshold:
                tech_score += 1
            elif rsi_value < oversold_threshold:
                rsi_extreme = "very_oversold"
            elif rsi_value > overbought_threshold:
                rsi_extreme = "very_overbought"
        except (TypeError, ValueError):
            pass
    
    # MACD scoring (0-2 points)
    if macd_signal == "BULLISH":
        tech_score += 2
    elif macd_signal == "NEUTRAL":
        tech_score += 1
    
    # Volume scoring (0-3 points)
    if volume_signal == "HIGH":
        tech_score += 3
    elif volume_signal == "NORMAL":
        tech_score += 2
    elif volume_signal == "LOW":
        tech_score += 1
    
    # Bollinger Bands scoring (0-2 points)
    if bb_signal == "OVERSOLD":
        tech_score += 2  # Near lower band, potential bounce
    elif bb_signal == "NEUTRAL":
        tech_score += 1
    
    # Supertrend scoring (0-2 points)
    if supertrend_signal == "BULLISH":
        tech_score += 2
    elif supertrend_signal == "BEARISH":
        tech_score += 0  # No points for bearish
    
    # ADX scoring (0-1 points) - trend strength confirmation
    if adx_signal == "STRONG_TREND":
        tech_score += 1  # Strong trend confirms the direction
    
    # Calculate combined score with weighted components
    # Fundamental weight: 1.5x, Technical weight: 1.0x
    try:
        combined_score = (fscore * 1.5) + tech_score
    except (TypeError, ValueError):
        combined_score = 0
    
    # === STRONG SELL CONDITIONS ===
    
    # Death cross with confirmation
    if cross_type == "DEATH_CROSS" and days_ago is not None and days_ago <= 15:
        if macd_signal == "BEARISH" or volume_signal == "HIGH":
            return "STRONG SELL 🔴🔴"
        return "SELL 🔴"
    
    # Extreme overbought with bearish signals
    if rsi_extreme == "very_overbought" and macd_signal == "BEARISH" and fscore < 5:
        return "STRONG SELL 🔴🔴"
    
    # Recent death cross (30 days)
    if cross_type == "DEATH_CROSS" and days_ago is not None and days_ago <= 30:
        if combined_score >= 18:  # Override only if exceptionally strong
            return "REDUCE 🟠"
        return "SELL 🔴"
    
    # Supertrend bearish with weak fundamentals
    if supertrend_signal == "BEARISH" and fscore < 4 and macd_signal == "BEARISH":
        return "SELL 🔴"
    
    # === REDUCE CONDITIONS ===
    
    # Overbought with weakening momentum
    if rsi_extreme == "very_overbought":
        if macd_signal == "BEARISH":
            return "SELL 🔴"
        elif macd_signal == "NEUTRAL" or volume_signal == "LOW":
            return "REDUCE 🟠"
    
    # Aging golden cross with deteriorating signals
    if cross_type == "GOLDEN_CROSS" and days_ago is not None and days_ago > 90:
        if macd_signal == "BEARISH" or (rsi_value is not None and rsi_value > 70):
            return "REDUCE 🟠"
    
    # Good fundamentals but technical breakdown
    if fscore >= 6 and tech_score <= 4:
        return "REDUCE 🟠"
    
    # === STRONG BUY CONDITIONS ===
    
    # Fresh golden cross with strong fundamentals and confirmation
    if cross_type == "GOLDEN_CROSS" and days_ago is not None and days_ago <= 10:
        if fscore >= 6 and macd_signal == "BULLISH" and volume_signal == "HIGH":
            if supertrend_signal == "BULLISH":
                return "STRONG BUY 🟢🟢"
            return "BUY 🟢"
        elif fscore >= 5 and macd_signal == "BULLISH":
            return "BUY 🟢"
    
    # Oversold reversal with strong fundamentals
    if rsi_extreme == "very_oversold" and macd_signal == "BULLISH":
        if fscore >= 6 and volume_signal == "HIGH":
            if bb_signal == "OVERSOLD":
                return "STRONG BUY 🟢🟢"
            return "BUY 🟢"
        elif fscore >= 4:
            return "BUY 🟢"
    
    # Exceptional combined score with multiple confirmations
    if combined_score >= 20:  # Very high bar
        if macd_signal == "BULLISH" and volume_signal in ["HIGH", "NORMAL"]:
            if supertrend_signal == "BULLISH" or bb_signal == "OVERSOLD":
                return "STRONG BUY 🟢🟢"
    
    # === BUY CONDITIONS ===
    
    # Golden cross with good confirmation (11-30 days)
    if cross_type == "GOLDEN_CROSS" and days_ago is not None and 11 <= days_ago <= 30:
        if fscore >= 5 and macd_signal == "BULLISH":
            if supertrend_signal == "BULLISH":
                return "BUY 🟢"
            return "ADD 🔵"
        elif fscore >= 4:
            return "ADD 🔵"
    
    # Strong combined score
    if combined_score >= 17:
        if macd_signal != "BEARISH" and supertrend_signal != "BEARISH":
            return "BUY 🟢"
    
    # Good fundamentals with decent technicals
    if fscore >= 7 and tech_score >= 8:
        return "BUY 🟢"
    
    # Multiple bullish indicators
    bullish_count = sum([
        macd_signal == "BULLISH",
        supertrend_signal == "BULLISH",
        bb_signal == "OVERSOLD",
        volume_signal == "HIGH",
        adx_signal == "STRONG_TREND"
    ])
    
    if bullish_count >= 3 and fscore >= 6:
        return "BUY 🟢"
    
    # === ADD CONDITIONS ===
    
    # Moderate dip in strong stock
    if fscore >= 6 and rsi_extreme == "oversold" and price > dma200:
        return "ADD 🔵"
    
    # Older golden cross with solid fundamentals
    if cross_type == "GOLDEN_CROSS" and days_ago is not None and 30 < days_ago <= 60:
        if fscore >= 5 and tech_score >= 6:
            return "ADD 🔵"
    
    # Good combined score
    if combined_score >= 14:
        if macd_signal != "BEARISH" and fscore >= 5:
            return "ADD 🔵"
    
    # === HOLD CONDITIONS ===
    
    # Moderate combined score
    if 11 <= combined_score < 14:
        return "HOLD 🟡"
    
    # Mixed signals with decent fundamentals
    if fscore >= 4 and tech_score >= 5:
        return "HOLD 🟡"
    
    # Old golden cross, weakening but not broken
    if cross_type == "GOLDEN_CROSS" and fscore >= 4:
        return "HOLD 🟡"
    
    # === SELL CONDITIONS ===
    
    # Weak combined score
    if combined_score < 9:
        if macd_signal == "BEARISH" or supertrend_signal == "BEARISH":
            return "SELL 🔴"
    
    # Poor fundamentals with weak technicals
    if fscore < 3 and tech_score < 5:
        return "SELL 🔴"
    
    # Default to sell for very weak signals
    if combined_score < 7:
        return "STRONG SELL 🔴🔴"
    
    # Final fallback
    return "SELL 🔴"


def enhanced_rating(price, dma50, dma200, fscore, cross_info, rsi=None, macd_signal=None, 
                    volume_signal=None, bb_signal=None, supertrend_signal=None, adx_signal=None,
                    vix_value=None, market_regime=None, sector_multiplier=1.0):
    """
    Get rating with all Indian market adjustments applied
    """
    # Get base rating
    base_rating = rating(price, dma50, dma200, fscore, cross_info, rsi, macd_signal, 
                        volume_signal, bb_signal, supertrend_signal, adx_signal, 
                        vix_value, market_regime, sector_multiplier)
    
    # Apply India VIX adjustment
    if vix_value is not None:
        base_rating = adjust_for_india_vix(base_rating, vix_value, fscore)
    
    # Apply calendar adjustment
    base_rating = adjust_for_calendar(base_rating, fscore)
    
    # Apply market regime adjustment
    if market_regime is not None:
        base_rating = adjust_for_market_regime(base_rating, market_regime, fscore)
    
    return base_rating


def get_rating_score(rating_str):
    """Convert rating string to numeric score for sorting"""
    if rating_str is None:
        return 0
    
    # Remove warnings and emojis for matching
    rating_base = rating_str.split(" ⚠️")[0]
    
    rating_scores = {
        "STRONG BUY 🟢🟢": 7,
        "BUY 🟢": 6,
        "ADD 🔵": 5,
        "HOLD 🟡": 4,
        "REDUCE 🟠": 3,
        "SELL 🔴": 2,
        "STRONG SELL 🔴🔴": 1,
    }
    return rating_scores.get(rating_base, 0)


def get_cross_display(cross_info):
    """Format cross information for display with null safety"""
    if cross_info is None:
        return "N/A"
    
    cross_type = cross_info.get('type')
    days_ago = cross_info.get('days_ago')
    
    if cross_type is None:
        return "N/A"
    
    cross_name = cross_type.replace("_", " ").title()
    
    if days_ago is None:
        return f"{cross_name}"
    
    try:
        days_ago = int(days_ago)
        if days_ago == 0:
            return f"{cross_name} today"
        elif days_ago == 1:
            return f"{cross_name} yesterday"
        else:
            return f"{cross_name} {days_ago}d ago"
    except (ValueError, TypeError):
        return f"{cross_name}"
    