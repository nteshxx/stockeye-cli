"""
Core functions for Graham's classic bargain analysis
Implements formulas and calculations for different value investing strategies
"""
import pandas as pd

from typing import Dict, Optional, Tuple
from stockeye.utils.utilities import safe_float, safe_int


def calculate_ncav(info: dict) -> Optional[float]:
    """
    Calculate Net Current Asset Value (NCAV) per share
    
    Formula: (Current Assets - Total Liabilities) / Shares Outstanding
    
    Args:
        info: Stock info dictionary
        
    Returns:
        NCAV per share or None if data unavailable
    """
    try:
        current_assets = safe_float(info.get('totalCurrentAssets'), None)
        total_liabilities = safe_float(info.get('totalLiab'), None)
        shares_outstanding = safe_float(info.get('sharesOutstanding'), None)
        
        if current_assets is None or total_liabilities is None or shares_outstanding is None:
            return None
        
        if shares_outstanding <= 0:
            return None
        
        ncav = (current_assets - total_liabilities) / shares_outstanding
        return ncav if ncav > 0 else None
        
    except Exception:
        return None


def calculate_net_net_ratio(price: float, ncav: float) -> Optional[float]:
    """
    Calculate Net-Net ratio (Price / NCAV)
    
    Graham's rule: Buy when ratio < 0.67 (2/3 of NCAV)
    
    Args:
        price: Current stock price
        ncav: Net Current Asset Value per share
        
    Returns:
        Net-Net ratio or None
    """
    if ncav is None or ncav <= 0 or price <= 0:
        return None
    
    return price / ncav


def calculate_working_capital_per_share(info: dict) -> Optional[float]:
    """
    Calculate Working Capital per share
    
    Formula: (Current Assets - Current Liabilities) / Shares Outstanding
    
    Args:
        info: Stock info dictionary
        
    Returns:
        Working capital per share or None
    """
    try:
        current_assets = safe_float(info.get('totalCurrentAssets'), None)
        current_liabilities = safe_float(info.get('totalCurrentLiabilities'), None)
        shares_outstanding = safe_float(info.get('sharesOutstanding'), None)
        
        if None in [current_assets, current_liabilities, shares_outstanding]:
            return None
        
        if shares_outstanding <= 0:
            return None
        
        working_capital = (current_assets - current_liabilities) / shares_outstanding
        return working_capital
        
    except Exception:
        return None


def calculate_tangible_book_value(info: dict) -> Optional[float]:
    """
    Calculate Tangible Book Value per share
    
    Formula: (Total Assets - Intangible Assets - Total Liabilities) / Shares Outstanding
    
    Args:
        info: Stock info dictionary
        
    Returns:
        Tangible book value per share or None
    """
    try:
        total_assets = safe_float(info.get('totalAssets'), None)
        intangible_assets = safe_float(info.get('intangibleAssets'), 0)  # Default 0 if not reported
        total_liabilities = safe_float(info.get('totalLiab'), None)
        shares_outstanding = safe_float(info.get('sharesOutstanding'), None)
        
        if None in [total_assets, total_liabilities, shares_outstanding]:
            return None
        
        if shares_outstanding <= 0:
            return None
        
        tangible_bv = (total_assets - intangible_assets - total_liabilities) / shares_outstanding
        return tangible_bv
        
    except Exception:
        return None


def calculate_liquidation_value(info: dict, discount: float = 0.5) -> Optional[float]:
    """
    Calculate estimated liquidation value per share
    
    Conservative estimate applying discounts to assets:
    - Current Assets: 100% (already liquid)
    - Fixed Assets: 50% discount (hard to sell)
    - Intangibles: 0% (worthless in liquidation)
    
    Formula: (Current Assets + discount * Fixed Assets - Total Liabilities) / Shares
    
    Args:
        info: Stock info dictionary
        discount: Discount rate for fixed assets (default 0.5)
        
    Returns:
        Liquidation value per share or None
    """
    try:
        total_assets = safe_float(info.get('totalAssets'), None)
        current_assets = safe_float(info.get('totalCurrentAssets'), None)
        intangible_assets = safe_float(info.get('intangibleAssets'), 0)
        total_liabilities = safe_float(info.get('totalLiab'), None)
        shares_outstanding = safe_float(info.get('sharesOutstanding'), None)
        
        if None in [total_assets, current_assets, total_liabilities, shares_outstanding]:
            return None
        
        if shares_outstanding <= 0:
            return None
        
        # Fixed assets = Total - Current - Intangible
        fixed_assets = total_assets - current_assets - intangible_assets
        fixed_assets = max(0, fixed_assets)  # Can't be negative
        
        # Liquidation value
        liq_value = (current_assets + (discount * fixed_assets) - total_liabilities) / shares_outstanding
        
        return liq_value if liq_value > 0 else None
        
    except Exception:
        return None


def calculate_earnings_yield(eps: float, price: float) -> Optional[float]:
    """
    Calculate earnings yield (inverse of P/E)
    
    Formula: (EPS / Price) * 100
    
    Higher is better - shows percentage return based on earnings
    
    Args:
        eps: Earnings per share
        price: Current stock price
        
    Returns:
        Earnings yield percentage or None
    """
    if price <= 0 or eps is None or eps <= 0:
        return None
    
    return (eps / price) * 100


def calculate_graham_number(eps: float, book_value_per_share: float) -> Optional[float]:
    """
    Calculate Graham Number (fair value estimate)
    
    Formula: sqrt(22.5 * EPS * Book Value per Share)
    
    Graham's rule: Buy when Price < Graham Number
    
    Args:
        eps: Earnings per share
        book_value_per_share: Book value per share
        
    Returns:
        Graham number or None
    """
    if eps is None or book_value_per_share is None:
        return None
    
    if eps <= 0 or book_value_per_share <= 0:
        return None
    
    try:
        graham_num = (22.5 * eps * book_value_per_share) ** 0.5
        return graham_num
    except Exception:
        return None


def calculate_defensive_investor_score(info: dict, price: float, eps: float) -> Tuple[int, Dict]:
    """
    Calculate Graham's Defensive Investor score (0-7)
    
    Criteria:
    1. Adequate size (Market Cap > $100M / ₹500Cr)
    2. Strong financial condition (Current Ratio ≥ 2.0)
    3. Earnings stability (Positive earnings last 10 years)
    4. Dividend record (Some dividend in recent years)
    5. Earnings growth (EPS growth > 0%)
    6. Moderate P/E (P/E ≤ 15)
    7. Moderate P/B (P/B ≤ 1.5)
    
    Args:
        info: Stock info dictionary
        price: Current stock price
        eps: Earnings per share
        
    Returns:
        Tuple of (score, criteria_details)
    """
    score = 0
    criteria = {}
    
    # 1. Adequate Size
    market_cap = safe_int(info.get('marketCap'), 0)
    criteria['size'] = market_cap >= 5_000_000_000  # ₹500 Cr
    score += 1 if criteria['size'] else 0
    
    # 2. Current Ratio ≥ 2.0
    current_ratio = safe_float(info.get('currentRatio'), None)
    criteria['current_ratio'] = current_ratio is not None and current_ratio >= 2.0
    score += 1 if criteria['current_ratio'] else 0
    
    # 3. Positive earnings (simplified - check if EPS > 0)
    criteria['earnings_stability'] = eps is not None and eps > 0
    score += 1 if criteria['earnings_stability'] else 0
    
    # 4. Dividend payment
    dividend_yield = safe_float(info.get('dividendYield'), None)
    criteria['dividend_record'] = dividend_yield is not None and dividend_yield > 0
    score += 1 if criteria['dividend_record'] else 0
    
    # 5. Earnings growth
    earnings_growth = safe_float(info.get('earningsGrowth'), None)
    criteria['earnings_growth'] = earnings_growth is not None and earnings_growth > 0
    score += 1 if criteria['earnings_growth'] else 0
    
    # 6. P/E ≤ 15
    pe_ratio = safe_float(info.get('trailingPE'), None)
    criteria['moderate_pe'] = pe_ratio is not None and 0 < pe_ratio <= 15
    score += 1 if criteria['moderate_pe'] else 0
    
    # 7. P/B ≤ 1.5
    pb_ratio = safe_float(info.get('priceToBook'), None)
    criteria['moderate_pb'] = pb_ratio is not None and 0 < pb_ratio <= 1.5
    score += 1 if criteria['moderate_pb'] else 0
    
    return score, criteria


def calculate_cigar_butt_score(price: float, eps: float, book_value: float, 
                                debt_to_equity: float) -> Tuple[int, Dict]:
    """
    Calculate Cigar Butt investment score (0-5)
    
    Criteria for beaten-down stocks with one last puff:
    1. Very low P/E (< 7)
    2. Trading below book value (P/B < 0.8)
    3. Positive earnings (EPS > 0)
    4. Low debt (D/E < 1.0)
    5. Extremely cheap (P/E < 5 or P/B < 0.5)
    
    Args:
        price: Current stock price
        eps: Earnings per share
        book_value: Book value per share
        debt_to_equity: Debt to equity ratio
        
    Returns:
        Tuple of (score, criteria_details)
    """
    score = 0
    criteria = {}
    
    # Calculate ratios with null safety
    pe_ratio = None
    if eps is not None and eps > 0 and price > 0:
        pe_ratio = price / eps
    
    pb_ratio = None
    if book_value is not None and book_value > 0 and price > 0:
        pb_ratio = price / book_value
    
    # 1. Very low P/E (< 7)
    criteria['very_low_pe'] = pe_ratio is not None and 0 < pe_ratio < 7
    score += 1 if criteria['very_low_pe'] else 0
    
    # 2. Below book value
    criteria['below_book'] = pb_ratio is not None and 0 < pb_ratio < 0.8
    score += 1 if criteria['below_book'] else 0
    
    # 3. Positive earnings
    criteria['profitable'] = eps is not None and eps > 0
    score += 1 if criteria['profitable'] else 0
    
    # 4. Low debt
    criteria['low_debt'] = debt_to_equity is not None and debt_to_equity < 1.0
    score += 1 if criteria['low_debt'] else 0
    
    # 5. Extremely cheap (bonus point)
    extremely_cheap_pe = pe_ratio is not None and 0 < pe_ratio < 5
    extremely_cheap_pb = pb_ratio is not None and 0 < pb_ratio < 0.5
    criteria['extremely_cheap'] = extremely_cheap_pe or extremely_cheap_pb
    score += 1 if criteria['extremely_cheap'] else 0
    
    return score, criteria


def estimate_growth_rate(info: dict) -> float:
    """
    Estimate conservative growth rate from available data
    
    Uses average of revenue growth and earnings growth
    Caps between -20% and 25%
    
    Args:
        info: Stock info dictionary
        
    Returns:
        Estimated growth rate (%)
    """
    revenue_growth = safe_float(info.get('revenueGrowth'), None)
    earnings_growth = safe_float(info.get('earningsGrowth'), None)
    
    # Convert to percentage if available
    revenue_growth_pct = revenue_growth * 100 if revenue_growth is not None else None
    earnings_growth_pct = earnings_growth * 100 if earnings_growth is not None else None
    
    # Calculate average of available values
    growth_values = []
    if revenue_growth_pct is not None:
        growth_values.append(revenue_growth_pct)
    if earnings_growth_pct is not None:
        growth_values.append(earnings_growth_pct)
    
    if growth_values:
        growth = sum(growth_values) / len(growth_values)
    else:
        growth = 0
    
    # Conservative caps
    return max(-20, min(25, growth))


def calculate_debt_metrics(info: dict) -> Dict[str, Optional[float]]:
    """
    Calculate various debt-related metrics
    
    Returns:
        Dictionary with debt metrics
    """
    total_debt = safe_float(info.get('totalDebt'), None)
    total_equity = safe_float(info.get('totalStockholderEquity'), None)
    total_assets = safe_float(info.get('totalAssets'), None)
    ebit = safe_float(info.get('ebit'), None)
    interest_expense = safe_float(info.get('interestExpense'), None)
    
    metrics = {}
    
    # Debt to Equity
    if total_debt is not None and total_equity is not None and total_equity > 0:
        metrics['debt_to_equity'] = total_debt / total_equity
    else:
        metrics['debt_to_equity'] = None
    
    # Debt to Assets
    if total_debt is not None and total_assets is not None and total_assets > 0:
        metrics['debt_to_assets'] = total_debt / total_assets
    else:
        metrics['debt_to_assets'] = None
    
    # Interest Coverage
    if ebit is not None and interest_expense is not None and interest_expense > 0:
        metrics['interest_coverage'] = ebit / interest_expense
    else:
        metrics['interest_coverage'] = None
    
    # Is debt-free or near debt-free?
    metrics['is_debt_free'] = (
        metrics['debt_to_equity'] is not None and 
        metrics['debt_to_equity'] < 0.1
    )
    
    return metrics


def calculate_quality_metrics(info: dict) -> Dict[str, Optional[float]]:
    """
    Calculate quality and profitability metrics
    
    Returns:
        Dictionary with quality metrics
    """
    metrics = {}
    
    # Return on Equity
    roe = safe_float(info.get('returnOnEquity'), None)
    if roe is not None:
        metrics['roe'] = roe * 100  # Convert to percentage
    else:
        metrics['roe'] = None
    
    # Return on Assets
    roa = safe_float(info.get('returnOnAssets'), None)
    if roa is not None:
        metrics['roa'] = roa * 100
    else:
        metrics['roa'] = None
    
    # Profit Margin
    profit_margin = safe_float(info.get('profitMargins'), None)
    if profit_margin is not None:
        metrics['profit_margin'] = profit_margin * 100
    else:
        metrics['profit_margin'] = None
    
    # Operating Margin
    operating_margin = safe_float(info.get('operatingMargins'), None)
    if operating_margin is not None:
        metrics['operating_margin'] = operating_margin * 100
    else:
        metrics['operating_margin'] = None
    
    # Current Ratio
    metrics['current_ratio'] = safe_float(info.get('currentRatio'), None)
    
    # Quick Ratio
    metrics['quick_ratio'] = safe_float(info.get('quickRatio'), None)
    
    return metrics


def is_financially_distressed(info: dict, eps: float) -> Tuple[bool, str]:
    """
    Check if company shows signs of financial distress
    
    Warning signs:
    - Negative earnings
    - Very high debt (D/E > 3.0)
    - Poor interest coverage (< 1.5)
    - Negative working capital
    
    Args:
        info: Stock info dictionary
        eps: Earnings per share
        
    Returns:
        Tuple of (is_distressed, reason)
    """
    reasons = []
    
    # Check negative earnings
    if eps is None or eps < 0:
        reasons.append("Negative earnings")
    
    # Check debt levels
    debt_metrics = calculate_debt_metrics(info)
    de_ratio = debt_metrics.get('debt_to_equity')
    if de_ratio is not None and de_ratio > 3.0:
        reasons.append(f"Very high debt (D/E: {de_ratio:.2f})")
    
    # Check interest coverage
    interest_cov = debt_metrics.get('interest_coverage')
    if interest_cov is not None and interest_cov < 1.5:
        reasons.append(f"Poor interest coverage ({interest_cov:.2f}x)")
    
    # Check working capital
    working_capital = calculate_working_capital_per_share(info)
    if working_capital is not None and working_capital < 0:
        reasons.append("Negative working capital")
    
    is_distressed = len(reasons) > 0
    reason = "; ".join(reasons) if reasons else "Financially stable"
    
    return is_distressed, reason


def calculate_margin_of_safety_score(price: float, intrinsic_value: float, 
                                     ncav: Optional[float], 
                                     tangible_bv: Optional[float]) -> Tuple[int, Dict]:
    """
    Calculate overall margin of safety score (0-4)
    
    Criteria:
    1. Price < Intrinsic Value (Graham formula)
    2. Price < 2/3 NCAV (if available)
    3. Price < Tangible Book Value
    4. Significant discount (>40% from intrinsic)
    
    Args:
        price: Current stock price
        intrinsic_value: Calculated intrinsic value
        ncav: Net Current Asset Value per share
        tangible_bv: Tangible book value per share
        
    Returns:
        Tuple of (score, criteria_details)
    """
    score = 0
    criteria = {}
    
    # 1. Price < Intrinsic Value
    if intrinsic_value is not None and intrinsic_value > 0:
        criteria['below_intrinsic'] = price < intrinsic_value
        score += 1 if criteria['below_intrinsic'] else 0
        
        # Calculate discount
        criteria['intrinsic_discount'] = ((intrinsic_value - price) / intrinsic_value) * 100
    else:
        criteria['below_intrinsic'] = False
        criteria['intrinsic_discount'] = 0
    
    # 2. Price < 2/3 NCAV (Net-Net)
    if ncav is not None and ncav > 0:
        net_net_threshold = ncav * 0.67
        criteria['below_net_net'] = price < net_net_threshold
        score += 1 if criteria['below_net_net'] else 0
    else:
        criteria['below_net_net'] = False
    
    # 3. Price < Tangible Book Value
    if tangible_bv is not None and tangible_bv > 0:
        criteria['below_tangible_bv'] = price < tangible_bv
        score += 1 if criteria['below_tangible_bv'] else 0
    else:
        criteria['below_tangible_bv'] = False
    
    # 4. Significant discount (>40%)
    discount_pct = criteria.get('intrinsic_discount', 0)
    if discount_pct > 40:
        criteria['large_discount'] = True
        score += 1
    else:
        criteria['large_discount'] = False
    
    return score, criteria
