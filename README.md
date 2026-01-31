# 🚀 StockEye v2.0 - Advanced Indian Stock Market Analyzer

**Enhanced with Indian Market Intelligence**

A comprehensive command-line tool for technical and fundamental stock analysis, specifically optimized for the Indian stock market (NSE/BSE).

## 🆕 What's New in v2.0

### Indian Market-Specific Enhancements

1. **India VIX Integration** 🌡️
   - Real-time volatility context
   - Automatic rating adjustments based on market fear/greed
   - VIX < 15: Favorable conditions
   - VIX > 20: Cautious approach
   - VIX > 25: High risk environment

2. **Bollinger Bands** 📊
   - Popular indicator in Indian intraday trading
   - Identifies overbought/oversold conditions
   - Dynamic support/resistance levels
   - Position indicator (0-100%)

3. **Supertrend Indicator** 📈
   - Widely used by Indian traders
   - Clear bullish/bearish signals
   - Works well in trending markets
   - Configurable period and multiplier

4. **ADX (Trend Strength)** 💪
   - Measures trend strength (0-100)
   - ADX > 25: Strong trend
   - ADX < 20: Weak/ranging market
   - Prevents false signals in sideways markets

5. **Sector-Specific Volatility Adjustments** 🏭
   - Different RSI thresholds per sector
   - Banking: 1.2x volatility
   - IT: 0.9x volatility
   - FMCG: 0.8x volatility (most stable)
   - Realty: 1.5x volatility (highest)
   - Auto, Metals, Energy: Adjusted accordingly

6. **Calendar Effects** 📅
   - **January-February**: Budget season volatility
   - **December**: Historically favorable (rally)
   - **March & September**: Unfavorable months
   - Automatic rating adjustments based on month

7. **Market Regime Detection** 🎯
   - Analyzes Nifty 50 to determine market phase
   - Bull Market: Price > SMA50 > SMA200
   - Bear Market: Price < SMA50 < SMA200
   - Sideways: Mixed signals
   - Adjusts stock ratings accordingly

8. **Enhanced Fundamental Scoring** 💎
   - **12-point scale** (upgraded from 8)
   - Core metrics (8 points):
     - ROE > 15%
     - Debt/Equity < 1
     - Revenue Growth > 10%
     - Profit Margins > 10%
   - Indian-specific metrics (4 points):
     - Promoter holding 40-70%
     - P/B ratio < 3
     - Dividend yield > 1%
     - Operating margins > 15%

9. **Relative Strength Analysis** 📊
   - Compare stock performance vs Nifty 50
   - Identifies outperformers/underperformers
   - 90-day rolling comparison
   - Helps select market leaders

10. **Liquidity Filters** 💧
    - Minimum volume: 1 lakh shares
    - Minimum value: ₹50 lakhs daily
    - Prevents illiquid stock recommendations

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/nteshxx/stockeye-cli.git
cd stockeye-cli

# Build using docker compose
docker compose up -d --build

# Run using bash shell
docker exec -it stockeye-cli bash
```

## 🚀 Quick Start

```bash
# Check version
stockeye --version
stockeye version

# Get help
stockeye --help
stockeye help
stockeye help analyze

# Add stocks to watchlist
stockeye watch add RELIANCE.NS TCS.NS INFY.NS HDFCBANK.NS

# Analyze watchlist
stockeye analyze

# Scan for opportunities
stockeye scan strong-buys

# Graham value analysis
stockeye mos analyze --min-mos 30
```

## 📊 Core Commands

### 1. Analysis Commands

```bash
# Basic analysis
stockeye analyze

# Detailed analysis (shows all indicators)
stockeye analyze --detailed
```

**Output includes:**
- Price vs DMA50/DMA200
- RSI with sector-adjusted thresholds
- MACD signals
- Volume analysis
- Bollinger Bands position
- Supertrend direction
- ADX trend strength
- Enhanced F-Score (0-12)
- Golden/Death Cross age
- India VIX context
- Market regime
- Final rating (7 levels)

### 2. Market Scanning

```bash
# Find STRONG BUY stocks
stockeye scan strong-buys --index NIFTY_500 --limit 20 --export

# Find fundamentally strong stocks
stockeye scan fundamentals --min-score 7 --export

# Find value opportunities (quality + dip)
stockeye scan value --index NIFTY_200

# Graham value screening
stockeye scan mos --min-mos 40 --conservative --export
```

### 3. Graham Value Analysis

```bash
# Analyze watchlist
stockeye mos analyze --min-mos 30 --conservative

# Quick analysis for single stock
stockeye mos inspect RELIANCE.NS
```

**Graham's Formula:**
```
Intrinsic Value = EPS × (8.5 + 2g)
Margin of Safety = (Intrinsic - Price) / Intrinsic × 100
```

### 4. Watchlist Management

```bash
# Add stocks
stockeye watch add SYMBOL1.NS SYMBOL2.NS

# Remove stocks
stockeye watch remove SYMBOL1.NS

# List watchlist
stockeye watch list

# Clear all
stockeye watch clear
```

## 🎯 Rating System

### 7-Level Rating Scale

1. **STRONG BUY 🟢🟢** - Exceptional opportunity
   - Fresh golden cross + strong fundamentals
   - Multiple bullish confirmations
   - High F-Score (≥6) + Strong technicals

2. **BUY 🟢** - Good entry point
   - Golden cross confirmation
   - Strong combined score (≥17)
   - Good fundamentals (≥5)

3. **ADD 🔵** - Good for adding to position
   - Quality stock on dip
   - Moderate golden cross
   - Decent combined score (≥14)

4. **HOLD 🟡** - Maintain position
   - Mixed signals
   - Moderate scores (11-13)
   - Wait for clearer direction

5. **REDUCE 🟠** - Consider reducing
   - Overbought conditions
   - Weakening momentum
   - Technical breakdown

6. **SELL 🔴** - Exit position
   - Recent death cross
   - Weak fundamentals + technicals
   - Bearish confirmations

7. **STRONG SELL 🔴🔴** - Urgent exit
   - Fresh death cross + bearish signals
   - Extreme overbought + weak fundamentals
   - Multiple bearish confirmations

## 📈 Technical Indicators

### Core Indicators
- **DMA 50/200**: Trend identification
- **RSI**: Momentum (overbought/oversold)
- **MACD**: Trend changes and momentum
- **Volume**: Confirmation indicator

### Enhanced Indicators (v2.0)
- **Bollinger Bands**: Volatility and price extremes
- **Supertrend**: Trend following
- **ADX**: Trend strength measurement
- **India VIX**: Market volatility context

## 💎 Fundamental Analysis

### Enhanced F-Score (0-12 points)

**Core Metrics (8 points):**
- ROE > 15% → +2
- Debt/Equity < 1 → +2
- Revenue Growth > 10% → +2
- Profit Margins > 10% → +2

**Indian Metrics (4 points):**
- Promoter Holding 40-70% → +1
- P/B Ratio < 3 → +1
- Dividend Yield > 1% → +1
- Operating Margins > 15% → +1

### Quality Score (0-10)
- Beta (volatility)
- Current Ratio (liquidity)
- Quick Ratio (short-term health)
- EBITDA Margins (profitability)
- P/E ratios (valuation)

### Growth Score (0-10)
- Revenue Growth
- Earnings Growth
- Book Value Growth
- Return on Assets

### Value Score (0-10)
- P/E Ratio
- P/B Ratio
- Dividend Yield
- PEG Ratio

## 🇮🇳 Indian Market Intelligence

### Sector Classifications
- Banking & Financial Services
- Information Technology
- Pharmaceuticals
- FMCG (Consumer Goods)
- Metals & Mining
- Automobile
- Real Estate
- Energy & Power
- Telecom

### Calendar Effects
- **Jan-Feb**: Budget volatility (conservative)
- **March**: Tax selling (unfavorable)
- **September**: Historically weak (unfavorable)
- **December**: Year-end rally (favorable)

### Market Regime Impact
- **Bull Market**: More aggressive on quality stocks
- **Bear Market**: More conservative, quality focus
- **Sideways**: Neutral, stock-specific

## 📊 Supported Indices

```
NIFTY_50           - Top 50 Indian stocks
NIFTY_100          - Top 100 stocks
NIFTY_200          - Top 200 stocks
NIFTY_500          - Top 500 stocks
NIFTY_NEXT_50      - Next 50 stocks
NIFTY_MIDCAP_100   - Top 100 Midcap
NIFTY_SMALLCAP_100 - Top 100 Smallcap
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Indicator periods
DMA_SHORT = 50
DMA_LONG = 200
RSI_PERIOD = 14
BB_PERIOD = 20
SUPERTREND_PERIOD = 10

# Indian market features
ENABLE_INDIA_VIX = True
ENABLE_CALENDAR_ADJUSTMENT = True
ENABLE_MARKET_REGIME = True
ENABLE_SECTOR_ADJUSTMENT = True

# Rating thresholds
STRONG_BUY_THRESHOLD = 20
BUY_THRESHOLD = 17
ADD_THRESHOLD = 14

# Liquidity filters
MIN_VOLUME_THRESHOLD = 100000
MIN_VALUE_THRESHOLD = 5000000
```

## 🔧 Advanced Features

### Null Safety
All functions include comprehensive null/NaN checking to prevent crashes.

### Error Handling
Graceful degradation when data is missing or API fails.

### Performance
- Parallel processing for bulk scanning
- Caching for frequently accessed data
- Rate limiting for API compliance

### Export Options
- Export scan results to watchlist
- JSON format for data persistence
- Future: CSV, Excel support

## 📖 Examples

### Example 1: Daily Watchlist Review
```bash
# Morning routine
stockeye watch list
stockeye analyze --detailed

# Check India VIX
# (automatically included in analysis)

# Review recommendations
# Focus on STRONG BUY / BUY ratings
```

### Example 2: Finding New Opportunities
```bash
# Scan for strong buys in Nifty 500
stockeye scan strong-buys --index NIFTY_500 --limit 30

# Add promising stocks to watchlist
stockeye watch add SYMBOL1.NS SYMBOL2.NS

# Run detailed analysis
stockeye analyze --detailed
```

### Example 3: Value Investing
```bash
# Find undervalued stocks with Graham method
stockeye scan mos --min-mos 40 --index NIFTY_500

# Quick check on specific stock
stockeye mos scan RELIANCE.NS

# Add value stocks to watchlist for monitoring
stockeye scan mos --min-mos 35 --export
```

### Example 4: Sector-Specific Scan
```bash
# Scan IT sector (lower volatility)
# Use NIFTY_IT index stocks

# Scan Banking sector (higher volatility)
# System automatically adjusts RSI thresholds

# Scan FMCG (most stable)
# Best for conservative investors
```

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```

2. **"No data available" for stock**
   - Check symbol format (NSE: .NS, BSE: .BO)
   - Verify stock is actively trading
   - Try different data period

3. **Slow scanning performance**
   - Reduce scan limit
   - Enable parallel processing in config
   - Check internet connection

4. **India VIX not loading**
   - Symbol: ^INDIAVIX
   - May not always be available
   - Analysis continues without it

## 📝 To-Do / Future Enhancements

- [ ] FII/DII flow data integration
- [ ] Real-time price alerts
- [ ] Backtesting framework
- [ ] Portfolio tracking
- [ ] Risk management tools
- [ ] Web dashboard
- [ ] Mobile app
- [ ] Email/SMS notifications
- [ ] Custom screening criteria
- [ ] Historical performance tracking

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 📄 License

MIT License - See LICENSE file

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Not financial advice. Always do your own research before investing. Past performance doesn't guarantee future results. The Indian stock market is subject to risks and volatility.

## 👥 Credits

- **Technical Indicators**: pandas_ta library
- **Data Source**: yfinance (Yahoo Finance)
- **CLI Framework**: typer
- **Display**: rich library

## 📞 Support

- Documentation: [GitHub Wiki]
- Issues: [GitHub Issues]
- Discussions: [GitHub Discussions]

---

**Made with ❤️ for Indian Stock Market Traders and Investors**

Version 2.0.0 | Last Updated: January 2026
