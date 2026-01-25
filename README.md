# 🚀 StockEye

## ✨ Key Features

### 📊 Advanced Technical Indicators
* ✅ **DMA 50 & 200** - Moving average trends
* ✅ **RSI (Relative Strength Index)** - Overbought/oversold detection
* ✅ **MACD** - Momentum and trend direction
* ✅ **Volume Analysis** - Trading volume vs 20-day average
* ✅ **Golden/Death Cross** - Crossover detection with age tracking

### 💰 Fundamental Analysis
* ✅ **ROE** (Return on Equity)
* ✅ **D/E Ratio** (Debt to Equity)
* ✅ **Revenue Growth**
* ✅ **Profit Margins**
* ✅ **Composite F-Score** (0-8 scale)

### 🎯 7-Level Rating System
| Rating | Description |
|------------|-------------|
| **STRONG BUY 🟢** | Exceptional entry opportunity |
| **BUY 🟢** | Good entry point |
| **ADD 🔵** | Good for adding to existing position |
| **HOLD 🟡** | Maintain current position |
| **PARTIAL EXIT 🟠** | Consider reducing position by 25-50% |
| **EXIT 🔴** | Exit position completely |
| **STRONG SELL 🔴** | Urgent exit recommended |

### 🔍 Market Scanner
* ✅ **Scan for STRONG BUY stocks** - Top opportunities across market
* ✅ **Scan for fundamentally strong stocks** - High F-Score companies
* ✅ **Scan for value opportunities** - Strong fundamentals, temporarily weak price
* ✅ **Multiple stock universes** - NIFTY 50, NIFTY Next 50, US Mega Caps

### 🌍 Multi-Market Support
* ✅ **Indian Market** - NSE/BSE (NIFTY 50, NIFTY Next 50)
* ✅ **US Market** - NYSE/NASDAQ (Mega Caps)
* ✅ **Global Markets** - UK, Hong Kong, Japan, and more

### 📊 Rating Algorithm

**Scoring System:**
```
Combined Score = (Fundamental Score × 1.5) + Technical Score

Technical Score (0-10):
- DMA Alignment: 0-3 points
- RSI Position: 0-2 points
- MACD Signal: 0-2 points
- Volume: 0-3 points (increased from 2!)

Fundamental Score (0-8):
- ROE > 15%: +2
- D/E < 1: +2
- Revenue Growth > 10%: +2
- Profit Margins > 10%: +2
```

**Special Override Conditions:**

| Condition | Rating | Priority |
|-----------|--------|----------|
| Fresh Death Cross (<15d) + Bearish + High Volume | STRONG SELL 🔴 | Highest |
| RSI >75 + MACD Bearish + F-Score <5 | STRONG SELL 🔴 | Highest |
| Golden Cross (<10d) + F-Score ≥6 + MACD Bullish + High Vol | STRONG BUY 🟢 | Highest |
| RSI <25 + MACD Bullish + F-Score ≥6 | STRONG BUY 🟢 | High |
| RSI >70 + MACD Neutral/Bearish | PARTIAL EXIT 🟠 | Medium |
| F-Score ≥6 + RSI Oversold | ADD 🔵 | Medium |

---

## 📁 Project Structure

```
stockeye-cli/
│
├── stockeye/
│   ├── __init__.py
│   ├── cli.py                    # Main CLI entry (Typer)
│   ├── config.py                 # Configuration
│   ├── storage.py                # Watchlist management
│   │
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── scan.py               # Scan commands
│   │   ├── watch.py              # Watchlist commands
│   │   └── run.py                # Analysis execution
│   │
│   └── core/
│       ├── __init__.py
│       ├── data_fetcher.py       # Yahoo Finance API
│       ├── indicators.py         # Technical indicators
│       ├── fundamentals.py       # Fundamental scoring
│       └── rating.py             # Rating algorithm
│
├── data/
│   └── watchlist.json            # Persistent storage
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 📊 Indicator Guide

### RSI (Relative Strength Index)
Measures momentum on a 0-100 scale:
- **< 30**: Oversold (potential buy opportunity)
- **30-70**: Neutral zone
- **> 70**: Overbought (potential sell signal)

### MACD (Moving Average Convergence Divergence)
Shows trend direction and momentum:
- **BULLISH**: MACD line > Signal line, positive histogram
- **BEARISH**: MACD line < Signal line, negative histogram
- **NEUTRAL**: Crossing or flat

### Volume Analysis
Compares current volume to 20-day average:
- **HIGH**: > 1.5x average (strong conviction)
- **NORMAL**: 0.5x - 1.5x average
- **LOW**: < 0.5x average (weak participation)

### Golden/Death Cross
Long-term trend indicators:
- **Golden Cross**: DMA50 crosses above DMA200 (bullish)
- **Death Cross**: DMA50 crosses below DMA200 (bearish)
- **Age**: Days since last cross (fresher = stronger signal)

### Special Conditions (Override Rules)

**Immediate STRONG SELL:**
- Death cross ≤15 days + MACD bearish + High volume
- RSI >75 + MACD bearish + F-Score <5

**Immediate STRONG BUY:**
- Golden cross ≤10 days + F-Score ≥6 + MACD bullish + High volume
- RSI <25 + MACD turning bullish + F-Score ≥6

**Oversold Bounce (BUY):**
- RSI <30 + MACD bullish + F-Score ≥4

**Overbought Warning (PARTIAL EXIT):**
- RSI >70 + MACD neutral/bearish + Volume declining

---

## 🐳 Docker Setup

### 1. Build the Container

```bash
docker compose up -d --build
```

### 2. Manage Watchlist

```bash
# Open docker shell
docker exec -it stockeye-cli sh

# Add stocks to watchlist
stockeye watch add RELIANCE.NS HDFCBANK.NS TCS.NS INFY.NS

# View watchlist
stockeye watch list

# Remove stocks
stockeye watch remove INFY.NS

# Clear entire watchlist
stockeye watch clear
```

### 3. Run Analysis

```bash
# Analyze all stocks in watchlist
stockeye analyze
```

### 4. Market Scanners

```bash
# Basic usage (scans NIFTY 50)
stockeye scan strong-buys

# Scan all Indian stocks
stockeye scan strong-buys --universe ALL_INDIAN

# Scan US market
stockeye scan strong-buys --universe NIFTY50

# Limit results to top 25
stockeye scan strong-buys --limit 25

# Export directly to watchlist
stockeye0 scan strong-buys --export
```

---

## 📝 Configuration

Edit `app/config.py` to customize:

```python
PERIOD = "1y"          # Data fetch period
DMA_SHORT = 50         # Short-term moving average
DMA_LONG = 200         # Long-term moving average
```

---

## 📊 Trading Signal Scenarios & Examples

This document explains how different indicator combinations translate into BUY/HOLD/SELL signals.

---

### 🟢 Strong BUY Scenarios

#### Scenario 1: Fresh Golden Cross with Strong Fundamentals
```
Stock: RELIANCE.NS
Price: ₹2,845 (above DMA50 and DMA200)
DMA50: ₹2,789 | DMA200: ₹2,650
RSI: 58.3 (Neutral zone - healthy)
MACD: BULLISH ↑ (positive momentum)
Volume: HIGH 📈 (strong conviction)
F-Score: 6/8 (strong fundamentals)
Cross: Golden Cross 🟢 (23 days ago)

Rating: BUY 🟢

Why: Fresh golden cross + strong fundamentals + bullish momentum + high volume = very strong buy signal
```

#### Scenario 2: Oversold Bounce with Improving Momentum
```
Stock: TCS.NS
Price: ₹3,850
RSI: 28.4 ↓ (oversold territory)
MACD: BULLISH ↑ (turning positive)
Volume: HIGH 📈
F-Score: 5/8
Cross: N/A

Rating: BUY 🟢

Why: RSI oversold + MACD turning bullish + decent fundamentals = potential reversal buy
```

#### Scenario 3: Established Uptrend with All Indicators Aligned
```
Stock: INFY.NS
Price: ₹1,650 (Price > DMA50 > DMA200)
RSI: 55.2 (healthy neutral)
MACD: BULLISH ↑
Volume: NORMAL
F-Score: 7/8
Cross: Golden Cross 🟢 (45 days ago)

Rating: BUY 🟢

Why: Perfect technical alignment + excellent fundamentals = strong uptrend
```

---

### 🟡 HOLD Scenarios

#### Scenario 1: Mixed Signals - Good Fundamentals, Weak Technicals
```
Stock: HDFCBANK.NS
Price: ₹1,680 (below DMA50)
DMA50: ₹1,695 | DMA200: ₹1,650
RSI: 52.1 (neutral)
MACD: NEUTRAL
Volume: NORMAL
F-Score: 6/8
Cross: N/A

Rating: HOLD 🟡

Why: Strong fundamentals but weak technical setup - wait for confirmation
```

#### Scenario 2: Old Golden Cross, Weakening Momentum
```
Stock: WIPRO.NS
Price: ₹580
RSI: 48.5
MACD: NEUTRAL
Volume: LOW 📉
F-Score: 5/8
Cross: Golden Cross 🟢 (120 days ago)

Rating: HOLD 🟡

Why: Old cross signal + weakening volume + neutral momentum = maintain position
```

#### Scenario 3: Consolidation Phase
```
Stock: BAJFINANCE.NS
Price: ₹7,250 (between DMAs)
DMA50: ₹7,200 | DMA200: ₹7,300
RSI: 50.0 (perfectly neutral)
MACD: NEUTRAL
Volume: NORMAL
F-Score: 4/8

Rating: HOLD 🟡

Why: All indicators neutral, price consolidating - wait for direction
```

---

### 🔴 SELL Scenarios

#### Scenario 1: Fresh Death Cross
```
Stock: YESBANK.NS
Price: ₹18.50
DMA50: ₹19.20 | DMA200: ₹18.80
RSI: 45.2
MACD: BEARISH ↓
Volume: HIGH 📈
F-Score: 2/8
Cross: Death Cross 🔴 (12 days ago)

Rating: SELL 🔴

Why: Recent death cross + weak fundamentals + bearish momentum = strong sell
```

#### Scenario 2: Overbought with Bearish Divergence
```
Stock: ADANIPORTS.NS
Price: ₹1,280
RSI: 76.8 ↑ (overbought)
MACD: BEARISH ↓ (divergence - price up but MACD down)
Volume: HIGH 📈
F-Score: 3/8
Cross: N/A

Rating: SELL 🔴

Why: Extreme overbought + bearish divergence + weak fundamentals = take profits
```

#### Scenario 3: Broken Support with Poor Fundamentals
```
Stock: VODAFONEIDEA.NS
Price: ₹12.30 (below both DMAs)
DMA50: ₹13.50 | DMA200: ₹14.20
RSI: 25.1 ↓ (oversold but still falling)
MACD: BEARISH ↓
Volume: HIGH 📈 (selling pressure)
F-Score: 1/8
Cross: Death Cross 🔴 (8 days ago)

Rating: SELL 🔴

Why: All indicators bearish + fundamentally weak = exit position
```

---

### 📈 Real Trading Examples

#### Example 1: Perfect Setup Trade
```
Initial Signal (Day 0):
- Stock: RELIANCE.NS @ ₹2,600
- Golden Cross detected (0 days ago)
- RSI: 45 (coming from oversold)
- MACD: Just turned bullish
- F-Score: 7/8
- Rating: BUY 🟢

After 30 Days:
- Price: ₹2,845 (+9.4% gain)
- RSI: 58 (healthy)
- MACD: Strongly bullish
- Still in uptrend
- Rating: BUY 🟢 → Continue holding

After 60 Days:
- Price: ₹2,920 (+12.3% total gain)
- RSI: 72 (overbought warning)
- MACD: Still bullish but flattening
- Rating: HOLD 🟡 → Consider taking partial profits
```

#### Example 2: Avoided Loss
```
Initial Analysis:
- Stock: BANKXYZ @ ₹850
- Death Cross 🔴 (5 days ago)
- RSI: 55 (still neutral)
- MACD: Bearish
- F-Score: 3/8
- Rating: SELL 🔴

Action: Did not buy / Sold existing position

After 45 Days:
- Price dropped to ₹720 (-15.3%)
- Saved significant loss by following the signal
```

---

## 🎯 Signal Strength Matrix

| Scenario | RSI | MACD | Volume | F-Score | Cross | Rating | Confidence |
|----------|-----|------|--------|---------|-------|--------|------------|
| Perfect Storm | <30 | BULL | HIGH | 7-8 | Golden (fresh) | BUY 🟢 | ⭐⭐⭐⭐⭐ |
| Strong Setup | 30-50 | BULL | HIGH | 6-8 | Golden | BUY 🟢 | ⭐⭐⭐⭐ |
| Decent Entry | 40-60 | BULL | NORM | 5-6 | N/A | BUY 🟢 | ⭐⭐⭐ |
| Neutral | 50-60 | NEUT | NORM | 4-5 | Old cross | HOLD 🟡 | ⭐⭐ |
| Weak | 60-70 | NEUT | LOW | 3-4 | N/A | HOLD 🟡 | ⭐⭐ |
| Warning | >70 | BEAR | HIGH | <3 | N/A | SELL 🔴 | ⭐⭐⭐ |
| Danger | Any | BEAR | HIGH | <3 | Death (fresh) | SELL 🔴 | ⭐⭐⭐⭐⭐ |

---

## 💡 Pro Tips

### 1. Confirmation is Key
Don't rely on a single indicator. The best signals have:
- ✅ 3+ indicators aligned
- ✅ Volume confirmation
- ✅ Fundamental support
- ✅ Clear trend direction

### 2. Time Your Entries
**Best BUY times:**
- RSI 30-40 (recovering from oversold)
- MACD histogram growing positive
- Volume picking up
- Fresh golden cross (0-30 days)

**Best SELL times:**
- RSI 70-80 (overbought)
- MACD histogram shrinking or negative
- Volume declining on rallies
- Fresh death cross (0-15 days)

### 3. Risk Management
- Never go all-in on one signal
- Use stop losses (8-10% below entry)
- Take partial profits at resistance
- Don't fight fresh death crosses

### 4. False Signals
Watch out for:
- Whipsaws in choppy markets (DMAs crossing back and forth)
- Low volume crosses (less reliable)
- Extreme news events (override technicals temporarily)
- Divergences (price vs indicators moving opposite)

---

**Note:** Always do your own analysis.

**Remember:** This tool provides signals, not guarantees. Always use proper risk management and never invest more than you can afford to lose.

---

## 📄 License

MIT License - Feel free to modify and distribute

---

## 🙏 Credits

Built with:
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance data
- [pandas-ta](https://github.com/twopirllc/pandas-ta) - Technical indicators
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Typer](https://github.com/tiangolo/typer) - Modern CLI framework