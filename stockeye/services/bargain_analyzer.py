"""
Graham Bargain Analyzer
Classifies stocks into different Graham bargain scenarios and assigns scores
"""
import pandas as pd

from typing import Dict, Optional, List

from stockeye.core.classic_bargain import (
    calculate_ncav,
    calculate_net_net_ratio,
    calculate_working_capital_per_share,
    calculate_tangible_book_value,
    calculate_liquidation_value,
    calculate_earnings_yield,
    calculate_graham_number,
    calculate_defensive_investor_score,
    calculate_cigar_butt_score,
    estimate_growth_rate,
    calculate_debt_metrics,
    calculate_quality_metrics,
    is_financially_distressed,
    calculate_margin_of_safety_score,
)
from stockeye.core.fundamentals import fundamental_score
from stockeye.core.margin_of_safety import intrinsic_value, margin_of_safety
from stockeye.utils.utilities import safe_float, safe_int


class GrahamScenario:
    """Enumeration of Graham bargain scenarios"""
    NET_NET = "NET_NET"  # Trading < 2/3 NCAV
    ASSET_PLAY = "ASSET_PLAY"  # Below book/liquidation value
    CIGAR_BUTT = "CIGAR_BUTT"  # Beaten down but profitable
    DEFENSIVE = "DEFENSIVE"  # Meets defensive investor criteria
    DEEP_VALUE = "DEEP_VALUE"  # High margin of safety (>40%)
    MODERATE_VALUE = "MODERATE_VALUE"  # Good value (30-40% MOS)
    STATISTICAL_BARGAIN = "STATISTICAL_BARGAIN"  # Meets multiple quantitative criteria
    DISTRESSED = "DISTRESSED"  # Financially troubled
    OVERVALUED = "OVERVALUED"  # No margin of safety


def analyze_graham_bargain(symbol: str, df: pd.DataFrame, info: dict) -> Optional[Dict]:
    """
    Comprehensive Graham-style bargain analysis
    
    Analyzes stock across multiple value frameworks:
    - Net-Net (NCAV)
    - Asset Play (Book Value, Liquidation)
    - Cigar Butt (Deep value in distressed)
    - Defensive Investor
    - Margin of Safety
    
    Args:
        symbol: Stock ticker
        df: Price history DataFrame
        info: Stock info dictionary
        
    Returns:
        Dictionary with complete analysis or None if insufficient data
    """
    try:
        # Validate inputs
        if df is None or info is None or len(df) < 50:
            return None
        
        # Get current price
        price = safe_float(df['Close'].iloc[-1])
        if price is None or price <= 0:
            return None
        
        # Get EPS
        trailing_eps = safe_float(info.get('trailingEps'), None)
        forward_eps = safe_float(info.get('forwardEps'), None)
        
        eps_values = [e for e in [trailing_eps, forward_eps] if e is not None and e > 0]
        if not eps_values:
            return None
        
        avg_eps = sum(eps_values) / len(eps_values)
        
        # Get book value per share
        book_value = safe_float(info.get('bookValue'), None)
        
        # Get basic ratios
        pe_ratio = safe_float(info.get('trailingPE'), None)
        pb_ratio = safe_float(info.get('priceToBook'), None)
        
        # Calculate asset values
        ncav = calculate_ncav(info)
        tangible_bv = calculate_tangible_book_value(info)
        liquidation_value = calculate_liquidation_value(info)
        working_capital_ps = calculate_working_capital_per_share(info)
        
        # Calculate intrinsic value using Graham formula
        growth = estimate_growth_rate(info)
        graham_intrinsic = intrinsic_value(avg_eps, growth)
        mos_value, mos_pct = margin_of_safety(graham_intrinsic, price)
        
        # Calculate Graham Number
        graham_num = calculate_graham_number(avg_eps, book_value) if book_value else None
        
        # Get debt and quality metrics
        debt_metrics = calculate_debt_metrics(info)
        quality_metrics = calculate_quality_metrics(info)
        
        # Check financial distress
        distressed, distress_reason = is_financially_distressed(info, avg_eps)
        
        # Calculate scores for different strategies
        defensive_score, defensive_criteria = calculate_defensive_investor_score(
            info, price, avg_eps
        )
        
        # For cigar butt score, safely get debt_to_equity with default
        cigar_de = debt_metrics.get('debt_to_equity')
        if cigar_de is None:
            cigar_de = 999  # High value if unknown (conservative)
        
        cigar_butt_score, cigar_criteria = calculate_cigar_butt_score(
            price, avg_eps, book_value if book_value else 0, cigar_de
        )
        
        mos_score, mos_criteria = calculate_margin_of_safety_score(
            price, graham_intrinsic, ncav, tangible_bv
        )
        
        # Calculate overall Graham score (0-100)
        graham_score = calculate_overall_graham_score(
            defensive_score, cigar_butt_score, mos_score, mos_pct
        )
        
        # Determine primary scenario
        scenario, scenario_score = determine_scenario(
            price, ncav, tangible_bv, liquidation_value, mos_pct, 
            pe_ratio, pb_ratio, defensive_score, cigar_butt_score, distressed
        )
        
        # Calculate earnings yield
        earnings_yield = calculate_earnings_yield(avg_eps, price)
        
        # Get fundamental score
        fscore = fundamental_score(info)
        
        # Get dividend yield
        dividend_yield = safe_float(info.get('dividendYield'), None)
        dividend_yield_pct = dividend_yield * 100 if dividend_yield is not None else 0
        
        # Compile complete analysis
        analysis = {
            # Basic info
            "symbol": symbol,
            "company_name": info.get('longName', symbol),
            "price": price,
            "market_cap": safe_int(info.get("marketCap", 0)),
            
            # Earnings & valuation
            "eps": avg_eps,
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "earnings_yield": earnings_yield,
            
            # Asset values
            "book_value": book_value,
            "ncav": ncav,
            "tangible_bv": tangible_bv,
            "liquidation_value": liquidation_value,
            "working_capital_ps": working_capital_ps,
            
            # Net-Net analysis
            "net_net_ratio": calculate_net_net_ratio(price, ncav) if ncav else None,
            "net_net_buy_price": ncav * 0.67 if ncav else None,
            
            # Graham intrinsic value
            "growth": growth,
            "graham_intrinsic": graham_intrinsic,
            "mos_value": mos_value,
            "mos_pct": mos_pct,
            "graham_number": graham_num,
            
            # Debt metrics
            "debt_to_equity": debt_metrics.get('debt_to_equity'),
            "debt_to_assets": debt_metrics.get('debt_to_assets'),
            "interest_coverage": debt_metrics.get('interest_coverage'),
            "is_debt_free": debt_metrics.get('is_debt_free', False),
            
            # Quality metrics
            "roe": quality_metrics.get('roe'),
            "roa": quality_metrics.get('roa'),
            "profit_margin": quality_metrics.get('profit_margin'),
            "current_ratio": quality_metrics.get('current_ratio'),
            "quick_ratio": quality_metrics.get('quick_ratio'),
            
            # Scores
            "graham_score": graham_score,
            "defensive_score": defensive_score,
            "cigar_butt_score": cigar_butt_score,
            "mos_score": mos_score,
            "fscore": fscore,
            
            # Scenario classification
            "scenario": scenario,
            "scenario_score": scenario_score,
            "scenario_description": get_scenario_description(scenario),
            
            # Criteria details
            "defensive_criteria": defensive_criteria,
            "cigar_criteria": cigar_criteria,
            "mos_criteria": mos_criteria,
            
            # Financial health
            "is_distressed": distressed,
            "distress_reason": distress_reason,
            
            # Dividend
            "dividend_yield": dividend_yield_pct,
        }
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def calculate_overall_graham_score(defensive_score: int, cigar_score: int, 
                                   mos_score: int, mos_pct: float) -> int:
    """
    Calculate overall Graham score (0-100)
    
    Weighted combination of different scores:
    - Defensive Score: 30% (7 criteria)
    - Cigar Butt Score: 20% (5 criteria)
    - MOS Score: 20% (4 criteria)
    - MOS Percentage: 30% (actual margin)
    
    Args:
        defensive_score: Score out of 7
        cigar_score: Score out of 5
        mos_score: Score out of 4
        mos_pct: Margin of safety percentage
        
    Returns:
        Overall score (0-100)
    """
    # Normalize scores to 0-100 scale
    defensive_normalized = (defensive_score / 7) * 100 if defensive_score else 0
    cigar_normalized = (cigar_score / 5) * 100 if cigar_score else 0
    mos_score_normalized = (mos_score / 4) * 100 if mos_score else 0
    
    # MOS percentage: 0% = 0 points, 50%+ = 100 points
    mos_pct_normalized = min(100, (mos_pct / 50) * 100) if mos_pct > 0 else 0
    
    # Weighted average
    total_score = (
        defensive_normalized * 0.30 +
        cigar_normalized * 0.20 +
        mos_score_normalized * 0.20 +
        mos_pct_normalized * 0.30
    )
    
    return int(round(total_score))


def determine_scenario(price: float, ncav: Optional[float], tangible_bv: Optional[float],
                      liquidation_value: Optional[float], mos_pct: float,
                      pe_ratio: Optional[float], pb_ratio: Optional[float],
                      defensive_score: int, cigar_score: int, 
                      is_distressed: bool) -> tuple[str, int]:
    """
    Determine primary Graham scenario and scenario-specific score
    
    Priority order:
    1. NET_NET (highest conviction)
    2. ASSET_PLAY
    3. DISTRESSED
    4. CIGAR_BUTT
    5. DEEP_VALUE
    6. DEFENSIVE
    7. MODERATE_VALUE
    8. STATISTICAL_BARGAIN
    9. OVERVALUED
    
    Args:
        price: Current price
        ncav: Net current asset value
        tangible_bv: Tangible book value
        liquidation_value: Estimated liquidation value
        mos_pct: Margin of safety percentage
        pe_ratio: Price to earnings ratio
        pb_ratio: Price to book ratio
        defensive_score: Defensive investor score
        cigar_score: Cigar butt score
        is_distressed: Financial distress flag
        
    Returns:
        Tuple of (scenario, scenario_score)
    """
    
    # 1. NET-NET: Price < 2/3 NCAV (Graham's favorite)
    if ncav and ncav > 0:
        net_net_ratio = price / ncav
        if net_net_ratio < 0.67:
            # Score based on how deep below 2/3 NCAV
            discount_from_threshold = (0.67 - net_net_ratio) / 0.67
            score = min(100, int(80 + (discount_from_threshold * 20)))
            return GrahamScenario.NET_NET, score
    
    # 2. ASSET PLAY: Below tangible book or liquidation value
    asset_play_signals = 0
    asset_play_score = 50
    
    if tangible_bv and tangible_bv > 0 and price < tangible_bv:
        asset_play_signals += 1
        discount = ((tangible_bv - price) / tangible_bv) * 100
        asset_play_score += int(discount / 2)  # Bigger discount = higher score
    
    if liquidation_value and liquidation_value > 0 and price < liquidation_value:
        asset_play_signals += 1
        asset_play_score += 10
    
    if pb_ratio and pb_ratio < 0.8:
        asset_play_signals += 1
        asset_play_score += 10
    
    if asset_play_signals >= 2:
        return GrahamScenario.ASSET_PLAY, min(100, asset_play_score)
    
    # 3. DISTRESSED: Financially troubled
    if is_distressed:
        # Lower score for distressed companies
        base_score = 20
        # Add points if there's still some value
        if mos_pct > 30:
            base_score += 20
        if cigar_score >= 3:
            base_score += 15
        return GrahamScenario.DISTRESSED, min(60, base_score)
    
    # 4. CIGAR BUTT: Beaten down but still profitable
    if cigar_score >= 4:
        # High cigar score = good cigar butt opportunity
        score = 60 + (cigar_score * 8)
        return GrahamScenario.CIGAR_BUTT, min(100, score)
    
    # 5. DEEP VALUE: MOS ≥ 40%
    if mos_pct >= 40:
        # Score based on MOS percentage
        score = int(60 + (mos_pct - 40))
        return GrahamScenario.DEEP_VALUE, min(100, score)
    
    # 6. DEFENSIVE: Meets defensive investor criteria (score ≥ 5)
    if defensive_score >= 5:
        score = 50 + (defensive_score * 7)
        return GrahamScenario.DEFENSIVE, min(100, score)
    
    # 7. MODERATE VALUE: MOS 25-40%
    if mos_pct >= 25:
        score = int(40 + (mos_pct - 25))
        return GrahamScenario.MODERATE_VALUE, min(80, score)
    
    # 8. STATISTICAL BARGAIN: Meets multiple criteria
    stat_signals = 0
    if pe_ratio and 0 < pe_ratio <= 12:
        stat_signals += 1
    if pb_ratio and 0 < pb_ratio <= 1.2:
        stat_signals += 1
    if defensive_score >= 4:
        stat_signals += 1
    if mos_pct >= 15:
        stat_signals += 1
    
    if stat_signals >= 3:
        score = 40 + (stat_signals * 10)
        return GrahamScenario.STATISTICAL_BARGAIN, min(70, score)
    
    # 9. OVERVALUED: No significant value identified
    return GrahamScenario.OVERVALUED, max(0, int(mos_pct)) if mos_pct > 0 else 0


def get_scenario_description(scenario: str) -> str:
    """Get human-readable description of scenario"""
    descriptions = {
        GrahamScenario.NET_NET: "Trading below 2/3 of Net Current Asset Value - Graham's favorite",
        GrahamScenario.ASSET_PLAY: "Trading below liquidation/book value - Asset-rich bargain",
        GrahamScenario.CIGAR_BUTT: "Beaten-down but profitable - One last puff opportunity",
        GrahamScenario.DEFENSIVE: "Meets Graham's defensive investor criteria - Quality at fair price",
        GrahamScenario.DEEP_VALUE: "High margin of safety (≥40%) - Significant undervaluation",
        GrahamScenario.MODERATE_VALUE: "Good value (25-40% MOS) - Reasonable opportunity",
        GrahamScenario.STATISTICAL_BARGAIN: "Meets multiple quantitative criteria - Statistical edge",
        GrahamScenario.DISTRESSED: "Financially troubled - High risk turnaround play",
        GrahamScenario.OVERVALUED: "No significant margin of safety - Avoid or wait",
    }
    return descriptions.get(scenario, "Unknown scenario")


def get_scenario_emoji(scenario: str) -> str:
    """Get emoji representation of scenario"""
    emojis = {
        GrahamScenario.NET_NET: "💎",
        GrahamScenario.ASSET_PLAY: "🏦",
        GrahamScenario.CIGAR_BUTT: "🚬",
        GrahamScenario.DEFENSIVE: "🛡️",
        GrahamScenario.DEEP_VALUE: "⭐",
        GrahamScenario.MODERATE_VALUE: "✅",
        GrahamScenario.STATISTICAL_BARGAIN: "📊",
        GrahamScenario.DISTRESSED: "⚠️",
        GrahamScenario.OVERVALUED: "❌",
    }
    return emojis.get(scenario, "❓")


def get_investment_recommendation(scenario: str, scenario_score: int, 
                                  graham_score: int, fscore: int) -> str:
    """
    Get investment recommendation based on analysis
    
    Args:
        scenario: Primary scenario classification
        scenario_score: Scenario-specific score
        graham_score: Overall Graham score
        fscore: Fundamental score
        
    Returns:
        Investment recommendation string
    """
    # Strong Buy criteria
    if scenario == GrahamScenario.NET_NET and scenario_score >= 80:
        return "STRONG BUY 🟢🟢"
    
    if scenario == GrahamScenario.ASSET_PLAY and scenario_score >= 75 and fscore >= 6:
        return "STRONG BUY 🟢🟢"
    
    if scenario == GrahamScenario.DEEP_VALUE and scenario_score >= 70 and fscore >= 7:
        return "STRONG BUY 🟢🟢"
    
    # Buy criteria
    if scenario in [GrahamScenario.NET_NET, GrahamScenario.ASSET_PLAY, GrahamScenario.DEEP_VALUE]:
        if scenario_score >= 60:
            return "BUY 🟢"
    
    if scenario == GrahamScenario.DEFENSIVE and scenario_score >= 70:
        return "BUY 🟢"
    
    if scenario == GrahamScenario.CIGAR_BUTT and scenario_score >= 75 and fscore >= 5:
        return "BUY 🟢"
    
    # Hold/Watch criteria
    if scenario == GrahamScenario.MODERATE_VALUE and graham_score >= 60:
        return "HOLD/WATCH 🟡"
    
    if scenario == GrahamScenario.STATISTICAL_BARGAIN and graham_score >= 50:
        return "HOLD/WATCH 🟡"
    
    # Avoid criteria
    if scenario == GrahamScenario.DISTRESSED:
        return "AVOID ⚠️"
    
    if scenario == GrahamScenario.OVERVALUED:
        return "AVOID ❌"
    
    # Default
    if graham_score >= 60:
        return "HOLD/WATCH 🟡"
    
    return "AVOID ❌"
