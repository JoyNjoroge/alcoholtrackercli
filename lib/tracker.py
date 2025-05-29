import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn
from model import DrinkEntry, UserProfile
from database import (
    insert_drink, get_all_drinks, delete_drink, update_drink,
    consume_drink, get_weekly_consumption, get_daily_consumption,
    get_last_hours_consumption, check_warning, get_user_profile,
    create_user_profile, update_user_profile
)
from units import convert_to_oz
import datetime

console = Console()
app = typer.Typer()

STANDARD_DRINKS = {
    "Beer": 12,
    "Wine": 5,
    "Spirit": 1.5,
    "Cocktail": 8,
    "Other": 1.5
}

def calculate_bac(gender, weight_kg, total_oz, hours):
    """Calculate estimated BAC using Widmark formula"""
    r = 0.68 if gender == "male" else 0.55
    metabolism = 0.015 * hours
    bac = (total_oz * 0.075) / (weight_kg * r) - metabolism
    return max(0, bac)

def ensure_user_profile():
    """Ensure user profile exists or create one"""
    profile = get_user_profile()
    if not profile:
        console.print("[bold yellow]Welcome to Alcohol Tracker![/bold yellow] Let's set up your profile.")
        name = typer.prompt("Your name")
        gender = typer.prompt("Gender (male/female)", type=str).lower()
        while gender not in ["male", "female"]:
            console.print("Please enter 'male' or 'female'")
            gender = typer.prompt("Gender (male/female)", type=str).lower()
        
        weight = typer.prompt("Weight (kg)", type=float)
        
        profile = UserProfile(name=name, gender=gender, weight=weight)
        create_user_profile(profile)
        console.print(f"[bold green]Profile created for {name}![/bold green]")
    return profile

@app.command(short_help='Add a drink entry')
def add(
    drink: str = typer.Option(None, help="Name of the drink"),
    category: str = typer.Option(None, help="Drink category (e.g., Beer, Wine, Spirit)"),
    quantity: int = typer.Option(None, help="Number of drinks consumed"),
    amount: float = typer.Option(None, help="Amount of drink (number)"),
    unit: str = typer.Option(None, help="Unit of measurement (oz, ml, l)")
):
    profile = ensure_user_profile()
    
    if drink is None:
        drink = typer.prompt("Enter drink name")
    if category is None:
        category = typer.prompt("Enter drink category", type=str, 
                              default="Beer", show_choices=True, 
                              choices=list(STANDARD_DRINKS.keys()))
    if quantity is None:
        quantity = typer.prompt("Enter number of drinks", type=int, default=1)
    if amount is None:
        amount = typer.prompt("Enter drink amount", type=int)
    if unit is None:
        unit = typer.prompt("Enter unit (oz/ml/l)", type=str, default="oz")
        if unit not in ["oz", "ml", "l"]:
            typer.echo("Invalid unit. Please enter oz, ml, or l.")
            raise typer.Exit()



    volume_oz = convert_to_oz(amount, unit)
    if category in STANDARD_DRINKS:
        volume_oz = STANDARD_DRINKS[category] * quantity
    
    entry = DrinkEntry(drink, category, quantity, volume_oz)
    insert_drink(entry, profile.id)
    typer.echo(f"Added: {quantity}x {drink} ({volume_oz:.1f}oz total) in category '{category}'")
    
    check_limits_and_warn(profile)
    show()

def check_limits_and_warn(profile):
    """Check all limits and show appropriate warnings"""
    weekly_consumed = get_weekly_consumption(profile.id)
    daily_consumed = get_daily_consumption(profile.id)
    last_4h_consumed = get_last_hours_consumption(profile.id, hours=4)
    
    weekly_limit = 14 if profile.gender == "male" else 7
    daily_limit = 4 if profile.gender == "male" else 3
    binge_limit = 3 if profile.gender == "male" else 2
    
    if weekly_consumed > weekly_limit:
        console.print(f"[bold red]WEEKLY LIMIT EXCEEDED:[/bold red] {weekly_consumed:.1f}/{weekly_limit}oz")
    elif weekly_consumed > weekly_limit * 0.8:
        console.print(f"[bold yellow]Weekly Warning:[/bold yellow] {weekly_consumed:.1f}/{weekly_limit}oz ({weekly_consumed/weekly_limit*100:.0f}%)")
    
    if daily_consumed > daily_limit:
        console.print(f"[bold red]DAILY LIMIT EXCEEDED:[/bold red] {daily_consumed:.1f}/{daily_limit}oz today")
    
    if last_4h_consumed > binge_limit:
        console.print(f"[bold red]BINGE WARNING:[/bold red] {last_4h_consumed:.1f}oz in last 4 hours")
    
    if daily_consumed > 0:
        bac = calculate_bac(profile.gender, profile.weight, daily_consumed, 1)
        console.print(f"Estimated BAC: {bac:.3f}%")
        if bac > 0.08:
            console.print("[bold red]LEGAL WARNING:[/bold red] Above legal driving limit (0.08%)")
        elif bac > 0.05:
            console.print("[bold yellow]CAUTION:[/bold yellow] Impaired driving possible (0.05%)")

@app.command(short_help='Delete a drink entry by ID')
def delete(entry_id: int):
    delete_drink(entry_id)
    typer.echo(f"Deleted entry ID {entry_id}")
    show()

@app.command(short_help='Update a drink entry')
def update(entry_id: int, drink: str = None, category: str = None):
    update_drink(entry_id, drink, category)
    typer.echo(f"Updated entry ID {entry_id}")
    show()

@app.command(short_help='Mark a drink as consumed')
def consume(entry_id: int):
    consume_drink(entry_id)
    typer.echo(f"Marked entry ID {entry_id} as consumed")
    profile = ensure_user_profile()
    check_limits_and_warn(profile)
    show()

@app.command(short_help='Show all drink entries')
def show():
    profile = ensure_user_profile()
    drinks = get_all_drinks(profile.id)
    
    weekly_consumed = get_weekly_consumption(profile.id)
    weekly_limit = 14 if profile.gender == "male" else 7
    
    console.print(f"[bold magenta]Alcohol Tracker[/bold magenta] 🥂 [dim]for {profile.name}[/dim]")
    console.print(f"[bold]Gender:[/bold] {profile.gender.capitalize()} | [bold]Weight:[/bold] {profile.weight}kg")
    
    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(bar_width=50),
        "[progress.percentage]{task.percentage:>3.0f}%"
    )
    
    with progress:
        task = progress.add_task(
            "[cyan]Weekly consumption:", 
            total=weekly_limit
        )
        progress.update(
            task, 
            completed=min(weekly_consumed, weekly_limit),
            description=f"Weekly: {weekly_consumed:.1f}/{weekly_limit}oz"
        )
    
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Drink", min_width=15)
    table.add_column("Category", min_width=12)
    table.add_column("Qty", justify="right")
    table.add_column("Vol (oz)", justify="right")
    table.add_column("When", min_width=12)
    table.add_column("Consumed", justify="center")

    for entry in drinks:
        consumed_str = "✅" if entry.status == 2 else "❌"
        when_str = entry.date_consumed.strftime("%b %d %H:%M") if entry.date_consumed else "Not consumed"
        table.add_row(
            str(entry.id),
            entry.drink,
            entry.category,
            str(entry.quantity),
            f"{entry.volume_oz:.1f}",
            when_str,
            consumed_str
        )

    console.print(table)
    check_limits_and_warn(profile)

@app.command(short_help='Update your profile')
def profile():
    current = ensure_user_profile()
    console.print("[bold]Current Profile:[/bold]")
    console.print(f"Name: {current.name}")
    console.print(f"Gender: {current.gender}")
    console.print(f"Weight: {current.weight} kg")
    
    name = typer.prompt("New name", default=current.name)
    gender = typer.prompt("Gender (male/female)", default=current.gender)
    weight = typer.prompt("Weight (kg)", type=float, default=current.weight)
    
    update_user_profile(name, gender, weight)
    console.print("[bold green]Profile updated![/bold green]")

if __name__ == "__main__":
    app()

