def fundamental_score(info):
    score = 0
    if info.get("returnOnEquity", 0) and info["returnOnEquity"] > 0.15:
        score += 2
    if info.get("debtToEquity", 2) < 1:
        score += 2
    if info.get("revenueGrowth", 0) > 0.1:
        score += 2
    if info.get("profitMargins", 0) > 0.1:
        score += 2
    return score
