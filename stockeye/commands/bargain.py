"""
Classic Graham Scan CLI Commands
Typer CLI for scanning and displaying Graham bargain opportunities
"""
import typer
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from stockeye.scanners.bargain_scanner import (
    scan_graham_bargains,
    scan_net_nets,
    scan_asset_plays,
    scan_cigar_butts,
    scan_defensive_stocks,
    scan_deep_value,
    scan_by_scenario_type,
    get_scenario_summary
)
from stockeye.services.watchlist_manager import add_symbols
from stockeye.utils.formatters import format_market_cap, format_percentage, format_price, format_ratio, format_score, format_time
from stockeye.services.bargain_analyzer import get_investment_recommendation, get_scenario_emoji

bargain_app = typer.Typer(help="📚 Classic Graham Value Bargain Investing Scans")
console = Console()


@bargain_app.command("all")
def scan_all_bargains(
    index: str = typer.Option("NIFTY_500", "--index", "-i", help="Stock index"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results"),
    min_score: int = typer.Option(50, "--min-score", "-s", help="Minimum Graham score (0-100)"),
    export: bool = typer.Option(False, "--export", "-e", help="Export to watchlist")
):
    """
    Scan for ALL types of Graham bargain opportunities
    
    Finds stocks across all scenarios:
    💎 Net-Net, 🏦 Asset Plays, 🚬 Cigar Butts, 🛡️ Defensive,
    ⭐ Deep Value, ✅ Moderate Value, 📊 Statistical Bargains
    """
    start_time = time.time()
    
    console.print(Panel.fit(
        f"[cyan]Scanning {index} for classic Graham bargains (Score ≥ {min_score})...[/cyan]",
        title="📚 Graham Classic Bargain Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Analyzing value opportunities...", total=100)
        results = scan_graham_bargains(index, limit, min_score)
        progress.update(task, completed=100)
    
    scan_time = time.time() - start_time
    
    if not results:
        console.print(f"\n[yellow]No bargains found with Graham score ≥ {min_score}[/yellow]")
        console.print(f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]")
        return
    
    # Create results table
    table = Table(
        title=f"📚 Top {len(results)} Graham Bargain Opportunities",
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
    )
    
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Symbol", style="cyan bold", no_wrap=True, width=12)
    table.add_column("Scenario", justify="left", width=20)
    table.add_column("Graham", justify="center", width=8)
    table.add_column("Price", justify="right", width=10)
    table.add_column("MOS%", justify="right", width=8)
    table.add_column("P/E", justify="right", width=6)
    table.add_column("P/B", justify="right", width=6)
    table.add_column("D/E", justify="right", width=6)
    table.add_column("Rec", justify="left", width=15)
    
    for idx, stock in enumerate(results, 1):
        scenario = stock.get("scenario", "UNKNOWN")
        emoji = get_scenario_emoji(scenario)
        scenario_display = f"{emoji} {scenario.replace('_', ' ').title()}"
        
        recommendation = get_investment_recommendation(
            scenario,
            stock.get("scenario_score", 0),
            stock.get("graham_score", 0),
            stock.get("fscore", 0)
        )
        
        table.add_row(
            str(idx),
            stock["symbol"],
            scenario_display[:20],
            format_score(stock.get("graham_score", 0), 100),
            format_price(stock["price"]),
            format_percentage(stock.get("mos_pct", 0), 30),
            f"{stock.get('pe_ratio', 0):.1f}" if stock.get('pe_ratio') else "N/A",
            f"{stock.get('pb_ratio', 0):.2f}" if stock.get('pb_ratio') else "N/A",
            format_ratio(stock.get("debt_to_equity", 0)) if stock.get("debt_to_equity") else "N/A",
            recommendation
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Summary
    summary = get_scenario_summary(results)
    
    scenario_breakdown = "\n".join([
        f"{get_scenario_emoji(s)} {s.replace('_', ' ').title()}: {count}"
        for s, count in summary.get("scenario_counts", {}).items()
    ])
    
    summary_panel = Panel(
        f"[bold]Total Opportunities:[/bold] {summary.get('total_stocks', 0)}\n"
        f"[bold]Avg Graham Score:[/bold] {summary.get('avg_graham_score', 0):.1f}/100\n"
        f"[bold]Avg MOS:[/bold] {summary.get('avg_mos_pct', 0):.1f}%\n"
        f"[bold]Avg F-Score:[/bold] {summary.get('avg_fscore', 0):.1f}/12\n\n"
        f"[bold green]STRONG BUY:[/bold green] {summary.get('strong_buy_count', 0)}\n"
        f"[bold cyan]BUY:[/bold cyan] {summary.get('buy_count', 0)}\n"
        f"[bold]Debt-Free:[/bold] {summary.get('debt_free_count', 0)}\n\n"
        f"[bold]By Scenario:[/bold]\n{scenario_breakdown}\n\n"
        f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]",
        title="📊 Summary",
        border_style="cyan"
    )
    console.print(summary_panel)
    
    if export:
        # Export only STRONG BUY and BUY recommendations
        export_symbols = [
            s["symbol"] for s in results 
            if "BUY" in get_investment_recommendation(
                s.get("scenario", ""),
                s.get("scenario_score", 0),
                s.get("graham_score", 0),
                s.get("fscore", 0)
            )
        ]
        if export_symbols:
            added = add_symbols(export_symbols)
            console.print(f"\n[green]✓[/green] Exported {len(added)} BUY opportunities to watchlist")


@bargain_app.command("net-nets")
def scan_net_net_stocks(
    index: str = typer.Option("NIFTY_500", "--index", "-i", help="Stock index"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum results"),
    export: bool = typer.Option(False, "--export", "-e", help="Export to watchlist")
):
    """
    💎 Scan for NET-NET stocks (Graham's favorite)
    
    Finds stocks trading below 2/3 of Net Current Asset Value
    The ultimate margin of safety - buying below liquidation value
    """
    start_time = time.time()
    
    console.print(Panel.fit(
        f"[cyan]Scanning {index} for Net-Net opportunities...[/cyan]\n"
        "[dim]Looking for stocks trading < 2/3 NCAV[/dim]",
        title="💎 Net-Net Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Searching for net-nets...", total=100)
        results = scan_net_nets(index, limit)
        progress.update(task, completed=100)
    
    scan_time = time.time() - start_time
    
    if not results:
        console.print()
        console.print(Panel(
            "[yellow]No Net-Net stocks found![/yellow]\n\n"
            "Net-Nets are extremely rare in normal market conditions.\n"
            "They typically appear during:\n"
            "• Market crashes\n"
            "• Deep bear markets\n"
            "• Sector-specific distress\n\n"
            "Try:\n"
            "• Broader index: [cyan]--index NIFTY_TOTAL_MARKET[/cyan]\n"
            "• Asset plays: [cyan]stockeye bargain asset-plays[/cyan]\n\n"
            f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]",
            title="💎 Net-Net Search Results",
            border_style="yellow"
        ))
        return
    
    # Create detailed net-net table
    table = Table(
        title=f"💎 {len(results)} Net-Net Opportunities Found",
        show_header=True,
        header_style="bold green",
        show_lines=True,
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan bold", no_wrap=True)
    table.add_column("Company", style="dim", max_width=20)
    table.add_column("Price", justify="right")
    table.add_column("NCAV/sh", justify="right", style="bold")
    table.add_column("Buy@2/3", justify="right", style="green")
    table.add_column("Ratio", justify="right")
    table.add_column("Discount", justify="right")
    table.add_column("F-Score", justify="center")
    table.add_column("Graham", justify="center")
    
    for idx, stock in enumerate(results, 1):
        ncav = stock.get("ncav", 0)
        buy_price = stock.get("net_net_buy_price", 0)
        ratio = stock.get("net_net_ratio", 0)
        discount = ((ncav - stock["price"]) / ncav) * 100 if ncav > 0 else 0
        
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"][:20],
            format_price(stock["price"]),
            format_price(ncav),
            format_price(buy_price),
            f"[bold green]{ratio:.2f}[/bold green]" if ratio < 0.5 else f"[green]{ratio:.2f}[/green]",
            format_percentage(discount, 30),
            format_score(stock.get("fscore", 0), 12),
            format_score(stock.get("graham_score", 0), 100)
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Net-Net wisdom
    wisdom = Panel(
        "[italic]\"The best opportunities come when great companies \n"
        "are surrounded by unusual circumstances that cause the \n"
        "stock to be misappraised.\"[/italic]\n"
        "— Benjamin Graham\n\n"
        "[bold]Net-Nets:[/bold] Trading below liquidation value\n"
        "[bold]You get:[/bold] Fixed assets, brands, IP for FREE\n"
        "[bold]Risk:[/bold] Company may be in terminal decline\n"
        "[bold]Strategy:[/bold] Diversify across 20-30 net-nets\n\n"
        "[dim]Graham's net-net portfolio averaged 20%+ annual returns[/dim]",
        title="💡 Graham's Greatest Discovery",
        border_style="blue"
    )
    console.print(wisdom)
    
    if export:
        symbols = [s["symbol"] for s in results]
        added = add_symbols(symbols)
        console.print(f"\n[green]✓[/green] Exported {len(added)} net-net stocks to watchlist")


@bargain_app.command("asset-plays")
def scan_asset_play_stocks(
    index: str = typer.Option("NIFTY_500", "--index", "-i", help="Stock index"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum results"),
    export: bool = typer.Option(False, "--export", "-e", help="Export to watchlist")
):
    """
    🏦 Scan for ASSET PLAY opportunities
    
    Finds stocks trading below book value or liquidation value
    Asset-rich companies selling at a discount
    """
    start_time = time.time()
    
    console.print(Panel.fit(
        f"[cyan]Scanning {index} for Asset Play opportunities...[/cyan]\n"
        "[dim]Looking for stocks trading below book/liquidation value[/dim]",
        title="🏦 Asset Play Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Analyzing asset values...", total=100)
        results = scan_asset_plays(index, limit)
        progress.update(task, completed=100)
    
    scan_time = time.time() - start_time
    
    if not results:
        console.print(f"\n[yellow]No asset plays found in {index}[/yellow]")
        console.print(f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]")
        return
    
    # Create asset play table
    table = Table(
        title=f"🏦 {len(results)} Asset Play Opportunities",
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan bold", no_wrap=True)
    table.add_column("Company", style="dim", max_width=18)
    table.add_column("Price", justify="right")
    table.add_column("Book/sh", justify="right")
    table.add_column("P/B", justify="right")
    table.add_column("Liq.Val", justify="right")
    table.add_column("D/E", justify="right")
    table.add_column("F-Score", justify="center")
    table.add_column("Graham", justify="center")
    
    for idx, stock in enumerate(results, 1):
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"][:18],
            format_price(stock["price"]),
            format_price(stock.get("book_value", 0)),
            f"[bold green]{stock.get('pb_ratio', 0):.2f}[/bold green]",
            format_price(stock.get("liquidation_value", 0)) if stock.get("liquidation_value") else "N/A",
            format_ratio(stock.get("debt_to_equity")) if stock.get("debt_to_equity") else "N/A",
            format_score(stock.get("fscore", 0), 12),
            format_score(stock.get("graham_score", 0), 100)
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Summary
    avg_pb = sum(s.get("pb_ratio", 0) for s in results) / len(results)
    below_liquidation = sum(1 for s in results if s.get("liquidation_value") and s["price"] < s["liquidation_value"])
    
    summary = Panel(
        f"[bold]Total Asset Plays:[/bold] {len(results)}\n"
        f"[bold]Average P/B:[/bold] {avg_pb:.2f}\n"
        f"[bold]Below Liquidation Value:[/bold] {below_liquidation}\n\n"
        f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]",
        title="📊 Summary",
        border_style="cyan"
    )
    console.print(summary)
    
    if export:
        symbols = [s["symbol"] for s in results]
        added = add_symbols(symbols)
        console.print(f"\n[green]✓[/green] Exported {len(added)} asset plays to watchlist")


@bargain_app.command("cigar-butts")
def scan_cigar_butt_stocks(
    index: str = typer.Option("NIFTY_500", "--index", "-i", help="Stock index"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum results"),
    min_score: int = typer.Option(4, "--min-score", "-s", help="Minimum cigar score (out of 5)"),
    export: bool = typer.Option(False, "--export", "-e", help="Export to watchlist")
):
    """
    🚬 Scan for CIGAR BUTT opportunities
    
    Finds beaten-down but still profitable stocks
    "One last puff" - short-term value plays
    Higher risk but potential for quick profits
    """
    start_time = time.time()
    
    console.print(Panel.fit(
        f"[cyan]Scanning {index} for Cigar Butt opportunities...[/cyan]\n"
        "[dim]Looking for beaten-down profitable stocks[/dim]",
        title="🚬 Cigar Butt Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Finding cigar butts...", total=100)
        results = scan_cigar_butts(index, limit, min_score)
        progress.update(task, completed=100)
    
    scan_time = time.time() - start_time
    
    if not results:
        console.print(f"\n[yellow]No cigar butts found with score ≥ {min_score}[/yellow]")
        console.print(f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]")
        return
    
    # Create cigar butt table
    table = Table(
        title=f"🚬 {len(results)} Cigar Butt Opportunities",
        show_header=True,
        header_style="bold yellow",
        show_lines=True,
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan bold", no_wrap=True)
    table.add_column("Company", style="dim", max_width=18)
    table.add_column("Price", justify="right")
    table.add_column("P/E", justify="right")
    table.add_column("P/B", justify="right")
    table.add_column("Cigar", justify="center")
    table.add_column("EPS", justify="right")
    table.add_column("D/E", justify="right")
    table.add_column("Graham", justify="center")
    
    for idx, stock in enumerate(results, 1):
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"][:18],
            format_price(stock["price"]),
            f"[bold green]{stock.get('pe_ratio', 0):.1f}[/bold green]" if stock.get('pe_ratio') and stock['pe_ratio'] < 7 else f"{stock.get('pe_ratio', 0):.1f}",
            f"[bold green]{stock.get('pb_ratio', 0):.2f}[/bold green]" if stock.get('pb_ratio') and stock['pb_ratio'] < 0.8 else f"{stock.get('pb_ratio', 0):.2f}",
            format_score(stock.get("cigar_butt_score", 0), 5),
            format_price(stock.get("eps", 0)),
            format_ratio(stock.get("debt_to_equity")) if stock.get("debt_to_equity") else "N/A",
            format_score(stock.get("graham_score", 0), 100)
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Warning about cigar butts
    warning = Panel(
        "[bold yellow]⚠️  CIGAR BUTT STRATEGY - USE WITH CAUTION[/bold yellow]\n\n"
        "[italic]\"If you buy a stock at a sufficiently low price, there will \n"
        "usually be some hiccup in the business that gives you a chance \n"
        "to sell at a decent profit, even though the long-term performance \n"
        "may be terrible.\"[/italic]\n"
        "— Warren Buffett on Cigar Butts\n\n"
        "[bold]Characteristics:[/bold]\n"
        "• Very cheap (P/E < 7, P/B < 0.8)\n"
        "• Still profitable (positive EPS)\n"
        "• Often declining businesses\n\n"
        "[bold]Strategy:[/bold]\n"
        "• Buy diversified basket (15-20 stocks)\n"
        "• Set profit targets (20-30%)\n"
        "• Exit quickly - don't hold long-term\n"
        "• NOT for buy-and-hold investors\n\n"
        f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]",
        title="⚠️  Important Note",
        border_style="yellow"
    )
    console.print(warning)
    
    if export:
        symbols = [s["symbol"] for s in results]
        added = add_symbols(symbols)
        console.print(f"\n[green]✓[/green] Exported {len(added)} cigar butts to watchlist")


@bargain_app.command("defensive")
def scan_defensive_investor_stocks(
    index: str = typer.Option("NIFTY_50", "--index", "-i", help="Stock index"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum results"),
    min_score: int = typer.Option(5, "--min-score", "-s", help="Minimum defensive score (out of 7)"),
    export: bool = typer.Option(False, "--export", "-e", help="Export to watchlist")
):
    """
    🛡️ Scan for DEFENSIVE INVESTOR stocks
    
    Quality companies meeting Graham's defensive criteria:
    • Large size • Strong financials • Earnings stability
    • Dividend record • Moderate P/E • Moderate P/B
    
    Perfect for passive, low-risk investors
    """
    start_time = time.time()
    
    console.print(Panel.fit(
        f"[cyan]Scanning {index} for Defensive Investor stocks...[/cyan]\n"
        "[dim]Quality companies at reasonable prices[/dim]",
        title="🛡️ Defensive Investor Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Finding defensive stocks...", total=100)
        results = scan_defensive_stocks(index, limit, min_score)
        progress.update(task, completed=100)
    
    scan_time = time.time() - start_time
    
    if not results:
        console.print(f"\n[yellow]No defensive stocks found with score ≥ {min_score}[/yellow]")
        console.print(f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]")
        return
    
    # Create defensive table
    table = Table(
        title=f"🛡️ {len(results)} Defensive Quality Stocks",
        show_header=True,
        header_style="bold blue",
        show_lines=True,
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan bold", no_wrap=True)
    table.add_column("Company", style="dim", max_width=20)
    table.add_column("Price", justify="right")
    table.add_column("P/E", justify="right")
    table.add_column("P/B", justify="right")
    table.add_column("Div%", justify="right")
    table.add_column("Def", justify="center")
    table.add_column("F-Score", justify="center")
    table.add_column("Graham", justify="center")
    
    for idx, stock in enumerate(results, 1):
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"][:20],
            format_price(stock["price"]),
            f"{stock.get('pe_ratio', 0):.1f}" if stock.get('pe_ratio') else "N/A",
            f"{stock.get('pb_ratio', 0):.2f}" if stock.get('pb_ratio') else "N/A",
            f"{stock.get('dividend_yield', 0):.1f}%" if stock.get('dividend_yield') else "0%",
            format_score(stock.get("defensive_score", 0), 7),
            format_score(stock.get("fscore", 0), 12),
            format_score(stock.get("graham_score", 0), 100)
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Summary
    perfect_scores = sum(1 for s in results if s.get("defensive_score") == 7)
    avg_div_yield = sum(s.get("dividend_yield", 0) for s in results) / len(results)
    
    summary = Panel(
        f"[bold]Total Defensive Stocks:[/bold] {len(results)}\n"
        f"[bold]Perfect Scores (7/7):[/bold] {perfect_scores}\n"
        f"[bold]Average Dividend:[/bold] {avg_div_yield:.1f}%\n\n"
        "[bold]For Defensive Investors:[/bold]\n"
        "• Low-risk, passive approach\n"
        "• Buy and hold 10-30 stocks\n"
        "• Rebalance annually\n"
        "• Expected: 10-12% annual returns\n\n"
        f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]",
        title="📊 Defensive Portfolio",
        border_style="blue"
    )
    console.print(summary)
    
    if export:
        symbols = [s["symbol"] for s in results]
        added = add_symbols(symbols)
        console.print(f"\n[green]✓[/green] Exported {len(added)} defensive stocks to watchlist")


@bargain_app.command("deep-value")
def scan_deep_value_stocks(
    index: str = typer.Option("NIFTY_500", "--index", "-i", help="Stock index"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum results"),
    min_mos: float = typer.Option(40.0, "--min-mos", "-m", help="Minimum MOS %"),
    export: bool = typer.Option(False, "--export", "-e", help="Export to watchlist")
):
    """
    ⭐ Scan for DEEP VALUE opportunities
    
    Stocks with high margin of safety (≥40%)
    Trading at significant discount to intrinsic value
    For enterprising investors willing to do research
    """
    start_time = time.time()
    
    console.print(Panel.fit(
        f"[cyan]Scanning {index} for Deep Value opportunities...[/cyan]\n"
        f"[dim]Looking for stocks with MOS ≥ {min_mos}%[/dim]",
        title="⭐ Deep Value Scanner"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Finding deep value...", total=100)
        results = scan_deep_value(index, limit, min_mos)
        progress.update(task, completed=100)
    
    scan_time = time.time() - start_time
    
    if not results:
        console.print(f"\n[yellow]No deep value stocks found with MOS ≥ {min_mos}%[/yellow]")
        console.print(f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]")
        return
    
    # Create deep value table
    table = Table(
        title=f"⭐ {len(results)} Deep Value Opportunities",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="cyan bold", no_wrap=True)
    table.add_column("Company", style="dim", max_width=18)
    table.add_column("Price", justify="right")
    table.add_column("Intrinsic", justify="right", style="bold")
    table.add_column("MOS%", justify="right", style="bold")
    table.add_column("EPS", justify="right")
    table.add_column("Growth", justify="right")
    table.add_column("F-Score", justify="center")
    table.add_column("Graham", justify="center")
    
    for idx, stock in enumerate(results, 1):
        table.add_row(
            str(idx),
            stock["symbol"],
            stock["company_name"][:18],
            format_price(stock["price"]),
            format_price(stock.get("graham_intrinsic", 0)),
            format_percentage(stock.get("mos_pct", 0), 40),
            format_price(stock.get("eps", 0)),
            f"{stock.get('growth', 0):.1f}%",
            format_score(stock.get("fscore", 0), 12),
            format_score(stock.get("graham_score", 0), 100)
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Summary
    avg_mos = sum(s.get("mos_pct", 0) for s in results) / len(results)
    extreme_value = sum(1 for s in results if s.get("mos_pct", 0) >= 50)
    
    summary = Panel(
        f"[bold]Total Deep Value:[/bold] {len(results)}\n"
        f"[bold]Average MOS:[/bold] {avg_mos:.1f}%\n"
        f"[bold]Extreme Value (≥50%):[/bold] {extreme_value}\n\n"
        "[bold]Deep Value Strategy:[/bold]\n"
        "• Higher returns (15-20%+ potential)\n"
        "• Requires research and patience\n"
        "• Hold 2-5 years for revaluation\n"
        "• Combine with F-Score ≥6\n\n"
        f"[dim]⏱️  Scan time: {format_time(scan_time)}[/dim]",
        title="📊 Deep Value Summary",
        border_style="magenta"
    )
    console.print(summary)
    
    if export:
        symbols = [s["symbol"] for s in results]
        added = add_symbols(symbols)
        console.print(f"\n[green]✓[/green] Exported {len(added)} deep value stocks to watchlist")
