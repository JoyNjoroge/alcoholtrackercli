from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class DrinkEntry(Base):
    _tablename_ = 'drinks'

    id = Column(Integer, primary_key=True)
    drink = Column(String)
    category = Column(String)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    date_consumed = Column(DateTime, nullable=True)
    status = Column(Integer, default=1)  # 1 = not consumed, 2 = consumed
    position = Column(Integer)

    def _repr_(self):
        return f"<DrinkEntry(drink={self.drink}, category={self.category}, date_added={self.date_added}, status={self.status})>"