import pandas as pd


def safe_float(value, default=0.0):
    """Safely convert value to float with null checking"""
    if value is None or pd.isna(value):
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def rating(price, dma50, dma200, fscore, cross_info, rsi=None, macd_signal=None, volume_signal=None):
    """
    Generate trading recommendation based on technicals and fundamentals with null safety
    
    Args:
        price: Current stock price
        dma50: 50-day moving average
        dma200: 200-day moving average
        fscore: Fundamental score (0-8)
        cross_info: Dict with cross type, days_ago, and cross_price
        rsi: RSI value (0-100)
        macd_signal: MACD signal ('BULLISH' | 'BEARISH' | 'NEUTRAL')
        volume_signal: Volume signal ('HIGH' | 'NORMAL' | 'LOW')
    
    Returns:
        str: Trading recommendation with emoji
        
    Rating Scale:
        STRONG BUY 🟢 - Exceptional entry opportunity
        BUY 🟢 - Good entry point
        ADD 🔵 - Good for adding to existing position
        HOLD 🟡 - Maintain current position
        REDUCE 🟠 - Consider reducing position
        SELL 🔴 - Sell position
        STRONG SELL 🔴 - Urgent sell recommended
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
    
    # Safely convert days_ago to int
    if days_ago is not None:
        try:
            days_ago = int(days_ago)
        except (ValueError, TypeError):
            days_ago = None
    
    # Calculate technical score (0-10)
    tech_score = 0
    
    # DMA alignment (0-3 points) - with null safety
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
    
    # RSI scoring (0-2 points) - with null safety
    rsi_extreme = None
    rsi_value = safe_float(rsi, None)
    
    if rsi_value is not None:
        try:
            if 40 <= rsi_value <= 60:  # Neutral zone - ideal
                tech_score += 2
            elif 30 <= rsi_value < 40:  # Slightly oversold
                tech_score += 1
                rsi_extreme = "oversold"
            elif 60 < rsi_value <= 70:  # Slightly overbought
                tech_score += 1
            elif rsi_value < 30:
                rsi_extreme = "very_oversold"
            elif rsi_value > 70:
                rsi_extreme = "very_overbought"
        except (TypeError, ValueError):
            pass
    
    # MACD scoring (0-2 points)
    if macd_signal == "BULLISH":
        tech_score += 2
    elif macd_signal == "NEUTRAL":
        tech_score += 1
    
    # Volume scoring (0-3 points) - increased weight
    if volume_signal == "HIGH":
        tech_score += 3
    elif volume_signal == "NORMAL":
        tech_score += 2
    elif volume_signal == "LOW":
        tech_score += 1
    
    # Calculate combined score with weighted components
    # Fundamental weight: 1.5x, Technical weight: 1.0x
    try:
        combined_score = (fscore * 1.5) + tech_score
    except (TypeError, ValueError):
        combined_score = 0
    
    # === STRONG SELL CONDITIONS (Highest Priority) ===
    
    # Death cross with confirmation
    if cross_type == "DEATH_CROSS" and days_ago is not None and days_ago <= 15:
        if macd_signal == "BEARISH" or volume_signal == "HIGH":
            return "STRONG SELL 🔴"
        return "SELL 🔴"
    
    # Extreme overbought with bearish signals
    if rsi_extreme == "very_overbought" and macd_signal == "BEARISH" and fscore < 5:
        return "STRONG SELL 🔴"
    
    # Recent death cross (30 days) - still bearish
    if cross_type == "DEATH_CROSS" and days_ago is not None and days_ago <= 30:
        if combined_score >= 14:  # Override only if exceptionally strong
            return "REDUCE 🟠"
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
    if fscore >= 6 and tech_score <= 3:
        return "REDUCE 🟠"
    
    # === STRONG BUY CONDITIONS ===
    
    # Fresh golden cross with strong fundamentals and confirmation
    if cross_type == "GOLDEN_CROSS" and days_ago is not None and days_ago <= 10:
        if fscore >= 6 and macd_signal == "BULLISH" and volume_signal == "HIGH":
            return "STRONG BUY 🟢"
        elif fscore >= 5 and macd_signal == "BULLISH":
            return "BUY 🟢"
    
    # Oversold reversal with strong fundamentals
    if rsi_extreme == "very_oversold" and macd_signal == "BULLISH":
        if fscore >= 6 and volume_signal == "HIGH":
            return "STRONG BUY 🟢"
        elif fscore >= 4:
            return "BUY 🟢"
    
    # Exceptional combined score
    if combined_score >= 18:  # Very high bar for strong buy
        if macd_signal == "BULLISH" and volume_signal in ["HIGH", "NORMAL"]:
            return "STRONG BUY 🟢"
    
    # === BUY CONDITIONS ===
    
    # Golden cross with good confirmation (11-30 days)
    if cross_type == "GOLDEN_CROSS" and days_ago is not None and 11 <= days_ago <= 30:
        if fscore >= 5 and macd_signal == "BULLISH":
            return "BUY 🟢"
        elif fscore >= 4:
            return "ADD 🔵"
    
    # Strong combined score
    if combined_score >= 15:
        if macd_signal != "BEARISH":
            return "BUY 🟢"
    
    # Good fundamentals with decent technicals
    if fscore >= 7 and tech_score >= 6:
        return "BUY 🟢"
    
    # === ADD CONDITIONS (Good for existing positions) ===
    
    # Moderate dip in strong stock
    if fscore >= 6 and rsi_extreme == "oversold" and price > dma200:
        return "ADD 🔵"
    
    # Older golden cross with solid fundamentals
    if cross_type == "GOLDEN_CROSS" and days_ago is not None and 30 < days_ago <= 60:
        if fscore >= 5 and tech_score >= 5:
            return "ADD 🔵"
    
    # Good combined score but not exceptional
    if combined_score >= 13:
        if macd_signal != "BEARISH" and fscore >= 5:
            return "ADD 🔵"
    
    # === HOLD CONDITIONS ===
    
    # Moderate combined score
    if 10 <= combined_score < 13:
        return "HOLD 🟡"
    
    # Mixed signals with decent fundamentals
    if fscore >= 4 and tech_score >= 4:
        return "HOLD 🟡"
    
    # Old golden cross, weakening but not broken
    if cross_type == "GOLDEN_CROSS" and fscore >= 4:
        return "HOLD 🟡"
    
    # === SELL CONDITIONS ===
    
    # Weak combined score
    if combined_score < 8:
        if macd_signal == "BEARISH":
            return "SELL 🔴"
    
    # Poor fundamentals with weak technicals
    if fscore < 3 and tech_score < 4:
        return "SELL 🔴"
    
    # Default to sell for very weak signals
    if combined_score < 6:
        return "STRONG SELL 🔴"
    
    # Final fallback
    return "SELL 🔴"


def get_rating_score(rating_str):
    """
    Convert rating string to numeric score for sorting with null safety
    Higher score = More bullish
    """
    if rating_str is None:
        return 0
    
    rating_scores = {
        "STRONG BUY 🟢🟢": 7,
        "BUY 🟢": 6,
        "ADD 🔵": 5,
        "HOLD 🟡": 4,
        "REDUCE 🟠": 3,
        "SELL 🔴": 2,
        "STRONG SELL 🔴🔴": 1
    }
    return rating_scores.get(rating_str, 0)


def get_cross_display(cross_info):
    """
    Format cross information for display with null safety
    
    Returns:
        str: Human-readable cross information
    """
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
