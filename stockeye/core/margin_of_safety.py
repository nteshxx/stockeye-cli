"""
Margin of Safety Calculator - Benjamin Graham Style Value Investing

Calculates intrinsic value based on:
- Historical EPS (Earnings Per Share)
- Growth rate
- Graham's formula for valuation
"""
import pandas as pd
import numpy as np


def calculate_growth(eps_series, method="cagr"):
    """
    Calculate growth rate from EPS history
    
    Args:
        eps_series: Pandas Series of historical EPS values
        method: "cagr" (Compound Annual Growth Rate) or "average"
    
    Returns:
        float: Growth rate as percentage
    """
    if len(eps_series) < 2:
        return 0.0
    
    # Remove any NaN or negative values
    clean_eps = eps_series.dropna()
    clean_eps = clean_eps[clean_eps > 0]
    
    if len(clean_eps) < 2:
        return 0.0
    
    if method == "cagr":
        # CAGR = (Ending Value / Beginning Value)^(1/n) - 1
        start_eps = clean_eps.iloc[0]
        end_eps = clean_eps.iloc[-1]
        n_years = len(clean_eps) - 1
        
        if start_eps <= 0:
            return 0.0
        
        try:
            cagr = (pow(end_eps / start_eps, 1/n_years) - 1) * 100
            # Cap growth rate at reasonable levels (-50% to 100%)
            return max(-50, min(100, cagr))
        except:
            return 0.0
    
    else:  # average growth
        # Calculate year-over-year growth rates
        growth_rates = []
        for i in range(1, len(clean_eps)):
            if clean_eps.iloc[i-1] > 0:
                growth = ((clean_eps.iloc[i] - clean_eps.iloc[i-1]) / clean_eps.iloc[i-1]) * 100
                growth_rates.append(growth)
        
        if growth_rates:
            avg_growth = np.mean(growth_rates)
            return max(-50, min(100, avg_growth))
        
        return 0.0


def intrinsic_value(eps, growth_rate, pe_ratio=None):
    """
    Calculate intrinsic value using Graham's formula
    
    Graham's Formula:
    Intrinsic Value = EPS × (8.5 + 2g)
    
    Where:
    - 8.5 is the base PE ratio for a no-growth company
    - g is the expected annual growth rate (in percentage)
    
    Args:
        eps: Current or average EPS
        growth_rate: Expected growth rate (percentage)
        pe_ratio: Optional custom PE ratio (if None, uses Graham's formula)
    
    Returns:
        float: Intrinsic value per share
    """
    if eps <= 0:
        return 0.0
    
    # Cap growth rate for conservative estimate
    conservative_growth = min(growth_rate, 25)  # Max 25% growth assumption
    
    if pe_ratio is not None:
        # Use custom PE ratio
        return eps * pe_ratio
    else:
        # Graham's formula: V = EPS × (8.5 + 2g)
        # 8.5 = base PE for no-growth company
        # 2g = growth component
        intrinsic = eps * (8.5 + 2 * conservative_growth)
        return max(0, intrinsic)


def margin_of_safety(intrinsic_value, current_price, min_mos=20):
    """
    Calculate Margin of Safety
    
    MOS = (Intrinsic Value - Current Price) / Intrinsic Value × 100
    
    Graham recommended buying only when there's at least 20-30% margin
    
    Args:
        intrinsic_value: Calculated intrinsic value
        current_price: Current market price
        min_mos: Minimum acceptable MOS percentage (default 20%)
    
    Returns:
        tuple: (mos_value, mos_percentage)
    """
    if intrinsic_value <= 0 or current_price <= 0:
        return (0, 0)
    
    mos_value = intrinsic_value - current_price
    mos_percentage = (mos_value / intrinsic_value) * 100
    
    return (mos_value, mos_percentage)


def graham_rating(mos_percentage):
    """
    Rate the investment based on Graham's principles
    
    Returns:
        str: Rating with emoji
    """
    if mos_percentage >= 50:
        return "STRONG VALUE 💎💎"
    elif mos_percentage >= 40:
        return "EXCELLENT VALUE 💎"
    elif mos_percentage >= 30:
        return "GOOD VALUE 🟢"
    elif mos_percentage >= 20:
        return "FAIR VALUE 🟡"
    elif mos_percentage >= 10:
        return "MARGINAL 🟠"
    elif mos_percentage >= 0:
        return "OVERVALUED 🔴"
    else:
        return "EXPENSIVE 🔴🔴"


def conservative_intrinsic_value(eps, growth_rate):
    """
    Ultra-conservative intrinsic value calculation
    
    Uses lower of:
    1. Graham's formula with capped growth
    2. 15 × EPS (reasonable PE for stable company)
    
    Args:
        eps: Current EPS
        growth_rate: Growth rate percentage
    
    Returns:
        float: Conservative intrinsic value
    """
    if eps <= 0:
        return 0.0
    
    # Method 1: Graham's formula with conservative growth
    graham_value = intrinsic_value(eps, min(growth_rate, 15))
    
    # Method 2: Simple 15 PE multiple
    pe_value = eps * 15
    
    # Return the lower (more conservative) value
    return min(graham_value, pe_value)


def get_eps_metrics(eps_history):
    """
    Calculate various EPS metrics
    
    Returns:
        dict: EPS metrics including average, growth, consistency
    """
    if len(eps_history) < 1:
        return None
    
    clean_eps = eps_history.dropna()
    
    if len(clean_eps) < 1:
        return None
    
    metrics = {
        "current_eps": clean_eps.iloc[-1] if len(clean_eps) > 0 else 0,
        "avg_eps_3y": clean_eps.tail(3).mean() if len(clean_eps) >= 3 else clean_eps.mean(),
        "avg_eps_5y": clean_eps.tail(5).mean() if len(clean_eps) >= 5 else clean_eps.mean(),
        "min_eps": clean_eps.min(),
        "max_eps": clean_eps.max(),
        "growth_3y": calculate_growth(clean_eps.tail(3)) if len(clean_eps) >= 3 else 0,
        "growth_5y": calculate_growth(clean_eps.tail(5)) if len(clean_eps) >= 5 else 0,
    }
    
    # Consistency score (0-100)
    # Lower coefficient of variation = higher consistency
    if len(clean_eps) >= 3:
        cv = (clean_eps.std() / clean_eps.mean()) if clean_eps.mean() > 0 else 999
        consistency = max(0, 100 - (cv * 100))
        metrics["consistency"] = min(100, consistency)
    else:
        metrics["consistency"] = 0
    
    return metrics
    