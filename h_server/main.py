from fastapi import FastAPI, HTTPException, Request
from models import Base, RaceDay, Race, Mode0Races, Mode2Races, Drivers
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Initialize the database
Base.metadata.create_all(bind=engine)

@app.post("/upload-data/")
async def upload_data(request: Request):
    data = await request.json()
    db = SessionLocal()
    for a in data:
        date = a[0]["race_config"]["DATE"]
        title = a[0]["race_config"]["TITLE_1"]
        raceday = db.query(RaceDay).filter(and_(RaceDay.date == date, RaceDay.title == title)).first()
        
        if raceday is None:
            new_item = RaceDay(date=date, title=title)
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            raceday_id = new_item.id
        else:
            raceday_id = raceday.id

        title_2 = a[0]["race_config"]["TITLE_2"]
        mode = a[0]["race_config"]["MODE"]
        heats = a[0]["race_config"]["HEATS"]
        race = db.query(Race).filter(and_(Race.raceday_id == raceday_id, Race.title == title_2, Race.mode == int(mode), Race.heats == int(heats))).first()
        
        if race is None:
            new_race = Race(raceday_id=raceday_id, title=title_2, mode=mode, heats=heats)
            db.add(new_race)
            db.commit()
            db.refresh(new_race)
        
        
        for b in a[1]['drivers']:
            first_name = b["first_name"]
            last_name = b["last_name"]
            club = b["club"]

            race = db.query(Drivers).filter(and_(Drivers.first_name == first_name, Drivers.last_name == last_name)).first()
            if race == None:
                new_entry = Drivers(first_name=first_name, last_name=last_name, club=club)
                db.add(new_entry)
                db.commit()
                db.refresh(new_entry)

        if int(mode) == 0:
            print("asssd")
        elif int(mode) == 2:
            print([1])
            print("blabla")

    return {"message": "Data uploaded successfully"}
