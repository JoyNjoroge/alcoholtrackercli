# model.py
import datetime

class DrinkEntry:
    def __init__(self, drink, category, quantity=1, volume_oz=None,
                 date_added=None, date_consumed=None, status=None):
        self.drink = drink
        self.category = category
        self.quantity = quantity
        self.volume_oz = volume_oz
        self.date_added = date_added if date_added else datetime.datetime.now()
        self.date_consumed = date_consumed
        self.status = status if status else 1
        
    def __repr__(self) -> str:
        return f"({self.drink}, {self.category}, {self.quantity}x{self.volume_oz}oz, {self.status})"

class UserProfile:
    def __init__(self, name, gender, weight):
        self.name = name
        self.gender = gender
        self.weight = weight
        self.id = None