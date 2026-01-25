import typer
from rich.console import Console
from commands.watch import watch_app
from commands.scan import scan_app
from commands.run import run

console = Console()

app = typer.Typer(
    name="stockeye-cli",
    help="🚀 Advanced Stock Analyzer with Market Scanning"
)

# Add subcommands
app.add_typer(watch_app, name="watch", help="Manage watchlist (add/remove/list/clear)")
app.add_typer(scan_app, name="scan", help="Scan markets for opportunities (strong-buys/fundamentals/value)")

@app.command()
def analyze(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed technical analysis")
):
    """
    Run advanced analysis on watchlist symbols
    
    Analyzes all stocks in your watchlist with:
    - Price vs DMAs (50 & 200)
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Volume Analysis
    - Fundamental Score
    - Golden/Death Cross Age
    - 7-Level Rating System (STRONG BUY to STRONG SELL)
    """
    run(detailed=detailed)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Stock Analyzer CLI - Advanced Technical & Fundamental Analysis
    """
    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        console.print("""
╔══════════════════════════════════════════════════════════╗
║       🚀 Advanced Stock Analyzer CLI v4.0                ║
║       Market Scanner • 7-Level Ratings • Multi-Market    ║
╚══════════════════════════════════════════════════════════╝

[bold cyan]Core Commands:[/bold cyan]
  [green]analyze[/green]              Run analysis on your watchlist
  [green]analyze -d[/green]           Run with detailed breakdown
  
[bold cyan]Market Scanning:[/bold cyan]
  [green]scan strong-buys[/green]     Find top STRONG BUY opportunities
  [green]scan fundamentals[/green]    Find fundamentally strong stocks
  [green]scan value[/green]           Find value opportunities (strong + cheap)
  
[bold cyan]Watchlist Management:[/bold cyan]
  [green]watch add[/green]            Add symbols to watchlist
  [green]watch remove[/green]         Remove symbols from watchlist
  [green]watch list[/green]           Show current watchlist
  [green]watch clear[/green]          Clear entire watchlist

[bold cyan]Examples:[/bold cyan]
  # Find top STRONG BUY stocks from NIFTY 50
  docker compose run stock-cli scan strong-buys
  
  # Find fundamentally strong stocks (F-Score ≥ 6)
  docker compose run stock-cli scan fundamentals --min-score 6
  
  # Scan US market for value opportunities
  docker compose run stock-cli scan value -u US_MEGA_CAPS
  
  # Add and analyze your watchlist
  docker compose run stock-cli watch add RELIANCE.NS HDFCBANK.NS
  docker compose run stock-cli analyze

[bold cyan]Stock Universes:[/bold cyan]
  [yellow]NIFTY50[/yellow]          - Top 50 Indian stocks (default)
  [yellow]NIFTY_NEXT_50[/yellow]    - Next 50 Indian stocks
  [yellow]ALL_INDIAN[/yellow]       - All 100 Indian stocks
  [yellow]US_MEGA_CAPS[/yellow]     - Top 50 US stocks

[bold cyan]Rating System:[/bold cyan]
  [green]🟢🟢 STRONG BUY[/green]   - Exceptional opportunity
  [green]🟢 BUY[/green]            - Good entry point
  [blue]🔵 ADD[/blue]             - Good for adding to position
  [yellow]🟡 HOLD[/yellow]           - Maintain position
  [rgb(255,165,0)]🟠 PARTIAL EXIT[/rgb(255,165,0)]   - Consider reducing
  [red]🔴 EXIT[/red]           - Exit position
  [red]🔴🔴 STRONG SELL[/red]  - Urgent exit

[bold cyan]Technical Indicators:[/bold cyan]
  ✓ DMA 50 & 200 (Trend direction)
  ✓ RSI (Overbought/Oversold detection)
  ✓ MACD (Momentum analysis)
  ✓ Volume Analysis (Conviction measurement)
  ✓ Golden/Death Cross with age tracking
  ✓ Fundamental Scoring (ROE, D/E, Growth, Margins)
        """)


if __name__ == "__main__":
    app()