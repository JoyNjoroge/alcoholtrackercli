import typer
from rich.console import Console
from rich.table import Table
from model import DrinkEntry
from database import (
    get_all_drinks,
    delete_drink,
    insert_drink,
    consume_drink,
    update_drink
)

console = Console()
app = typer.Typer()

@app.command(short_help='Add a drink entry')
def add(drink: str, category: str):
    typer.echo(f"Adding drink: {drink}, category: {category}")
    entry = DrinkEntry(drink=drink, category=category)
    insert_drink(entry)
    show()

@app.command(short_help='Delete a drink entry by its position')
def delete(position: int):
    typer.echo(f"Deleting entry at position {position}")
    delete_drink(position - 1)  # user-facing positions start at 1
    show()

@app.command(short_help='Update a drink or its category')
def update(position: int, drink: str = None, category: str = None):
    typer.echo(f"Updating entry at position {position}")
    update_drink(position - 1, drink, category)
    show()

@app.command(short_help='Mark a drink as consumed')
def consume(position: int):
    typer.echo(f"Marking entry at position {position} as consumed")
    consume_drink(position - 1)
    show()

@app.command()
def show():
    entries = get_all_drinks()
    console.print("[bold magenta]Alcohol Tracker[/bold magenta] 🥂")

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("#", style="dim", width=6)
    table.add_column("Drink", min_width=20)
    table.add_column("Category", min_width=12, justify="right")
    table.add_column("Consumed", min_width=12, justify="right")

    def get_category_color(category):
        COLORS = {
            'Beer': 'yellow',
            'Wine': 'red',
            'Whiskey': 'magenta',
            'Vodka': 'cyan',
            'Other': 'white'
        }
        return COLORS.get(category, 'white')

    for idx, entry in enumerate(entries, start=1):
        color = get_category_color(entry.category)
        status = '✅' if entry.status == 2 else '❌'
        table.add_row(str(idx), entry.drink, f'[{color}]{entry.category}[/{color}]', status)

    console.print(table)

if __name__ == "__main__":
    app()
