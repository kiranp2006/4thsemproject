from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///agrirent.db', echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)  # store hashed
    email = Column(String)
    role = Column(String)
    location = Column(String)

class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    category = Column(String)
    description = Column(String)
    daily_rate = Column(Float)
    location = Column(String)
    available_from = Column(Date)
    available_to = Column(Date)
    image_url = Column(String)

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'))
    renter_id = Column(Integer, ForeignKey('users.id'))
    start_date = Column(Date)
    end_date = Column(Date)
    total_cost = Column(Float)
    status = Column(String)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
