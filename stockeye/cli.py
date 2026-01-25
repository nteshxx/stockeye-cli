import typer
from rich.console import Console
from stockeye.commands import watch_app, scan_app, run

console = Console()

app = typer.Typer(
    name="stockeye",
    help="🚀 Advanced Stock Analyzer with Market Scanning"
)

# Add subcommands
app.add_typer(watch_app, name="watch")
app.add_typer(scan_app, name="scan")

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
    - 7-Level Rating System (STRONG BUY to STRONG EXIT)
    """
    run(detailed=detailed)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    StockEye CLI - Advanced Technical & Fundamental Analysis
    """
    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        console.print("""
╔══════════════════════════════════════════════════════════╗
║         🚀 StockEye - Advanced Stock Analyzer CLI        ║
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
  # Add stocks to your watchlist
  [green]stockeye watch add RELIANCE.NS HDFCBANK.NS[/green]

  # Analyze your watchlist
  [green]stockeye analyze[/green]

  # Find top STRONG BUY stocks from NIFTY 50
  [green]stockeye scan strong-buys[/green]
  
  # Find fundamentally strong stocks (F-Score ≥ 6)
  [green]stockeye scan fundamentals --min-score 6[/green]
  
  # Scan US market for value opportunities
  [green]stockeye scan value -u US_MEGA_CAPS[/green]

[bold cyan]Stock Universes:[/bold cyan]
  [yellow]NIFTY50[/yellow]          - Top 50 Indian stocks (default)
  [yellow]NIFTY_NEXT_50[/yellow]    - Next 50 Indian stocks
  [yellow]ALL_INDIAN[/yellow]       - All 100 Indian stocks
  [yellow]US_MEGA_CAPS[/yellow]     - Top 50 US stocks
        """)

def main():
    app()

if __name__ == "__main__":
    main()
