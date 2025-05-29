from database import (
    create_user_profile, get_user_profile, insert_drink,
    consume_drink, get_all_drinks, check_warning,
    delete_drink, update_drink, update_user_profile
)
from model import DrinkEntry, UserProfile
import time

def test_debug_flow():
    print("---- Creating Test User ----")
    profile = UserProfile(name="TestUser", gender="male", weight=75)
    user = create_user_profile(profile)
    profile.id = user.id
    print(f"User created: {user.name} (ID: {user.id})")

    print("\n---- Adding Drinks ----")
    drink1 = DrinkEntry(drink="Beer", category="Alcoholic", quantity=2, volume_oz=12)
    drink2 = DrinkEntry(drink="Whiskey", category="Alcoholic", quantity=1, volume_oz=5)
    insert_drink(drink1, user.id)
    insert_drink(drink2, user.id)
    print("Drinks added.")

    print("\n---- All Drinks ----")
    all_drinks = get_all_drinks(user.id)
    for d in all_drinks:
        print(f"{d.id}: {d.drink} - {d.quantity}x{d.volume_oz}oz - Status: {d.status}")

    print("\n---- Consuming Drinks ----")
    for d in all_drinks:
        consume_drink(d.id)
        time.sleep(1)  # ensure different timestamps

    print("\n---- After Consumption ----")
    all_drinks = get_all_drinks(user.id)
    for d in all_drinks:
        print(f"{d.id}: {d.drink} - Consumed: {d.date_consumed} - Status: {d.status}")

    print("\n---- Warning Check ----")
    warning = check_warning(user.id)
    print(warning)

    print("\n---- Updating User Profile ----")
    updated_user = update_user_profile("TestUser", "male", 70)
    print(f"Updated weight: {updated_user.weight}kg")

    print("\n---- Cleaning up: Deleting all drinks ----")
    for d in get_all_drinks(user.id):
        delete_drink(d.id)
    print("Clean-up complete.")

if __name__ == "__main__":
    test_debug_flow()
