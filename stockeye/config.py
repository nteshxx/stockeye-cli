# Data Fetching Configuration
PERIOD = "1y"  # Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

# Moving Average Configuration
DMA_SHORT = 50
DMA_LONG = 200

# RSI Configuration
RSI_PERIOD = 14  # Standard RSI period
RSI_OVERSOLD = 30  # Oversold threshold
RSI_OVERBOUGHT = 70  # Overbought threshold

# MACD Configuration
MACD_FAST = 12  # Fast EMA period
MACD_SLOW = 26  # Slow EMA period
MACD_SIGNAL = 9  # Signal line period

# Volume Analysis Configuration
VOLUME_PERIOD = 20  # Period for volume moving average
VOLUME_HIGH_THRESHOLD = 1.5  # Volume ratio for "high" classification
VOLUME_LOW_THRESHOLD = 0.5  # Volume ratio for "low" classification

# Cross Detection Configuration
GOLDEN_CROSS_FRESH_DAYS = 60  # Days to consider golden cross "fresh"
DEATH_CROSS_FRESH_DAYS = 30  # Days to consider death cross "fresh"

# Storage Configuration
WATCHLIST_PATH = "data/watchlist.json"

# Display Configuration
SHOW_PROGRESS = True  # Show progress bar during analysis
COLOR_SCHEME = "rich"  # Terminal color scheme
