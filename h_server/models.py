from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RaceDay(Base):
    __tablename__ = 'racedays'
    id = Column(Integer, primary_key=True)
    date = Column(String)
    title = Column(String)
    races = relationship("Race", back_populates="raceday")

class Drivers(Base):
    __tablename__ = 'drivers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    club = Column(String)

class Race(Base):
    __tablename__ = 'races'
    id = Column(Integer, primary_key=True)
    raceday_id = Column(Integer, ForeignKey('racedays.id'))
    title = Column(String)
    heats = Column(Integer)
    mode = Column(Integer)
    raceday = relationship("RaceDay", back_populates="races")

class Run(Base):
    __tablename__ = 'run'
    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'))
    driver_id = Column(Integer, ForeignKey('drivers.id'))
    run_id = Column(Integer)
    pair_id = Column(Integer)
    finishtime = Column(Integer)
    inter_1 = Column(Integer)
    inter_2 = Column(Integer)
    penalty = Column(Integer)  
    speed = Column(Integer)
    vehicle = Column(String)
    status = Column(Integer) 
    race = relationship("Race")
    drivers = relationship("Drivers")