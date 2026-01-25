from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from config import PERIOD, DMA_SHORT, DMA_LONG
from core.data_fetcher import fetch_stock
from core.indicators import (
    add_dma, add_rsi, add_macd, analyze_volume,
    detect_cross_age, cross_signal,
    get_rsi_signal, get_macd_signal, get_volume_signal
)
from core.fundamentals import fundamental_score
from core.rating import rating, get_cross_display
from storage import load_watchlist

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
            "[cyan]docker compose run stock-cli watch add SYMBOL1 SYMBOL2[/cyan]",
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
    table.add_column("Cross", justify="left")
    table.add_column("Rating", justify="center", style="bold")
    
    # Progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Analyzing stocks...", total=len(symbols))
        
        for sym in symbols:
            try:
                progress.update(task, description=f"[cyan]Analyzing {sym}...")
                
                # Fetch data
                df, info = fetch_stock(sym, PERIOD)
                
                # Add all indicators
                df = add_dma(df, DMA_SHORT, DMA_LONG)
                df = add_rsi(df)
                df = add_macd(df)
                df = analyze_volume(df)
                
                last = df.iloc[-1]
                fscore = fundamental_score(info)
                
                # Get indicator signals
                rsi = last.get("RSI")
                rsi_signal = get_rsi_signal(rsi)
                
                macd_val = last.get("MACD")
                macd_sig = last.get("MACD_Signal")
                macd_hist = last.get("MACD_Hist")
                macd_signal = get_macd_signal(macd_val, macd_sig, macd_hist)
                
                volume_ratio = last.get("Volume_Ratio")
                volume_signal = get_volume_signal(volume_ratio)
                
                # Detect cross and calculate age
                cross_info = detect_cross_age(df)
                
                # Check for immediate cross
                immediate_cross = cross_signal(df)
                if immediate_cross:
                    cross_info['type'] = immediate_cross
                    cross_info['days_ago'] = 0
                
                # Generate rating with all indicators
                decision = rating(
                    last["Close"], 
                    last["DMA50"], 
                    last["DMA200"], 
                    fscore, 
                    cross_info,
                    rsi,
                    macd_signal,
                    volume_signal
                )
                
                # Format displays
                cross_display = get_cross_display(cross_info)
                price_style = "green" if last["Close"] > last["DMA50"] else "red"
                
                table.add_row(
                    sym,
                    f"[{price_style}]{last['Close']:.2f}[/{price_style}]",
                    f"{last['DMA50']:.2f}" if last['DMA50'] else "N/A",
                    f"{last['DMA200']:.2f}" if last['DMA200'] else "N/A",
                    format_rsi(rsi, rsi_signal),
                    format_macd(macd_signal),
                    format_volume(volume_signal),
                    str(fscore),
                    cross_display,
                    decision
                )
                
                progress.advance(task)
                
            except Exception as e:
                console.print(f"[red]Error processing {sym}: {str(e)}[/red]")
                table.add_row(sym, "ERROR", "-", "-", "-", "-", "-", "-", "-", "N/A")
                progress.advance(task)
    
    console.print()
    console.print(table)
    console.print()
    
    # Enhanced legend
    legend = Panel(
        "[bold]Ratings:[/bold] [green]🟢 BUY[/green] - Strong bullish | "
        "[yellow]🟡 HOLD[/yellow] - Mixed signals | "
        "[red]🔴 SELL[/red] - Weak/bearish\n\n"
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