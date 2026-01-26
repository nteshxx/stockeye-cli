import typer
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from stockeye.storage import load_watchlist
from stockeye.core.data_fetcher import fetch_stock
from stockeye.core.margin_of_safety import (
    calculate_growth,
    intrinsic_value,
    margin_of_safety,
    graham_rating,
    get_eps_metrics,
    conservative_intrinsic_value
)

mos_app = typer.Typer(help="📊 Graham-style Value Analysis")
console = Console()


def get_eps_history(info, years=5):
    """
    Extract EPS history from stock info
    Returns pandas Series of EPS values
    """
    try:
        # Try to get trailing EPS
        eps_data = []
        
        # Current EPS
        trailing_eps = info.get('trailingEps')
        if trailing_eps and trailing_eps > 0:
            eps_data.append(trailing_eps)
        
        # Try to get forward EPS as well
        forward_eps = info.get('forwardEps')
        
        # If we have very limited data, try other fields
        if len(eps_data) < 2:
            # Try earnings history from financials
            # This is a simplified version - real implementation would fetch from yfinance Ticker.earnings
            pass
        
        if eps_data:
            return pd.Series(eps_data)
        else:
            return pd.Series([])
            
    except Exception as e:
        return pd.Series([])


@mos_app.command("analyze")
def analyze(
    min_mos: float = typer.Option(30, "--min-mos", "-m", help="Minimum Margin of Safety %"),
    conservative: bool = typer.Option(False, "--conservative", "-c", help="Use ultra-conservative valuation"),
    export: bool = typer.Option(False, "--export", "-e", help="Export results to watchlist"),
):
    """
    Run Graham-style Margin of Safety analysis on watchlist
    
    Calculates intrinsic value based on:
    - Historical EPS (Earnings Per Share)
    - Growth rate (CAGR)
    - Graham's formula: V = EPS × (8.5 + 2g)
    - Margin of Safety = (Intrinsic - Price) / Intrinsic
    """
    stocks = load_watchlist()
    
    if not stocks:
        console.print(Panel.fit(
            "[yellow]Watchlist is empty![/yellow]\n\n"
            "Add symbols using:\n"
            "[cyan]docker compose run stock-cli watch add SYMBOL1 SYMBOL2[/cyan]",
            title="No Symbols to Analyze"
        ))
        return
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Analyzing values...", total=len(stocks))
        
        for symbol in stocks:
            progress.update(task, description=f"[cyan]Analyzing {symbol}...")
            
            try:
                df, info = fetch_stock(symbol, "5y")  # Get 5 years of data
                
                if df is None or len(df) < 50:
                    progress.advance(task)
                    continue
                
                price = df['Close'].iloc[-1]
                
                # Get EPS data
                trailing_eps = info.get('trailingEps', 0)
                forward_eps = info.get('forwardEps', 0)
                
                # Use average of available EPS
                eps_values = [e for e in [trailing_eps, forward_eps] if e and e > 0]
                
                if not eps_values:
                    progress.advance(task)
                    continue
                
                avg_eps = sum(eps_values) / len(eps_values)
                
                # Estimate growth from revenue growth and earnings growth
                revenue_growth = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
                earnings_growth = info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0
                
                # Conservative growth estimate
                growth = (revenue_growth + earnings_growth) / 2 if (revenue_growth or earnings_growth) else 0
                growth = max(-20, min(25, growth))  # Cap between -20% and 25%
                
                # Calculate intrinsic value
                if conservative:
                    intrinsic = conservative_intrinsic_value(avg_eps, growth)
                else:
                    intrinsic = intrinsic_value(avg_eps, growth)
                
                # Calculate margin of safety
                mos_value, mos_pct = margin_of_safety(intrinsic, price)
                
                # Only include if meets minimum MOS
                if mos_pct < min_mos:
                    progress.advance(task)
                    continue
                
                results.append({
                    "symbol": symbol,
                    "price": price,
                    "eps": avg_eps,
                    "growth": growth,
                    "intrinsic": intrinsic,
                    "mos_value": mos_value,
                    "mos_pct": mos_pct,
                    "rating": graham_rating(mos_pct),
                    "company": info.get('longName', symbol)
                })
                
            except Exception as e:
                console.print(f"[dim]⚠ {symbol} skipped: {str(e)}[/dim]")
            
            progress.advance(task)
    
    if not results:
        console.print()
        console.print(Panel(
            f"[yellow]No stocks met the minimum Margin of Safety threshold of {min_mos}%[/yellow]\n\n"
            "Try lowering the threshold with: [cyan]--min-mos 20[/cyan]\n"
            "Or check if your watchlist needs different stocks.",
            title="📊 No Value Opportunities Found",
            border_style="yellow"
        ))
        return
    
    # Sort by MOS percentage (descending)
    results.sort(key=lambda x: x["mos_pct"], reverse=True)
    
    # Create results table
    table = Table(
        title=f"🛡️ Margin of Safety Analysis - Graham Method ({len(results)} stocks)",
        show_header=True,
        header_style="bold green"
    )
    
    table.add_column("#", justify="right", style="dim")
    table.add_column("Stock", style="cyan")
    table.add_column("Company", style="dim", max_width=25)
    table.add_column("Price", justify="right")
    table.add_column("EPS", justify="right")
    table.add_column("Growth%", justify="right")
    table.add_column("Intrinsic", justify="right", style="bold")
    table.add_column("MOS", justify="right")
    table.add_column("MOS%", justify="right", style="bold")
    table.add_column("Rating", justify="center")
    
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
            stock["company"],
            f"₹{stock['price']:.2f}",
            f"{stock['eps']:.2f}",
            f"{stock['growth']:.1f}%",
            f"₹{stock['intrinsic']:.2f}",
            f"₹{stock['mos_value']:.2f}",
            f"[{mos_color}]{stock['mos_pct']:.1f}%[/{mos_color}]",
            stock["rating"]
        )
    
    console.print()
    console.print(table)
    console.print()
    
    # Summary statistics
    avg_mos = sum(s["mos_pct"] for s in results) / len(results)
    strong_value = sum(1 for s in results if s["mos_pct"] >= 50)
    excellent_value = sum(1 for s in results if 40 <= s["mos_pct"] < 50)
    good_value = sum(1 for s in results if 30 <= s["mos_pct"] < 40)
    
    method = "Conservative" if conservative else "Standard Graham"
    
    summary = Panel(
        f"[bold]Method:[/bold] {method}\n"
        f"[bold]Stocks Analyzed:[/bold] {len(stocks)}\n"
        f"[bold]Value Opportunities Found:[/bold] {len(results)}\n"
        f"[bold]Average MOS:[/bold] {avg_mos:.1f}%\n\n"
        f"[bold green]STRONG VALUE (≥50%):[/bold green] {strong_value} stocks\n"
        f"[bold cyan]EXCELLENT VALUE (40-50%):[/bold cyan] {excellent_value} stocks\n"
        f"[bold yellow]GOOD VALUE (30-40%):[/bold yellow] {good_value} stocks",
        title="📊 Value Analysis Summary",
        border_style="green"
    )
    console.print(summary)
    
    # Graham's wisdom
    wisdom = Panel(
        "[italic]\"The investor's chief problem - and even his worst enemy - "
        "is likely to be himself.\"[/italic]\n"
        "— Benjamin Graham\n\n"
        "[dim]Value investing requires patience. These stocks are undervalued "
        "based on fundamentals, but markets can remain irrational longer than "
        "you can remain solvent. Always do your own research![/dim]",
        title="💡 Graham's Wisdom",
        border_style="blue"
    )
    console.print(wisdom)
    
    if export:
        from storage import add_symbols
        symbols_to_export = [s["symbol"] for s in results if s["mos_pct"] >= 40]
        if symbols_to_export:
            added = add_symbols(symbols_to_export)
            console.print(f"\n[green]✓[/green] Exported {len(added)} stocks with MOS ≥40% to watchlist")


@mos_app.command("scan")
def scan(
    symbol: str = typer.Argument(..., help="Stock symbol to analyze"),
):
    """
    Quick Graham analysis for a single stock
    
    Example: docker compose run stock-cli value quick RELIANCE.NS
    """
    console.print(f"\n[cyan]Analyzing {symbol}...[/cyan]\n")
    
    try:
        df, info = fetch_stock(symbol, "5y")
        
        if df is None:
            console.print(f"[red]Could not fetch data for {symbol}[/red]")
            return
        
        price = df['Close'].iloc[-1]
        company_name = info.get('longName', symbol)
        
        # Get EPS
        trailing_eps = info.get('trailingEps', 0)
        forward_eps = info.get('forwardEps', 0)
        
        eps_values = [e for e in [trailing_eps, forward_eps] if e and e > 0]
        
        if not eps_values:
            console.print(f"[red]No EPS data available for {symbol}[/red]")
            return
        
        avg_eps = sum(eps_values) / len(eps_values)
        
        # Estimate growth
        revenue_growth = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
        earnings_growth = info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0
        growth = (revenue_growth + earnings_growth) / 2 if (revenue_growth or earnings_growth) else 0
        growth = max(-20, min(25, growth))
        
        # Calculate values
        intrinsic_std = intrinsic_value(avg_eps, growth)
        intrinsic_cons = conservative_intrinsic_value(avg_eps, growth)
        mos_value_std, mos_pct_std = margin_of_safety(intrinsic_std, price)
        mos_value_cons, mos_pct_cons = margin_of_safety(intrinsic_cons, price)
        
        # Display detailed analysis
        info_table = Table(title=f"📊 {company_name}", show_header=False, box=None)
        info_table.add_column("", style="bold")
        info_table.add_column("", style="cyan")
        
        info_table.add_row("Symbol", symbol)
        info_table.add_row("Current Price", f"₹{price:.2f}")
        info_table.add_row("EPS (Average)", f"₹{avg_eps:.2f}")
        info_table.add_row("Est. Growth Rate", f"{growth:.1f}%")
        info_table.add_row("", "")
        info_table.add_row("[bold]STANDARD GRAHAM", "")
        info_table.add_row("Intrinsic Value", f"₹{intrinsic_std:.2f}")
        info_table.add_row("Margin of Safety", f"₹{mos_value_std:.2f} ({mos_pct_std:.1f}%)")
        info_table.add_row("Rating", graham_rating(mos_pct_std))
        info_table.add_row("", "")
        info_table.add_row("[bold]CONSERVATIVE", "")
        info_table.add_row("Intrinsic Value", f"₹{intrinsic_cons:.2f}")
        info_table.add_row("Margin of Safety", f"₹{mos_value_cons:.2f} ({mos_pct_cons:.1f}%)")
        info_table.add_row("Rating", graham_rating(mos_pct_cons))
        
        console.print(info_table)
        console.print()
        
        # Recommendation
        if mos_pct_std >= 30:
            console.print(Panel(
                f"[bold green]✓ GOOD VALUE OPPORTUNITY[/bold green]\n\n"
                f"Standard MOS of {mos_pct_std:.1f}% exceeds the recommended 30% threshold.\n"
                f"Conservative MOS: {mos_pct_cons:.1f}%\n\n"
                f"[dim]This stock appears undervalued based on Graham's formula. "
                "Consider adding to your watchlist for further research.[/dim]",
                border_style="green"
            ))
        elif mos_pct_std >= 20:
            console.print(Panel(
                f"[bold yellow]⚠ FAIR VALUE[/bold yellow]\n\n"
                f"Standard MOS of {mos_pct_std:.1f}% is modest.\n"
                f"Conservative MOS: {mos_pct_cons:.1f}%\n\n"
                f"[dim]Marginally undervalued. Wait for better entry point or "
                "verify with additional analysis.[/dim]",
                border_style="yellow"
            ))
        else:
            console.print(Panel(
                f"[bold red]✗ NOT A VALUE OPPORTUNITY[/bold red]\n\n"
                f"Standard MOS of {mos_pct_std:.1f}% is below recommended 30%.\n"
                f"Conservative MOS: {mos_pct_cons:.1f}%\n\n"
                f"[dim]Stock appears fairly valued or overvalued. "
                "Consider waiting for a better price.[/dim]",
                border_style="red"
            ))
        
    except Exception as e:
        console.print(f"[red]Error analyzing {symbol}: {str(e)}[/red]")
