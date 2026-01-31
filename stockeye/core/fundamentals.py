def fundamental_score(info):
    """
    Calculate fundamental score with null safety
    
    Args:
        info: Stock info dictionary
        
    Returns:
        int: Fundamental score (0-8)
    """
    if info is None:
        return 0
        
    score = 0
    
    # Return on Equity check
    roe = info.get("returnOnEquity")
    if roe is not None and isinstance(roe, (int, float)) and roe > 0.15:
        score += 2
    
    # Debt to Equity check
    debt_to_equity = info.get("debtToEquity")
    if debt_to_equity is not None and isinstance(debt_to_equity, (int, float)) and debt_to_equity < 1:
        score += 2
    
    # Revenue Growth check
    revenue_growth = info.get("revenueGrowth")
    if revenue_growth is not None and isinstance(revenue_growth, (int, float)) and revenue_growth > 0.1:
        score += 2
    
    # Profit Margins check
    profit_margins = info.get("profitMargins")
    if profit_margins is not None and isinstance(profit_margins, (int, float)) and profit_margins > 0.1:
        score += 2
    
    return score
