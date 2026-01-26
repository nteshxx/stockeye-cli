import typer
from rich.console import Console
from stockeye.commands import watch_app, scan_app, mos_app, run

console = Console()

app = typer.Typer(
    name="stockeye",
    help="🚀 Advanced Stock Analyzer with Market Scanning"
)

# Add subcommands
app.add_typer(watch_app, name="watch")
app.add_typer(scan_app, name="scan")
app.add_typer(mos_app, name="mos")

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
  [green]mos analyze[/green]          Run margin of safety analysis on your watchlist
  [green]mos quick[/green]            Run margin of safety analysis on stock
  
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
  [green]stockeye scan value -i NIFTY_500[/green]

[bold cyan]NSE Stock Indexes:[/bold cyan]
  [yellow]NIFTY_50[/yellow]               - Top 50 Indian stocks (default)
  [yellow]NIFTY_100[/yellow]              - Top 100 Indian stocks
  [yellow]NIFTY_200[/yellow]              - Top 200 Indian stocks
  [yellow]NIFTY_500[/yellow]              - Top 500 Indian stocks
  [yellow]NIFTY_NEXT_50[/yellow]          - Next 50 Indian stocks
  [yellow]NIFTY_MIDCAP_100[/yellow]       - Top 100 Midcap Indian stocks
  [yellow]NIFTY_SMALLCAP_100[/yellow]     - Top 100 Smallcap Indian stocks
        """)

def main():
    app()

if __name__ == "__main__":
    main()
