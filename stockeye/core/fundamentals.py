def fundamental_score(info):
    """
    Enhanced fundamental score for Indian stocks
    Includes promoter holding, P/B ratio, dividend yield, operating margins
    
    Returns: Score out of 12 points
    """
    if info is None:
        return 0
    
    score = 0
    
    # Core metrics (8 points)
    roe = info.get("returnOnEquity")
    if roe is not None and isinstance(roe, (int, float)) and roe > 0.15:
        score += 2
    
    debt_to_equity = info.get("debtToEquity")
    if debt_to_equity is not None and isinstance(debt_to_equity, (int, float)) and debt_to_equity < 1:
        score += 2
    
    revenue_growth = info.get("revenueGrowth")
    if revenue_growth is not None and isinstance(revenue_growth, (int, float)) and revenue_growth > 0.1:
        score += 2
    
    profit_margins = info.get("profitMargins")
    if profit_margins is not None and isinstance(profit_margins, (int, float)) and profit_margins > 0.1:
        score += 2
    
    # Indian-specific additions (4 points)
    
    # Promoter holding (should be stable, 40-70% is good)
    promoter_holding = info.get("heldPercentInsiders", 0) * 100
    if promoter_holding is not None and isinstance(promoter_holding, (int, float)):
        if 40 <= promoter_holding <= 70:
            score += 1
    
    # Price to Book ratio (< 3 is good for Indian stocks)
    pb_ratio = info.get("priceToBook", 999)
    if pb_ratio is not None and isinstance(pb_ratio, (int, float)) and pb_ratio < 3 and pb_ratio > 0:
        score += 1
    
    # Dividend yield (> 1% is good)
    dividend_yield = info.get("dividendYield", 0)
    if dividend_yield is not None and isinstance(dividend_yield, (int, float)):
        dividend_yield_pct = dividend_yield * 100
        if dividend_yield_pct > 1:
            score += 1
    
    # Operating margin (> 15% is excellent)
    operating_margin = info.get("operatingMargins", 0)
    if operating_margin is not None and isinstance(operating_margin, (int, float)) and operating_margin > 0.15:
        score += 1
    
    return min(score, 12)


def get_sector_from_industry(industry: str) -> str:
    """
    Map Yahoo Finance 'industry' string to a custom broad sector bucket.
    Prioritizes keywords to map distinct sub-industries (e.g., 'Credit Services')
    to broader groups (e.g., 'BANKING').
    """
    if not industry or not isinstance(industry, str):
        return "UNKNOWN"
    
    # Normalize for easier matching
    ind = industry.upper().strip()
    
    # Configuration: Define your buckets and their trigger keywords here.
    # ORDER MATTERS: Put more specific/likely matches earlier if there is overlap risk.
    sector_keywords = {
        "BANKING": [
            "BANK", "FINANCE", "INSURANCE", "NBFC", "CREDIT", 
            "CAPITAL", "ASSET", "BROKER", "WEALTH", "MORTGAGE"
        ],
        "IT": [
            "SOFTWARE", "TECHNOLOGY", "COMPUTER", "IT ", "DATA", 
            "INTERNET", "SEMICONDUCTOR", "ELECTRONICS", "DIGITAL", "CHIP"
        ],
        "PHARMA": [
            "PHARMA", "DRUG", "HEALTH", "BIOTECH", "MEDICAL", "LIFE SCIENCE"
        ],
        "AUTO": [
            "AUTO", "VEHICLE", "MOTOR", "TRUCK", "TIRES"
        ],
        "FMCG": [
            "CONSUMER", "FMCG", "FOOD", "BEVERAGE", "TOBACCO", 
            "HOUSEHOLD", "PERSONAL", "GROCERY"
        ],
        "METALS": [
            "METAL", "STEEL", "MINING", "ALUMINUM", "COPPER", 
            "ZINC", "GOLD", "SILVER", "MATERIALS"
        ],
        "ENERGY": [
            "POWER", "ENERGY", "OIL", "GAS", "COAL", 
            "PETROLEUM", "SOLAR", "RENEWABLE", "UTILITIES"
        ],
        "REALTY": [
            "REAL ESTATE", "REALTY", "CONSTRUCTION", "REIT", 
            "INFRASTRUCTURE", "DEVELOPMENT"
        ],
        "TELECOM": [
            "TELECOM", "COMMUNICATION", "WIRELESS"
        ]
    }

    # Iterate through the config to find the first match
    for sector, keywords in sector_keywords.items():
        if any(k in ind for k in keywords):
            return sector
            
    # Fallback for unmapped industries (e.g. "Aerospace", "Textile")
    return "OTHER"


SECTOR_VOLATILITY_ADJUSTMENT = {
    "BANKING": 1.2,     # Higher volatility
    "IT": 0.9,          # Lower volatility
    "PHARMA": 1.1,
    "FMCG": 0.8,        # Most stable
    "METALS": 1.4,      # High commodity dependency
    "AUTO": 1.3,
    "REALTY": 1.5,      # Highest volatility
    "ENERGY": 1.2,
    "TELECOM": 1.1,
    "OTHER": 1.0
}


def get_sector_volatility_multiplier(sector):
    """
    Get volatility multiplier for sector
    """
    return SECTOR_VOLATILITY_ADJUSTMENT.get(sector, 1.0)


def get_quality_score(info):
    """
    Calculate quality score based on stability metrics
    Returns: Score out of 10
    """
    if info is None:
        return 0
    
    score = 0
    
    # Consistent earnings (low beta preferred)
    beta = info.get("beta")
    if beta is not None and isinstance(beta, (int, float)):
        if 0.8 <= beta <= 1.2:
            score += 2  # Market-like volatility
        elif beta < 0.8:
            score += 3  # Low volatility (defensive)
    
    # Strong balance sheet (current ratio > 1.5)
    current_ratio = info.get("currentRatio")
    if current_ratio is not None and isinstance(current_ratio, (int, float)) and current_ratio > 1.5:
        score += 2
    
    # Good cash position (quick ratio > 1)
    quick_ratio = info.get("quickRatio")
    if quick_ratio is not None and isinstance(quick_ratio, (int, float)) and quick_ratio > 1:
        score += 2
    
    # Profitability (EBITDA margins > 15%)
    ebitda_margins = info.get("ebitdaMargins")
    if ebitda_margins is not None and isinstance(ebitda_margins, (int, float)) and ebitda_margins > 0.15:
        score += 2
    
    # Earnings consistency (forward P/E reasonable)
    forward_pe = info.get("forwardPE")
    trailing_pe = info.get("trailingPE")
    if forward_pe and trailing_pe:
        if isinstance(forward_pe, (int, float)) and isinstance(trailing_pe, (int, float)):
            if 10 <= forward_pe <= 25 and 10 <= trailing_pe <= 30:
                score += 2
    
    return min(score, 10)


def get_growth_score(info):
    """
    Calculate growth score
    Returns: Score out of 10
    """
    if info is None:
        return 0
    
    score = 0
    
    # Revenue growth (> 15% excellent)
    revenue_growth = info.get("revenueGrowth")
    if revenue_growth is not None and isinstance(revenue_growth, (int, float)):
        if revenue_growth > 0.20:
            score += 3
        elif revenue_growth > 0.15:
            score += 2
        elif revenue_growth > 0.10:
            score += 1
    
    # Earnings growth
    earnings_growth = info.get("earningsGrowth")
    if earnings_growth is not None and isinstance(earnings_growth, (int, float)):
        if earnings_growth > 0.20:
            score += 3
        elif earnings_growth > 0.15:
            score += 2
        elif earnings_growth > 0.10:
            score += 1
    
    # Book value growth
    book_value = info.get("bookValue")
    price_to_book = info.get("priceToBook")
    if book_value and price_to_book:
        if isinstance(book_value, (int, float)) and isinstance(price_to_book, (int, float)):
            if price_to_book > 0 and book_value > 0:
                # Growing book value is good
                score += 2
    
    # Return on Assets (> 10% is good growth indicator)
    roa = info.get("returnOnAssets")
    if roa is not None and isinstance(roa, (int, float)) and roa > 0.10:
        score += 2
    
    return min(score, 10)


def get_value_score(info):
    """
    Calculate value score based on valuation metrics
    Returns: Score out of 10
    """
    if info is None:
        return 0
    
    score = 0
    
    # P/E ratio (< 20 is good for value)
    trailing_pe = info.get("trailingPE")
    if trailing_pe is not None and isinstance(trailing_pe, (int, float)):
        if 0 < trailing_pe < 15:
            score += 3
        elif 15 <= trailing_pe < 20:
            score += 2
        elif 20 <= trailing_pe < 25:
            score += 1
    
    # P/B ratio (< 2 is good)
    pb_ratio = info.get("priceToBook")
    if pb_ratio is not None and isinstance(pb_ratio, (int, float)):
        if 0 < pb_ratio < 1.5:
            score += 3
        elif 1.5 <= pb_ratio < 2.5:
            score += 2
        elif 2.5 <= pb_ratio < 3.5:
            score += 1
    
    # Dividend yield (> 2% is good)
    dividend_yield = info.get("dividendYield")
    if dividend_yield is not None and isinstance(dividend_yield, (int, float)):
        div_pct = dividend_yield * 100
        if div_pct > 3:
            score += 2
        elif div_pct > 2:
            score += 1
    
    # PEG ratio (< 1 is undervalued)
    peg_ratio = info.get("pegRatio")
    if peg_ratio is not None and isinstance(peg_ratio, (int, float)):
        if 0 < peg_ratio < 1:
            score += 2
        elif 1 <= peg_ratio < 1.5:
            score += 1
    
    return min(score, 10)

