from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from concurrent.futures import ThreadPoolExecutor, as_completed
from stockeye.services.analyzer import analyze_symbol
from stockeye.storage import load_watchlist
from stockeye.config import MAX_WORKERS
from stockeye.core.rating import get_cross_display

console = Console()

def format_rsi(rsi, rsi_signal):
    """Format RSI display with color coding"""
    if rsi is None or rsi_signal is None:
        return "N/A"
    
    if rsi_signal == "OVERSOLD":
        return f"[green]{rsi:.1f} ↓[/green]"
    elif rsi_signal == "OVERBOUGHT":
        return f"[red]{rsi:.1f} ↑[/red]"
    else:
        return f"[yellow]{rsi:.1f}[/yellow]"

def format_macd(macd_signal):
    """Format MACD signal display"""
    if macd_signal == "BULLISH":
        return "[green]BULL ↑[/green]"
    elif macd_signal == "BEARISH":
        return "[red]BEAR ↓[/red]"
    elif macd_signal == "NEUTRAL":
        return "[yellow]NEUT[/yellow]"
    return "N/A"

def format_volume(volume_signal):
    """Format volume signal display"""
    if volume_signal == "HIGH":
        return "[green]HIGH 📈[/green]"
    elif volume_signal == "LOW":
        return "[red]LOW 📉[/red]"
    elif volume_signal == "NORMAL":
        return "[yellow]NORM[/yellow]"
    return "N/A"


def run(detailed=False):
    """
    Run analysis on watchlist symbols
    
    Args:
        detailed: If True, show additional technical indicator details
    """
    symbols = load_watchlist()
    
    if not symbols:
        console.print(Panel.fit(
            "[yellow]Watchlist is empty![/yellow]\n\n"
            "Add symbols using:\n"
            "[cyan]stockeye watch add SYMBOL1 SYMBOL2[/cyan]",
            title="No Symbols to Analyze"
        ))
        return
    
    # Create analysis table
    table = Table(
        title=f"📊 Advanced Stock Analysis ({len(symbols)} stocks)",
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Stock", style="cyan", no_wrap=True)
    table.add_column("Price", justify="right")
    table.add_column("DMA50", justify="right", style="dim")
    table.add_column("DMA200", justify="right", style="dim")
    table.add_column("RSI", justify="center")
    table.add_column("MACD", justify="center")
    table.add_column("Volume", justify="center")
    table.add_column("F-Score", justify="center")
    table.add_column("Cross", justify="left", no_wrap=True)
    table.add_column("Rating", justify="center", style="bold")

    results = []
    
    # Progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Analyzing stocks...", total=len(symbols))

        # Use ThreadPoolExecutor with 8 workers
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Map symbols to futures
            future_to_sym = {executor.submit(analyze_symbol, sym): sym for sym in symbols}
            
            for future in as_completed(future_to_sym):
                sym = future_to_sym[future]
                progress.update(task, description=f"[cyan]Completed analyzing {sym}...")
                
                try:
                    res = future.result()
                    results.append(res)
                except Exception as e:
                    results.append({"sym": sym, "error": str(e)})
                
                progress.advance(task)

    # Process results and add to table (sorted by symbol name)
    for res in sorted(results, key=lambda x: x['sym']):
        sym = res['sym']
        if res.get("error"):
            console.print(f"[red]Error processing {sym}: {res['error']}[/red]")
            table.add_row(sym, "ERROR", "-", "-", "-", "-", "-", "-", "-", "N/A")
            continue

        # Format displays
        cross_display = get_cross_display(res['cross_info'])
        price_style = "green" if res['close'] > res['dma50'] else "red"
        
        table.add_row(
            sym,
            f"[{price_style}]{res['close']:.2f}[/{price_style}]",
            f"{res['dma50']:.2f}" if res['dma50'] else "N/A",
            f"{res['dma200']:.2f}" if res['dma200'] else "N/A",
            format_rsi(res['rsi'], res['rsi_signal']),
            format_macd(res['macd_signal']),
            format_volume(res['volume_signal']),
            str(res['fscore']),
            cross_display,
            res['decision']
        )

    console.print()
    console.print(table)
    console.print()
    
    # Enhanced legend
    legend = Panel(
        "[bold]Ratings:[/bold]\n"
        "[green]🟢🟢 STRONG BUY[/green] - Exceptional opportunity\n"
        "[green]🟢 BUY[/green] - Good entry point\n"
        "[blue]🔵 ADD[/blue] - Good for adding to position\n"
        "[yellow]🟡 HOLD[/yellow] - Maintain position\n"
        "[orange]🟠 REDUCE[/orange] - Consider reducing\n"
        "[red]🔴 SELL[/red] - Sell position\n"
        "[red]🔴🔴 STRONG SELL[/red] - Urgent sell\n"
        "[bold]RSI:[/bold] [green]<30 Oversold[/green] | "
        "[yellow]30-70 Neutral[/yellow] | "
        "[red]>70 Overbought[/red]\n"
        "[bold]MACD:[/bold] [green]BULL[/green] = Bullish momentum | "
        "[red]BEAR[/red] = Bearish momentum | "
        "[yellow]NEUT[/yellow] = Neutral\n"
        "[bold]Volume:[/bold] [green]HIGH[/green] = >1.5x average | "
        "[yellow]NORM[/yellow] = Normal | "
        "[red]LOW[/red] = <0.5x average\n"
        "[bold]Cross:[/bold] [green]Golden[/green] = DMA50 > DMA200 (Bullish) | "
        "[red]Death[/red] = DMA50 < DMA200 (Bearish)",
        title="📖 Legend",
        border_style="dim"
    )
    console.print(legend)
    