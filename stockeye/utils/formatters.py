def format_market_cap(market_cap):
    """Format market cap in billions/trillions"""
    if market_cap >= 1_000_000_000_000:  # Trillion
        return f"${market_cap / 1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:  # Billion
        return f"${market_cap / 1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:  # Million
        return f"${market_cap / 1_000_000:.2f}M"
    else:
        return f"${market_cap:,.0f}"

def format_rsi(rsi, rsi_signal):
    """Format RSI display"""
    if rsi is None or rsi_signal is None: return "N/A"
    if rsi_signal == "OVERSOLD": return f"[green bold]{rsi:.0f} ↓[/green bold]"
    elif rsi_signal == "OVERBOUGHT": return f"[red]{rsi:.0f} ↑[/red]"
    return f"[yellow]{rsi:.0f}[/yellow]"


def format_macd(macd_signal):
    if macd_signal == "BULLISH": return "[green]BULL[/green]"
    elif macd_signal == "BEARISH": return "[red]BEAR[/red]"
    return "[dim]-[/dim]"


def format_volume(volume_signal):
    if volume_signal == "HIGH": return "[green bold]HIGH[/green bold]"
    elif volume_signal == "LOW": return "[red]LOW[/red]"
    return "[dim]-[/dim]"


def format_time(seconds):
    """Format execution time in a human-readable way"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
