import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from stockeye.core.scanner import (
    scan_for_strong_buys,
    scan_for_fundamentally_strong,
    scan_for_value_opportunities,
    get_stock_universe
)
from stockeye.core.rating import get_cross_display

scan_app = typer.Typer(help="Scan markets for opportunities (strong-buys/fundamentals/value)")
console = Console()

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


def format_rsi_compact(rsi, rsi_signal):
    """Compact RSI display"""
    if rsi is None:
        return "N/A"
    
    if rsi_signal == "OVERSOLD":
        return f"[green]{rsi:.0f}↓[/green]"
    elif rsi_signal == "OVERBOUGHT":
        return f"[red]{rsi:.0f}↑[/red]"
    else:
        return f"{rsi:.0f}"


def format_macd_compact(macd_signal):
    """Compact MACD display"""
    if macd_signal == "BULLISH":
        return "[green]↑[/green]"
    elif macd_signal == "BEARISH":
        return "[red]↓[/red]"
    else:
        return "→"


@scan_app.command("strong-buys")
def strong_buys(
    universe: str = typer.Option("NIFTY50", "--universe", "-u", help="Stock universe (NIFTY50, ALL_INDIAN, US_MEGA_CAPS)"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum results to show"),
    export: bool = typer.Option(False, "--export", "-e", help="Export to watchlist")
):
    """
    Scan for top STRONG BUY stocks across market
    
    Finds stocks with:
    - STRONG BUY or BUY ratings
    - Strong technical + fundamental alignment
    - Fresh golden crosses
    - Oversold bounces with momentum
    """
    console.print(Panel.fit(
        f"[cyan]Scanning {universe} universe for STRONG BUY opportunities...[/cyan]",
        title="🔍 Market Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Analyzing stocks...", total=100)
        
        results = scan_for_strong_buys(universe, limit)
        progress.update(task, completed=100)
    
    if not results:
        console.print("[yellow]No STRONG BUY stocks found in current market conditions[/yellow]")
        return
    
    # Create results table
    table = Table(
        title=f"🟢 Top {len(results)} STRONG BUY Stocks from {universe}",
        show_header=True,
        header_style="bold green"
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan", no_wrap=True)
    table.add_column("Company", style="dim", max_width=25)
    table.add_column("Price", justify="right", style="green")
    table.add_column("F-Score", justify="center")
    table.add_column("RSI", justify="center")
    table.add_column("MACD", justify="center")
    table.add_column("Cross", justify="left", max_width=20)
    table.add_column("Rating", justify="center", style="bold")
    table.add_column("Mkt Cap", justify="right", style="dim")
    
    for idx, stock in enumerate(results, 1):
        cross_display = get_cross_display(stock["cross_info"])
        
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"],
            f"{stock['price']:.2f}",
            str(stock["fscore"]),
            format_rsi_compact(stock["rsi"], stock["rsi_signal"]),
            format_macd_compact(stock["macd_signal"]),
            cross_display,
            stock["rating"],
            format_market_cap(stock["market_cap"])
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Summary stats
    strong_buy_count = sum(1 for s in results if "STRONG BUY" in s["rating"])
    buy_count = sum(1 for s in results if s["rating"] == "BUY 🟢")
    avg_fscore = sum(s["fscore"] for s in results) / len(results)
    
    summary = Panel(
        f"[green]STRONG BUY:[/green] {strong_buy_count} stocks\n"
        f"[cyan]BUY:[/cyan] {buy_count} stocks\n"
        f"[yellow]Average F-Score:[/yellow] {avg_fscore:.1f}/8",
        title="📊 Summary",
        border_style="green"
    )
    console.print(summary)
    
    # Export option
    if export:
        from storage import add_symbols
        symbols = [s["symbol"] for s in results]
        added = add_symbols(symbols)
        console.print(f"\n[green]✓[/green] Added {len(added)} symbols to watchlist")


@scan_app.command("fundamentals")
def fundamentals(
    universe: str = typer.Option("NIFTY50", "--universe", "-u", help="Stock universe"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum results"),
    min_score: int = typer.Option(5, "--min-score", "-m", help="Minimum F-Score"),
    export: bool = typer.Option(False, "--export", "-e", help="Export to watchlist")
):
    """
    Scan for fundamentally strong stocks (high F-Score)
    
    Finds stocks with:
    - High ROE (>15%)
    - Low Debt/Equity (<1)
    - Strong Revenue Growth (>10%)
    - Good Profit Margins (>10%)
    """
    console.print(Panel.fit(
        f"[cyan]Scanning {universe} for fundamentally strong stocks (F-Score ≥ {min_score})...[/cyan]",
        title="💎 Fundamental Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Analyzing fundamentals...", total=100)
        
        results = scan_for_fundamentally_strong(universe, limit)
        progress.update(task, completed=100)
    
    # Filter by minimum score
    results = [r for r in results if r["fscore"] >= min_score]
    
    if not results:
        console.print(f"[yellow]No stocks found with F-Score ≥ {min_score}[/yellow]")
        return
    
    # Create results table
    table = Table(
        title=f"💎 Top {len(results)} Fundamentally Strong Stocks (F-Score ≥ {min_score})",
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan", no_wrap=True)
    table.add_column("Company", style="dim", max_width=25)
    table.add_column("F-Score", justify="center", style="bold green")
    table.add_column("Price", justify="right")
    table.add_column("RSI", justify="center")
    table.add_column("MACD", justify="center")
    table.add_column("Rating", justify="center")
    table.add_column("Mkt Cap", justify="right", style="dim")
    
    for idx, stock in enumerate(results, 1):
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"],
            f"{stock['fscore']}/8",
            f"{stock['price']:.2f}",
            format_rsi_compact(stock["rsi"], stock["rsi_signal"]),
            format_macd_compact(stock["macd_signal"]),
            stock["rating"],
            format_market_cap(stock["market_cap"])
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Summary
    perfect_score = sum(1 for s in results if s["fscore"] == 8)
    excellent_score = sum(1 for s in results if s["fscore"] >= 7)
    avg_fscore = sum(s["fscore"] for s in results) / len(results)
    
    summary = Panel(
        f"[green]Perfect Score (8/8):[/green] {perfect_score} stocks\n"
        f"[cyan]Excellent (≥7/8):[/cyan] {excellent_score} stocks\n"
        f"[yellow]Average F-Score:[/yellow] {avg_fscore:.1f}/8",
        title="📊 Fundamental Quality",
        border_style="magenta"
    )
    console.print(summary)
    
    if export:
        from storage import add_symbols
        symbols = [s["symbol"] for s in results]
        added = add_symbols(symbols)
        console.print(f"\n[green]✓[/green] Added {len(added)} symbols to watchlist")


@scan_app.command("value")
def value_opportunities(
    universe: str = typer.Option("NIFTY50", "--universe", "-u", help="Stock universe"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum results"),
    export: bool = typer.Option(False, "--export", "-e", help="Export to watchlist")
):
    """
    Scan for value opportunities
    
    Finds stocks with:
    - Strong fundamentals (F-Score ≥ 6)
    - Temporarily weak prices (oversold or ADD ratings)
    - Potential mean reversion opportunities
    """
    console.print(Panel.fit(
        f"[cyan]Scanning {universe} for value opportunities...[/cyan]",
        title="💰 Value Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Finding value stocks...", total=100)
        
        results = scan_for_value_opportunities(universe, limit)
        progress.update(task, completed=100)
    
    if not results:
        console.print("[yellow]No value opportunities found[/yellow]")
        return
    
    # Create results table
    table = Table(
        title=f"💰 Top {len(results)} Value Opportunities",
        show_header=True,
        header_style="bold blue"
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan")
    table.add_column("Company", style="dim", max_width=25)
    table.add_column("F-Score", justify="center", style="bold")
    table.add_column("Price", justify="right")
    table.add_column("RSI", justify="center")
    table.add_column("Rating", justify="center")
    table.add_column("Mkt Cap", justify="right", style="dim")
    
    for idx, stock in enumerate(results, 1):
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"],
            f"{stock['fscore']}/8",
            f"{stock['price']:.2f}",
            format_rsi_compact(stock["rsi"], stock["rsi_signal"]),
            stock["rating"],
            format_market_cap(stock["market_cap"])
        )
    
    console.print()
    console.print(table)
    console.print()
    
    console.print(Panel(
        "[yellow]Value stocks are fundamentally strong but temporarily weak.[/yellow]\n"
        "These represent potential buy-the-dip opportunities.\n"
        "Always do your own research before investing!",
        title="💡 Value Investing Note",
        border_style="blue"
    ))
    
    if export:
        from storage import add_symbols
        symbols = [s["symbol"] for s in results]
        added = add_symbols(symbols)
        console.print(f"\n[green]✓[/green] Added {len(added)} symbols to watchlist")
