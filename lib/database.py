# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class Drink(Base):
    __tablename__ = 'drinks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    drink = Column(String)
    category = Column(String)
    quantity = Column(Integer)
    volume_oz = Column(Float)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    date_consumed = Column(DateTime)
    status = Column(Integer, default=1)
    
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    weight = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

engine = create_engine('sqlite:///alcohol_tracker.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def insert_drink(entry, user_id):
    drink = Drink(
        user_id=user_id,
        drink=entry.drink,
        category=entry.category,
        quantity=entry.quantity,
        volume_oz=entry.volume_oz,
        status=entry.status
    )
    session.add(drink)
    session.commit()

def get_all_drinks(user_id):
    return session.query(Drink).filter_by(user_id=user_id).order_by(Drink.date_added.desc()).all()

def delete_drink(entry_id):
    entry = session.query(Drink).filter_by(id=entry_id).first()
    if entry:
        session.delete(entry)
        session.commit()

def update_drink(entry_id, drink=None, category=None):
    entry = session.query(Drink).filter_by(id=entry_id).first()
    if entry:
        if drink:
            entry.drink = drink
        if category:
            entry.category = category
        session.commit()

def consume_drink(entry_id):
    entry = session.query(Drink).filter_by(id=entry_id).first()
    if entry:
        entry.status = 2
        entry.date_consumed = datetime.datetime.utcnow()
        session.commit()

def get_weekly_consumption(user_id):
    one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    entries = session.query(Drink).filter(
        Drink.user_id == user_id,
        Drink.status == 2,
        Drink.date_consumed >= one_week_ago
    ).all()
    return sum(e.volume_oz * e.quantity for e in entries)

def get_daily_consumption(user_id):
    today = datetime.datetime.utcnow().date()
    entries = session.query(Drink).filter(
        Drink.user_id == user_id,
        Drink.status == 2,
        func.date(Drink.date_consumed) == today
    ).all()
    return sum(e.volume_oz * e.quantity for e in entries)

def get_last_hours_consumption(user_id, hours):
    time_threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
    entries = session.query(Drink).filter(
        Drink.user_id == user_id,
        Drink.status == 2,
        Drink.date_consumed >= time_threshold
    ).all()
    return sum(e.volume_oz * e.quantity for e in entries)

def get_user_profile():
    return session.query(User).first()

def create_user_profile(profile):
    user = User(
        name=profile.name,
        gender=profile.gender,
        weight=profile.weight
    )
    session.add(user)
    session.commit()
    return user

def update_user_profile(name, gender, weight):
    user = session.query(User).first()
    if user:
        user.name = name
        user.gender = gender
        user.weight = weight
        session.commit()
    return user

def check_warning(user_id):
    """Check all warning conditions and return a message"""
    weekly_consumed = get_weekly_consumption(user_id)
    daily_consumed = get_daily_consumption(user_id)
    last_4h_consumed = get_last_hours_consumption(user_id, hours=4)
    
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return "No user profile found"
    
    weekly_limit = 14 if user.gender == "male" else 7
    daily_limit = 4 if user.gender == "male" else 3
    binge_limit = 3 if user.gender == "male" else 2
    
    warnings = []
    
    if weekly_consumed > weekly_limit:
        warnings.append(f"WEEKLY LIMIT EXCEEDED: {weekly_consumed:.1f}/{weekly_limit}oz")
    elif weekly_consumed > weekly_limit * 0.8:
        warnings.append(f"Approaching weekly limit: {weekly_consumed:.1f}/{weekly_limit}oz")
    
    if daily_consumed > daily_limit:
        warnings.append(f"DAILY LIMIT EXCEEDED: {daily_consumed:.1f}/{daily_limit}oz")
    
    if last_4h_consumed > binge_limit:
        warnings.append(f"BINGE WARNING: {last_4h_consumed:.1f}oz in last 4 hours")
    
    if daily_consumed > 0:
        bac = calculate_bac(user.gender, user.weight, daily_consumed, 1)
        if bac > 0.08:
            warnings.append(f"LEGAL WARNING: Estimated BAC {bac:.3f}% (above 0.08%)")
        elif bac > 0.05:
            warnings.append(f"CAUTION: Estimated BAC {bac:.3f}% (impaired driving possible)")
    
    return "\n".join(warnings) if warnings else "Within safe consumption limits"

def calculate_bac(gender, weight_kg, total_oz, hours):
    """Calculate estimated BAC using Widmark formula"""
    r = 0.68 if gender == "male" else 0.55
    metabolism = 0.015 * hours
    bac = (total_oz * 0.075) / (weight_kg * r) - metabolism
    return max(0, bac)