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
╔══════════════════════════════════════════════════════════════════╗
║                     🚀 StockeEye CLI v1.0                        ║
╚══════════════════════════════════════════════════════════════════╝

[bold cyan]Core Analysis:[/bold cyan]
  [green]stockeye analyze[/green]              Run technical + fundamental analysis
  [green]stockeye analyze -d[/green]           Run with detailed breakdown
  
[bold cyan]Market Scanning:[/bold cyan]
  [green]stockeye scan strong-buys[/green]     Find top STRONG BUY opportunities
  [green]stockeye scan fundamentals[/green]    Find fundamentally strong stocks (high F-Score)
  [green]stockeye scan value[/green]           Find technical value opportunities
  [green]stockeye scan mos[/green]             Find Graham value stocks (MOS analysis on indices)
  
[bold cyan]Graham Value Analysis:[/bold cyan]
  [green]stockeye mos analyze[/green]          Calculate Margin of Safety for watchlist
  [green]stockeye mos scan SYMBOL[/green]      Quick Graham analysis for single stock
  
[bold cyan]Watchlist Management:[/bold cyan]
  [green]stockeye watch add SYMBOL1 SYMBOL2 ...[/green]       Add symbols to watchlist
  [green]stockeye watch remove SYMBOL1 SYMBOL2 ...[/green]    Remove symbols
  [green]stockeye watch list[/green]                          Show current watchlist
  [green]stockeye watch clear[/green]                         Clear entire watchlist

[bold cyan]Examples:[/bold cyan]
  # Market scanning
  [blue]stockeye scan strong-buys[/blue]
  [blue]stockeye scan fundamentals --min-score 6[/blue]
  
  # Graham value scanning on indices
  [blue]stockeye scan mos[/blue]
  [blue]stockeye scan mos --index NIFTY_500 --min-mos 35[/blue]
  [blue]stockeye scan mos --conservative --export[/blue]
  
  # Value investing using Margin of safety
  [blue]stockeye mos analyze --min-mos 30[/blue]
  [blue]stockeye mos scan RELIANCE.NS[/blue]
  
  # Watchlist analysis
  [blue]stockeye watch add RELIANCE.NS HDFCBANK.NS[/blue]
  [blue]stockeye analyze[/blue]

[bold cyan]NSE Stock Indices:[/bold cyan]
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
