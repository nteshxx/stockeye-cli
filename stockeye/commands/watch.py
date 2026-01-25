import typer
from rich.console import Console
from rich.table import Table
from stockeye.storage import load_watchlist, add_symbols, remove_symbols, clear_watchlist

watch_app = typer.Typer(help="Manage watchlist (add/remove/list/clear)")
console = Console()

@watch_app.command("add")
def add(symbols: list[str]):
    """Add symbols to watchlist"""
    added = add_symbols(symbols)
    
    if added:
        console.print(f"[green]✓[/green] Added {len(added)} symbol(s): {', '.join(added)}")
    else:
        console.print("[yellow]![/yellow] All symbols already in watchlist")
    
    show_list()


@watch_app.command("remove")
def remove(symbols: list[str]):
    """Remove symbols from watchlist"""
    removed = remove_symbols(symbols)
    
    if removed:
        console.print(f"[green]✓[/green] Removed {len(removed)} symbol(s): {', '.join(removed)}")
    else:
        console.print("[yellow]![/yellow] No symbols found in watchlist")
    
    show_list()


@watch_app.command("list")
def show_list():
    """Display current watchlist"""
    watchlist = load_watchlist()
    
    if not watchlist:
        console.print("[yellow]Watchlist is empty[/yellow]")
        return
    
    table = Table(title=f"📋 Watchlist ({len(watchlist)} symbols)")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Symbol", style="green")
    
    for idx, symbol in enumerate(watchlist, 1):
        table.add_row(str(idx), symbol)
    
    console.print(table)


@watch_app.command("clear")
def clear():
    """Clear entire watchlist"""
    if typer.confirm("Are you sure you want to clear the entire watchlist?"):
        clear_watchlist()
        console.print("[green]✓[/green] Watchlist cleared")
    else:
        console.print("[yellow]Cancelled[/yellow]")
