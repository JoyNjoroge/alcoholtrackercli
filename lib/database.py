from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, DrinkEntry
from typing import List
import datetime

engine = create_engine('sqlite:///drinks.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()


Base.metadata.create_all(engine)

def insert_drink(entry: DrinkEntry):
    count = session.query(DrinkEntry).count()
    entry.position = count
    session.add(entry)
    session.commit()

def get_all_drinks() -> List[DrinkEntry]:
    return session.query(DrinkEntry).order_by(DrinkEntry.position).all()

def delete_drink(position: int):
    drink = session.query(DrinkEntry).filter_by(position=position).first()
    if drink:
        session.delete(drink)
        # Update positions of subsequent entries
        subsequent = session.query(DrinkEntry).filter(DrinkEntry.position > position).all()
        for d in subsequent:
            d.position -= 1
        session.commit()

def update_drink(position: int, drink: str = None, category: str = None):
    entry = session.query(DrinkEntry).filter_by(position=position).first()
    if entry:
        if drink:
            entry.drink = drink
        if category:
            entry.category = category
        session.commit()

def consume_drink(position: int):
    entry = session.query(DrinkEntry).filter_by(position=position).first()
    if entry:
        entry.status = 2
        entry.date_consumed = datetime.datetime.now()
        session.commit()