import typer
import time

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from stockeye.core.rating import get_cross_display
from stockeye.services.watchlist_manager import add_symbols
from stockeye.scanners.graham_value_scanner import scan_for_graham_value
from stockeye.scanners.strong_buys_scanner import scan_for_strong_buys
from stockeye.scanners.strong_fundamental_scanner import scan_for_fundamentally_strong
from stockeye.utils.formatters import format_macd, format_market_cap, format_rsi, format_time

scan_app = typer.Typer(help="🔍 Scan markets for opportunities")
console = Console()


@scan_app.command("strong-buys")
def strong_buys(
    index: str = typer.Option("NIFTY_50", "--index", "-i", help="Stock index (NIFTY_50, NIFTY_500, NIFTY_NEXT_50)"),
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
    start_time = time.time()
    
    console.print(Panel.fit(
        f"[cyan]Scanning {index} index for STRONG BUY opportunities...[/cyan]",
        title="🔍 Market Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Analyzing stocks...", total=100)
        
        results = scan_for_strong_buys(index, limit)
        progress.update(task, completed=100)
    
    scan_time = time.time() - start_time
    
    if not results:
        console.print("[yellow]No STRONG BUY stocks found in current market conditions[/yellow]")
        console.print(f"\n[dim]⏱️  Scan completed in {format_time(scan_time)}[/dim]")
        return
    
    # Create results table
    table = Table(
        title=f"🟢 Top {len(results)} STRONG BUY Stocks from {index}",
        show_header=True,
        header_style="bold green",
        show_lines=True,
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan", no_wrap=True)
    table.add_column("Company", style="dim", max_width=25)
    table.add_column("Price", justify="right", style="green")
    table.add_column("F-Score", justify="center")
    table.add_column("RSI", justify="center")
    table.add_column("MACD", justify="center")
    table.add_column("Cross", justify="left", max_width=20)
    table.add_column("Rating", justify="left", style="bold")
    table.add_column("Mkt Cap", justify="right", style="dim")
    
    for idx, stock in enumerate(results, 1):
        cross_display = get_cross_display(stock["cross_info"])
        
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"],
            f"{stock['price']:.2f}",
            f"{stock['fscore']}/12",
            format_rsi(stock["rsi"], stock["rsi_signal"]),
            format_macd(stock["macd_signal"]),
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
    
    summary = Panel(
        f"[green]STRONG BUY:[/green] {strong_buy_count} stocks\n"
        f"[cyan]BUY:[/cyan] {buy_count} stocks\n\n"
        f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]",
        title="📊 Summary",
        border_style="green"
    )
    console.print(summary)
    
    if export:
        symbols = [s["symbol"] for s in results]
        added = add_symbols(symbols)
        console.print(f"\n[green]✓[/green] Added {len(added)} symbols to watchlist")


@scan_app.command("strong-fundamentals")
def fundamentals(
    index: str = typer.Option("NIFTY_50", "--index", "-i", help="Stock index"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum results"),
    min_score: int = typer.Option(9, "--min-score", "-m", help="Minimum F-Score"),
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
    start_time = time.time()
    
    console.print(Panel.fit(
        f"[cyan]Scanning {index} for fundamentally strong stocks (F-Score ≥ {min_score})...[/cyan]",
        title="💎 Fundamental Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Analyzing fundamentals...", total=100)
        
        results = scan_for_fundamentally_strong(index, limit)
        progress.update(task, completed=100)
    
    scan_time = time.time() - start_time
    
    # Filter by minimum score
    results = [r for r in results if r["fscore"] >= min_score]
    
    if not results:
        console.print(f"[yellow]No stocks found with F-Score ≥ {min_score}[/yellow]")
        console.print(f"\n[dim]⏱️  Scan completed in {format_time(scan_time)}[/dim]")
        return
    
    # Create results table
    table = Table(
        title=f"💎 Top {len(results)} Fundamentally Strong Stocks (F-Score ≥ {min_score})",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan", no_wrap=True)
    table.add_column("Company", style="dim", max_width=25)
    table.add_column("F-Score", justify="center", style="bold green")
    table.add_column("Price", justify="right")
    table.add_column("RSI", justify="center")
    table.add_column("MACD", justify="center")
    table.add_column("Rating", justify="left")
    table.add_column("Mkt Cap", justify="right", style="dim")
    
    for idx, stock in enumerate(results, 1):
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"],
            f"{stock['fscore']}/12",
            f"{stock['price']:.2f}",
            format_rsi(stock["rsi"], stock["rsi_signal"]),
            format_macd(stock["macd_signal"]),
            stock["rating"],
            format_market_cap(stock["market_cap"])
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Summary
    perfect_score = sum(1 for s in results if s["fscore"] == 12)
    excellent_score = sum(1 for s in results if s["fscore"] >= 9)
    
    summary = Panel(
        f"[green]Perfect Score (12/12):[/green] {perfect_score} stocks\n"
        f"[cyan]Excellent (≥9/12):[/cyan] {excellent_score} stocks\n\n"
        f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]",
        title="📊 Fundamental Quality",
        border_style="magenta"
    )
    console.print(summary)
    
    if export:
        symbols = [s["symbol"] for s in results]
        added = add_symbols(symbols)
        console.print(f"\n[green]✓[/green] Added {len(added)} symbols to watchlist")


@scan_app.command("graham-value")
def graham_value(
    index: str = typer.Option("NIFTY_50", "--index", "-i", help="Stock index (NIFTY_50, NIFTY_500, etc)"),
    limit: int = typer.Option(1000, "--limit", "-l", help="Maximum results"),
    min_mos: float = typer.Option(30, "--min-mos", "-m", help="Minimum Margin of Safety %"),
    conservative: bool = typer.Option(False, "--conservative", "-c", help="Use conservative valuation"),
    export: bool = typer.Option(False, "--export", "-e", help="Export to watchlist")
):
    """
    Scan for Graham-style value stocks (Margin of Safety)
    
    Finds stocks with:
    - Intrinsic value > Market price
    - Minimum MOS threshold (default 30%)
    - Based on EPS and growth rate
    - Graham's formula: EPS × (8.5 + 2g)
    """
    start_time = time.time()
    
    console.print(Panel.fit(
        f"[cyan]Scanning {index} for Graham value stocks (MOS ≥ {min_mos}%)...[/cyan]\n"
        f"[dim]Method: {'Conservative' if conservative else 'Standard Graham'}[/dim]",
        title="🛡️ Graham Value Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Calculating intrinsic values...", total=100)
        
        results = scan_for_graham_value(index, limit, min_mos, conservative)
        progress.update(task, completed=100)
    
    scan_time = time.time() - start_time
    
    if not results:
        console.print()
        console.print(Panel(
            f"[yellow]No stocks met the minimum Margin of Safety threshold of {min_mos}%[/yellow]\n\n"
            "Try:\n"
            "• Lowering threshold: [cyan]--min-mos 20[/cyan]\n"
            "• Different index: [cyan]--index NIFTY_500[/cyan]\n"
            "• Standard method: [cyan]Remove --conservative flag[/cyan]\n\n"
            f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]",
            title="📊 No Value Opportunities Found",
            border_style="yellow"
        ))
        return
    
    # Create results table
    table = Table(
        title=f"🛡️ Top {len(results)} Graham Value Stocks (MOS ≥ {min_mos}%)",
        show_header=True,
        header_style="bold green",
        show_lines=True,
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan", no_wrap=True)
    table.add_column("Company", style="dim", max_width=20)
    table.add_column("Price", justify="right")
    table.add_column("EPS", justify="right")
    table.add_column("Growth%", justify="right")
    table.add_column("Intrinsic", justify="right", style="bold")
    table.add_column("MOS%", justify="right", style="bold")
    table.add_column("Rating", justify="left")
    table.add_column("F-Score", justify="center")
    
    for idx, stock in enumerate(results, 1):
        # Color code MOS percentage
        if stock["mos_pct"] >= 50:
            mos_color = "bold green"
        elif stock["mos_pct"] >= 40:
            mos_color = "green"
        elif stock["mos_pct"] >= 30:
            mos_color = "yellow"
        else:
            mos_color = "dim yellow"
        
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"],
            f"₹{stock['price']:.2f}",
            f"₹{stock['eps']:.2f}",
            f"{stock['growth']:.1f}%",
            f"₹{stock['intrinsic']:.2f}",
            f"[{mos_color}]{stock['mos_pct']:.1f}%[/{mos_color}]",
            stock["rating"],
            f"{stock['fscore']}/12"
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Summary statistics
    avg_mos = sum(s["mos_pct"] for s in results) / len(results)
    strong_value = sum(1 for s in results if s["mos_pct"] >= 50)
    excellent_value = sum(1 for s in results if 40 <= s["mos_pct"] < 50)
    good_value = sum(1 for s in results if 30 <= s["mos_pct"] < 40)
    avg_fscore = sum(s["fscore"] for s in results) / len(results)
    
    method = "Conservative" if conservative else "Standard Graham"
    
    summary = Panel(
        f"[bold]Method:[/bold] {method}\n"
        f"[bold]Average MOS:[/bold] {avg_mos:.1f}%\n"
        f"[bold]Average F-Score:[/bold] {avg_fscore:.1f}/12\n"
        f"[bold green]STRONG VALUE (≥50%):[/bold green] {strong_value} stocks\n"
        f"[bold cyan]EXCELLENT VALUE (40-50%):[/bold cyan] {excellent_value} stocks\n"
        f"[bold yellow]GOOD VALUE (30-40%):[/bold yellow] {good_value} stocks\n\n"
        f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]",
        title="📊 Graham Value Summary",
        border_style="green"
    )
    console.print(summary)
    
    # Graham's wisdom
    wisdom = Panel(
        "[italic]\"Price is what you pay. Value is what you get.\"[/italic]\n"
        "— Benjamin Graham\n\n"
        "[dim]These stocks trade below intrinsic value with a margin of safety.\n"
        "Combine with fundamental analysis (F-Score ≥6) for best results.[/dim]",
        title="💡 Graham's Wisdom",
        border_style="blue"
    )
    console.print(wisdom)
    
    if export:
        # Only export stocks with MOS ≥40% (excellent value)
        symbols_to_export = [s["symbol"] for s in results if s["mos_pct"] >= 40]
        if symbols_to_export:
            added = add_symbols(symbols_to_export)
            console.print(f"\n[green]✓[/green] Exported {len(added)} stocks with MOS ≥40% to watchlist")
        else:
            console.print(f"\n[yellow]⚠[/yellow] No stocks with MOS ≥40% to export (threshold too high)")
