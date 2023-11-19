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

class Mode0Races(Base):
    __tablename__ = 'mode0races'
    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'))
    d1_finishtime = Column(Integer)
    d1_inter_1 = Column(Integer)
    d1_inter_2 = Column(Integer)
    d1_penalty = Column(Integer)  
    d1_speed = Column(Integer)
    d1_vehicle = Column(String)
    race = relationship("Race")

class Mode2Races(Mode0Races):
    __tablename__ = 'mode2races'
    id = Column(Integer, ForeignKey('mode0races.id'), primary_key=True)
    d2_finishtime = Column(Integer)
    d2_inter_1 = Column(Integer)
    d2_inter_2 = Column(Integer)
    d2_penalty = Column(Integer) 
    d2_speed = Column(Integer)
    d2_vehicle = Column(String)

