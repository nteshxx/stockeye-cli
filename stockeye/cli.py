import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from stockeye.commands import watch_app, scan_app, mos_app, run

console = Console()

__version__ = "2.0.0"
__app_name__ = "StockEye"

app = typer.Typer(
    name="stockeye",
    help="🚀 Advanced Stock Analyzer with Indian Market Intelligence",
    add_completion=False,
)

# Add subcommands
app.add_typer(watch_app, name="watch")
app.add_typer(scan_app, name="scan")
app.add_typer(mos_app, name="mos")


@app.command()
def version():
    """
    Show StockEye version information
    """
    console.print(Panel.fit(
        f"[bold cyan]{__app_name__}[/bold cyan] version [green]{__version__}[/green]\n\n"
        f"[dim]Advanced Stock Analysis Tool for Indian Markets[/dim]\n"
        f"[dim]Enhanced with Bollinger Bands, Supertrend, ADX, and India VIX[/dim]\n\n"
        f"[yellow]Author:[/yellow] StockEye Team\n"
        f"[yellow]Python:[/yellow] {sys.version.split()[0]}",
        title="ℹ️ Version Info",
        border_style="cyan"
    ))


@app.command(name="help")
def show_help(
    command: str = typer.Argument(None, help="Command to get help for")
):
    """
    Show detailed help for commands
    """
    if command is None:
        console.print("""
╔══════════════════════════════════════════════════════════════╗
║                  🚀 StockEye CLI v2.0.0                      ║
║          Advanced Indian Stock Market Analysis Tool          ║
╚══════════════════════════════════════════════════════════════╝

[bold cyan]🎯 QUICK START:[/bold cyan]

1. Add stocks to watchlist:
   [green]stockeye watch add RELIANCE.NS TCS.NS INFY.NS[/green]

2. Analyze your watchlist:
   [green]stockeye analyze[/green]

3. Scan for opportunities:
   [green]stockeye scan strong-buys[/green]

[bold cyan]📊 CORE COMMANDS:[/bold cyan]

  [yellow]stockeye analyze[/yellow]          Run technical + fundamental analysis
  [yellow]stockeye analyze -d[/yellow]       Run with detailed breakdown
  [yellow]stockeye version[/yellow]          Show version information
  [yellow]stockeye help [COMMAND][/yellow]   Show help for specific command

[bold cyan]🔍 MARKET SCANNING:[/bold cyan]

  [yellow]stockeye scan strong-buys[/yellow]     Find top STRONG BUY opportunities
  [yellow]stockeye scan fundamentals[/yellow]    Find strong F-Score stocks (≥5)
  [yellow]stockeye scan value[/yellow]           Find value opportunities
  [yellow]stockeye scan mos[/yellow]             Find Graham value stocks

[bold cyan]💎 VALUE INVESTING (Graham Method):[/bold cyan]

  [yellow]stockeye mos analyze[/yellow]          Margin of Safety on watchlist
  [yellow]stockeye mos scan SYMBOL[/yellow]      Quick Graham analysis
  
[bold cyan]📋 WATCHLIST MANAGEMENT:[/bold cyan]

  [yellow]stockeye watch add SYMBOL...[/yellow]     Add symbols
  [yellow]stockeye watch remove SYMBOL...[/yellow]  Remove symbols
  [yellow]stockeye watch list[/yellow]              Show watchlist
  [yellow]stockeye watch clear[/yellow]             Clear all symbols

[bold cyan]🇮🇳 INDIAN MARKET FEATURES:[/bold cyan]

  • India VIX integration for volatility context
  • Bollinger Bands for overbought/oversold
  • Supertrend indicator (popular in Indian trading)
  • ADX for trend strength measurement
  • Sector-specific volatility adjustments
  • Calendar effects (Budget season, Dec rally)
  • Market regime detection (Bull/Bear/Sideways)
  • Enhanced F-Score with Indian metrics

[bold cyan]📈 SUPPORTED INDICES:[/bold cyan]

  NIFTY_50            - Top 50 stocks (default)
  NIFTY_100           - Top 100 stocks
  NIFTY_200           - Top 200 stocks
  NIFTY_500           - Top 500 stocks
  NIFTY_NEXT_50       - Next 50 stocks
  NIFTY_MIDCAP_100    - Top 100 Midcap stocks
  NIFTY_SMALLCAP_100  - Top 100 Smallcap stocks

[bold cyan]💡 EXAMPLES:[/bold cyan]

  # Market scanning with filters
  [blue]stockeye scan strong-buys --index NIFTY_500 --limit 20[/blue]
  [blue]stockeye scan fundamentals --min-score 7[/blue]
  
  # Graham value analysis
  [blue]stockeye scan mos --min-mos 40 --conservative[/blue]
  [blue]stockeye mos scan RELIANCE.NS[/blue]
  
  # Watchlist workflow
  [blue]stockeye watch add HDFCBANK.NS ICICIBANK.NS[/blue]
  [blue]stockeye analyze --detailed[/blue]
  [blue]stockeye mos analyze --min-mos 30[/blue]

[bold cyan]📖 MORE INFO:[/bold cyan]

  For command-specific help:
    [green]stockeye COMMAND --help[/green]
  
  Example:
    [green]stockeye scan --help[/green]
    [green]stockeye mos --help[/green]

[dim]Use [cyan]stockeye version[/cyan] to check your version[/dim]
        """)
    
    elif command == "analyze":
        console.print("""
[bold cyan]📊 ANALYZE COMMAND[/bold cyan]

Runs comprehensive technical and fundamental analysis on your watchlist.

[yellow]Usage:[/yellow]
  stockeye analyze [OPTIONS]

[yellow]Options:[/yellow]
  -d, --detailed    Show detailed technical indicator breakdown
  --help            Show this help message

[yellow]What it analyzes:[/yellow]
  • Price vs Moving Averages (DMA 50 & 200)
  • RSI (Relative Strength Index)
  • MACD (Moving Average Convergence Divergence)
  • Volume Analysis (vs 20-day average)
  • Bollinger Bands position
  • Supertrend direction
  • ADX trend strength
  • Fundamental Score (0-12 points)
  • Golden/Death Cross detection
  • India VIX context
  • Market regime (Bull/Bear/Sideways)

[yellow]Examples:[/yellow]
  stockeye analyze
  stockeye analyze --detailed
        """)
    
    elif command == "scan":
        console.print("""
[bold cyan]🔍 SCAN COMMANDS[/bold cyan]

Scan entire market indices for trading opportunities.

[yellow]Available Scans:[/yellow]

1. [green]stockeye scan strong-buys[/green]
   Find stocks with STRONG BUY or BUY ratings
   
   Options:
     --index, -i     Index to scan (default: NIFTY_50)
     --limit, -l     Max results (default: 50)
     --export, -e    Export to watchlist

2. [green]stockeye scan fundamentals[/green]
   Find fundamentally strong stocks (high F-Score)
   
   Options:
     --min-score, -m Minimum F-Score (default: 5)
     --index, -i     Index to scan
     --export, -e    Export to watchlist

3. [green]stockeye scan value[/green]
   Find quality stocks with temporary weakness
   
   Criteria: F-Score ≥6 + (RSI <40 OR ADD rating)

4. [green]stockeye scan mos[/green]
   Graham-style value screening (Margin of Safety)
   
   Options:
     --min-mos, -m      Min MOS % (default: 30)
     --conservative, -c Use conservative valuation
     --index, -i        Index to scan

[yellow]Examples:[/yellow]
  stockeye scan strong-buys --index NIFTY_500
  stockeye scan fundamentals --min-score 7 --export
  stockeye scan mos --min-mos 40 --conservative
        """)
    
    elif command == "mos":
        console.print("""
[bold cyan]💎 MARGIN OF SAFETY (Graham Method)[/bold cyan]

Value investing analysis based on Benjamin Graham's principles.

[yellow]Commands:[/yellow]

1. [green]stockeye mos analyze[/green]
   Calculate MOS for entire watchlist
   
   Options:
     --min-mos, -m      Minimum MOS % (default: 30)
     --conservative, -c Ultra-conservative valuation
     --export, -e       Export results to watchlist

2. [green]stockeye mos scan SYMBOL[/green]
   Quick Graham analysis for single stock
   
   Shows:
   • Current price vs intrinsic value
   • EPS and growth rate
   • Margin of Safety (%)
   • Both standard and conservative valuations

[yellow]Graham's Formula:[/yellow]
  Intrinsic Value = EPS × (8.5 + 2g)
  
  Where:
    8.5 = Base P/E for no-growth company
    g   = Expected annual growth rate

  Margin of Safety = (Intrinsic - Price) / Intrinsic × 100

[yellow]Rating Scale:[/yellow]
  MOS ≥50%: STRONG VALUE 💎💎
  MOS ≥40%: EXCELLENT VALUE 💎
  MOS ≥30%: GOOD VALUE 🟢
  MOS ≥20%: FAIR VALUE 🟡
  MOS <20%: OVERVALUED 🔴

[yellow]Examples:[/yellow]
  stockeye mos analyze --min-mos 40
  stockeye mos scan RELIANCE.NS
  stockeye mos analyze --conservative --export
        """)
    
    elif command == "watch":
        console.print("""
[bold cyan]📋 WATCHLIST MANAGEMENT[/bold cyan]

Manage your personal stock watchlist.

[yellow]Commands:[/yellow]

1. [green]stockeye watch add SYMBOL1 SYMBOL2 ...[/green]
   Add one or more symbols to watchlist
   
   Example:
     stockeye watch add RELIANCE.NS TCS.NS INFY.NS

2. [green]stockeye watch remove SYMBOL1 SYMBOL2 ...[/green]
   Remove symbols from watchlist
   
   Example:
     stockeye watch remove RELIANCE.NS

3. [green]stockeye watch list[/green]
   Display current watchlist
   
4. [green]stockeye watch clear[/green]
   Clear entire watchlist (with confirmation)

[yellow]Symbol Format:[/yellow]
  NSE stocks: Add .NS suffix (e.g., RELIANCE.NS)
  BSE stocks: Add .BO suffix (e.g., RELIANCE.BO)

[yellow]Watchlist Features:[/yellow]
  • Persistent storage (survives container restarts)
  • Automatic duplicate prevention
  • Case-insensitive symbol matching
  • Bulk add/remove support
        """)
    
    else:
        console.print(f"[yellow]No detailed help available for '{command}'[/yellow]\n")
        console.print("Available commands: analyze, scan, mos, watch, version, help")
        console.print("\nUse [cyan]stockeye help[/cyan] for general help")


@app.command()
def analyze(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed analysis")
):
    """
    🎯 Run comprehensive analysis on watchlist
    
    Analyzes stocks with technical + fundamental indicators,
    enhanced with Indian market intelligence (VIX, calendar effects, etc.)
    """
    run(detailed=detailed)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version_flag: bool = typer.Option(None, "--version", "-v", help="Show version"),
):
    """
    StockEye CLI - Advanced Stock Analysis for Indian Markets
    
    Enhanced with Indian market-specific indicators:
    • India VIX integration
    • Bollinger Bands & Supertrend
    • Sector volatility adjustments
    • Calendar effects (Budget, Dec rally)
    • Market regime detection
    """
    if version_flag:
        console.print(f"{__app_name__} version {__version__}")
        raise typer.Exit()
    
    # If no command is provided, show welcome screen
    if ctx.invoked_subcommand is None:
        console.print(f"""
╔══════════════════════════════════════════════════════════════╗
║                  🚀 StockEye CLI v{__version__}                      ║
║          Advanced Indian Stock Market Analysis Tool          ║
╚══════════════════════════════════════════════════════════════╝

[bold cyan]🎯 Quick Commands:[/bold cyan]

  [green]stockeye analyze[/green]              Analyze your watchlist
  [green]stockeye scan strong-buys[/green]     Find top opportunities
  [green]stockeye mos analyze[/green]          Graham value analysis
  [green]stockeye watch add SYMBOL[/green]     Add to watchlist

[bold cyan]📖 Help & Info:[/bold cyan]

  [green]stockeye help[/green]                 Show detailed help
  [green]stockeye version[/green]              Show version info
  [green]stockeye --help[/green]               Show all commands

[bold cyan]🇮🇳 Indian Market Features:[/bold cyan]

  ✓ India VIX volatility context
  ✓ Bollinger Bands & Supertrend
  ✓ Sector-specific adjustments
  ✓ Calendar effects analysis
  ✓ Enhanced F-Score (12 points)

[dim]First time? Try:[/dim]
  [cyan]stockeye help[/cyan]           - Detailed guide
  [cyan]stockeye scan strong-buys[/cyan] - Find opportunities
        """)


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
