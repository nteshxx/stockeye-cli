# StockEye Configuration - Indian Market Optimized
# Version 2.0.0

# ==================== DATA FETCHING ====================
PERIOD = "1y"  # Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

# ==================== MOVING AVERAGES ====================
DMA_SHORT = 50
DMA_LONG = 200

# ==================== RSI CONFIGURATION ====================
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Sector-adjusted RSI thresholds (multipliers applied based on sector volatility)
RSI_SECTOR_ADJUSTMENT = True

# ==================== MACD CONFIGURATION ====================
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# ==================== BOLLINGER BANDS (Indian Market) ====================
BB_PERIOD = 20
BB_STD_DEV = 2

# ==================== SUPERTREND (Popular in India) ====================
SUPERTREND_PERIOD = 10
SUPERTREND_MULTIPLIER = 3

# ==================== ADX (Trend Strength) ====================
ADX_PERIOD = 14
ADX_STRONG_THRESHOLD = 25  # ADX > 25 = strong trend
ADX_WEAK_THRESHOLD = 20    # ADX < 20 = weak trend

# ==================== VOLUME ANALYSIS ====================
VOLUME_PERIOD = 20
VOLUME_HIGH_THRESHOLD = 1.5  # 1.5x average = high volume
VOLUME_LOW_THRESHOLD = 0.5   # 0.5x average = low volume

# ==================== CROSS DETECTION ====================
GOLDEN_CROSS_FRESH_DAYS = 60
DEATH_CROSS_FRESH_DAYS = 30

# ==================== FUNDAMENTAL SCORING ====================
MIN_FSCORE_QUALITY = 6               # Minimum for quality stocks
MIN_FSCORE_GROWTH = 5                # Minimum for growth stocks

# ==================== INDIAN MARKET SPECIFIC ====================

# India VIX thresholds
INDIA_VIX_LOW = 15      # Below this = low volatility
INDIA_VIX_HIGH = 20     # Above this = high volatility
INDIA_VIX_EXTREME = 25  # Above this = extreme fear

# Sector volatility multipliers
SECTOR_VOLATILITY = {
    "BANKING": 1.2,
    "IT": 0.9,
    "PHARMA": 1.1,
    "FMCG": 0.8,
    "METALS": 1.4,
    "AUTO": 1.3,
    "REALTY": 1.5,
    "ENERGY": 1.2,
    "TELECOM": 1.1,
    "OTHER": 1.0
}

# Calendar effects
ENABLE_CALENDAR_ADJUSTMENT = True
BUDGET_MONTHS = [1, 2]           # January-February (volatile)
FAVORABLE_MONTHS = [12]          # December (rally)
UNFAVORABLE_MONTHS = [3, 9]      # March, September

# Market regime detection
ENABLE_MARKET_REGIME = True
NIFTY_SYMBOL = "^NSEI"  # Nifty 50 index

# Liquidity filters
MIN_VOLUME_THRESHOLD = 100000    # 1 lakh shares
MIN_VALUE_THRESHOLD = 5000000    # Rs 50 lakhs daily turnover

# ==================== MARGIN OF SAFETY (Graham) ====================
GRAHAM_MIN_MOS = 30              # Minimum 30% margin recommended
GRAHAM_CONSERVATIVE_GROWTH = 15  # Cap growth at 15% for conservative
GRAHAM_MAX_GROWTH = 25           # Cap growth at 25% for standard

# ==================== RATING SYSTEM ====================
# Enhanced multi-indicator system
ENABLE_BOLLINGER_BANDS = True
ENABLE_SUPERTREND = True
ENABLE_ADX = True
ENABLE_INDIA_VIX = True

# Rating weights
FUNDAMENTAL_WEIGHT = 1.5
TECHNICAL_WEIGHT = 1.0

# Combined score thresholds (with enhanced scoring 0-27)
STRONG_BUY_THRESHOLD = 20
BUY_THRESHOLD = 17
ADD_THRESHOLD = 14
HOLD_THRESHOLD = 11
REDUCE_THRESHOLD = 9
SELL_THRESHOLD = 7

# ==================== STORAGE ====================
WATCHLIST_FILE = "/app/data/watchlist.json"

# ==================== DISPLAY ====================
SHOW_PROGRESS = True
COLOR_SCHEME = "rich"
COMPACT_MODE = False

# Table display
MAX_COMPANY_NAME_LENGTH = 25
SHOW_MARKET_CAP = True
SHOW_SECTOR = True

# ==================== PERFORMANCE ====================
# Parallel processing for scanning
ENABLE_PARALLEL_PROCESSING = True
MAX_WORKERS = 8  # Concurrent API calls

# Rate limiting
API_DELAY_SECONDS = 0.5  # Delay between API calls
MAX_RETRIES = 3

# ==================== INDICES ====================
AVAILABLE_INDICES = [
    "NIFTY_50",
    "NIFTY_100",
    "NIFTY_200",
    "NIFTY_500",
    "NIFTY_NEXT_50",
    "NIFTY_MIDCAP_100",
    "NIFTY_SMALLCAP_100",
]

DEFAULT_INDEX = "NIFTY_50"

# ==================== EXPORT/IMPORT ====================
EXPORT_FORMAT = "json"  # json, csv, excel
AUTO_BACKUP_WATCHLIST = True
BACKUP_INTERVAL_DAYS = 7

# ==================== LOGGING ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "stockeye.log"
LOG_TO_FILE = False

# ==================== NOTIFICATIONS ====================
# Future feature placeholders
ENABLE_ALERTS = False
ALERT_ON_STRONG_BUY = False
ALERT_ON_DEATH_CROSS = False

# ==================== API CONFIGURATION ====================
# Yahoo Finance specific
YFINANCE_TIMEOUT = 10  # seconds
YFINANCE_THREADS = True

# ==================== VERSION ====================
VERSION = "2.0.0"
APP_NAME = "StockEye"

# ==================== FEATURE FLAGS ====================
FEATURES = {
    "india_vix": True,
    "bollinger_bands": True,
    "supertrend": True,
    "adx": True,
    "calendar_effects": True,
    "sector_adjustment": True,
    "market_regime": True,
    "relative_strength": True,
    "liquidity_filter": True,
    "enhanced_fundamental": True,
}

# ==================== HELP URLS ====================
DOCUMENTATION_URL = "https://github.com/nteshxx/stockeye-cli"
ISSUE_TRACKER_URL = "https://github.com/nteshxx/stockeye-cli/issues"
