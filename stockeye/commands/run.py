from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from stockeye.services.analyzer import analyze_stock
from stockeye.services.data_fetcher import clear_expired_cache, fetch_stock
from stockeye.services.watchlist_manager import load_watchlist
from stockeye.config import PERIOD
from stockeye.core.rating import get_cross_display
from stockeye.core.indicators import fetch_india_vix, detect_market_regime
from stockeye.utils.formatters import format_macd, format_rsi, format_volume

console = Console()

def run(detailed=False):
    symbols = load_watchlist()
    symbols = sorted(symbols)

    clear_expired_cache()
    
    if not symbols:
        console.print(Panel.fit(
            "[yellow]Watchlist is empty![/yellow]\n\n"
            "Add symbols using:\n"
            "[cyan]stockeye watch add SYMBOL1 SYMBOL2[/cyan]",
            title="No Symbols to Analyze"
        ))
        return
    
    # 1. Fetch Market Context
    with console.status("[bold cyan]Fetching market context (VIX & Nifty Trend)..."):
        vix = fetch_india_vix()
        regime = "UNKNOWN"
        try:
            nifty_df, _ = fetch_stock("^NSEI", "1y")
            regime = detect_market_regime(nifty_df)
        except:
            pass
        
        context_msg = f"🇮🇳 India VIX: [bold]{vix:.2f}[/bold]" if vix else "VIX: N/A"
        context_msg += f" | Market: [bold]{regime}[/bold]"
        console.print(context_msg)

    # 2. Setup Table
    table = Table(
        title=f"📊 Advanced Stock Analysis", 
        show_header=True, 
        header_style="bold magenta",
        show_lines=True,
    )
    table.add_column("#", justify="right", style="dim")
    table.add_column("Stock", style="cyan bold", no_wrap=True)
    table.add_column("Sector", style="white dim", no_wrap=True) # New
    table.add_column("Price", justify="right")
    table.add_column("DMA50", justify="right", style="dim")
    table.add_column("DMA200", justify="right", style="dim")
    table.add_column("RSI", justify="center")
    table.add_column("MACD", justify="center")
    table.add_column("Vol", justify="center")
    table.add_column("BB", justify="center")
    table.add_column("ST", justify="center")
    table.add_column("ADX", justify="center")
    table.add_column("F-Score", justify="center")
    table.add_column("Cross", justify="left")
    table.add_column("Rating", justify="left", style="bold")

    results = []
    
    # 3. Analyze Symbols
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as progress:
        task = progress.add_task("[cyan]Analyzing stocks...", total=len(symbols))
        
        for symbol in symbols:
            try:
                df, info = fetch_stock(symbol, PERIOD)
                if df is None or info is None:
                    results.append({"symbol": symbol, "error": "not found"})
                    continue
                value_data = analyze_stock(symbol, df, info, vix, regime)
                results.append(value_data)
                progress.update(task, description=f"[cyan]Completed analyzing {symbol}...")
            except Exception as e:
                results.append({"symbol": symbol, "error": str(e)})
                progress.console.print(f"[bold red]Error[/bold red] analyzing {symbol}: {e}")
                
        progress.advance(task)
    
    # 4. Display Results
    for idx, res in enumerate(sorted(results, key=lambda x: x['symbol']), 1):
        sym = res['symbol']
        if res.get("error"):
            table.add_row(str(idx), sym, "-", "ERR", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "N/A")
            continue

        # Formatters
        price_color = "green" if res['price'] > res['dma50'] else "red"
        
        # Supertrend
        st_sig = res.get('supertrend_signal')
        st_disp = "[green]BULL[/green]" if st_sig == "BULLISH" else "[red]BEAR[/red]" if st_sig == "BEARISH" else "[dim]-[/dim]"

        # Bollinger Bands
        bb_sig = res.get('bb_signal')
        bb_disp = "[green]OS[/green]" if bb_sig == "OVERSOLD" else "[red]OB[/red]" if bb_sig == "OVERBOUGHT" else "[dim]-[/dim]"

        # ADX
        adx_sig = res.get('adx_signal')
        adx_disp = "[bold green]STR[/bold green]" if adx_sig == "STRONG_TREND" else "[dim]WEAK[/dim]" if adx_sig == "WEAK_TREND" else "[yellow]MOD[/yellow]"

        # F-Score
        fscore = res['fscore']
        f_color = "green" if fscore >= 8 else "yellow" if fscore >= 5 else "red"
        
        table.add_row(
            str(idx),
            sym,
            res.get('sector', 'Other'),
            f"[{price_color}]{res['price']:.2f}[/{price_color}]",
            f"{res['dma50']:.0f}" if res['dma50'] else "-",
            f"{res['dma200']:.0f}" if res['dma200'] else "-",
            format_rsi(res['rsi'], res['rsi_signal']),
            format_macd(res['macd_signal']),
            format_volume(res['volume_signal']),
            bb_disp,
            st_disp,
            adx_disp,
            f"[{f_color}]{fscore}[/{f_color}]/12",
            get_cross_display(res['cross_info']),
            res['rating']
        )

    console.print()
    console.print(table)
    console.print()
    
    # 5. Legend
    console.print(Panel(
        "[bold]Key Metrics:[/bold]\n\n"
        "• [bold]BB (Bollinger):[/bold] [green]OS[/green]=Oversold(Buy) | [red]OB[/red]=Overbought(Sell)\n"
        "• [bold]ST (Supertrend):[/bold] [green]BULL[/green]=Uptrend | [red]BEAR[/red]=Downtrend\n"
        "• [bold]ADX (Strength):[/bold] [green]STR[/green]=Strong Trend (>25) | [yellow]MOD[/yellow]=Moderate | [dim]WEAK[/dim]=<20\n"
        "• [bold]F-Score:[/bold] Fundamental Score out of 12 (Quality & Stability)\n\n"
        "[bold]Ratings:[/bold] "
        "[green]STRONG BUY[/green] | [green]BUY[/green] | [blue]ADD[/blue] | "
        "[yellow]HOLD[/yellow] | [orange]REDUCE[/orange] | [red]SELL[/red]",
        title="📖 Legend", border_style="dim"
    ))
