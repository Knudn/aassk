from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Base, RaceDay, Race, Run, Drivers
from sqlalchemy import create_engine, and_, text
from sqlalchemy.orm import sessionmaker, Session
import queries
import hashlib
import math

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


app = FastAPI()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Initialize the database
Base.metadata.create_all(bind=engine)

app.state.db_cache_dict = {}


def db_cache():
    async def cache_logic(query=None, data=None):
        b64_hash = hashlib.md5(query.encode()).hexdigest()
        if query and b64_hash in app.state.db_cache_dict:
            if app.state.db_cache_dict[b64_hash] == []:
                return [{"None":"None"}]
            return app.state.db_cache_dict[b64_hash]
        if data is not None:
            app.state.db_cache_dict[b64_hash] = data
        return None
    return cache_logic
    

def fix_names(first_name, last_name, club):
    if "é" in first_name:
        first_name = first_name.replace('é', 'e')

    if "é" in last_name:
        last_name = first_name.replace('é', 'e')

    if "Throsland" in last_name and "Vilde" in first_name:
        first_name = "Vilde"
        last_name = "Thorsland Lauen"

    if "Vilde Thorsland" in first_name:
        first_name = "Vilde"
        last_name = "Thorsland Lauen"
    
    if "Yngve" in first_name and "Ousdal" in last_name:
        first_name = "Yngve"
        last_name = "Ousdal"
    
    if "Sigurd S" in first_name:
        first_name = "Sigurd Selmer"

    if first_name == "Ole B":
        first_name = "Ole Bjørnestad"

    if last_name == "Håvorstad":
        last_name = "Håverstad"

    if first_name == "Maja Alexandra":
        first_name = "Maja Alexandra Egelandsdal" 
    
    if "Live Sunniva" in first_name:
        club = "Kongsberg & Numedal SNK"
    
    if first_name == "Fredrik Åsland":
        first_name = "Fredrik"
        last_name = "Åsland"
    
    if first_name == "Bjørnar" and last_name == "Bjørnestad":
        first_name = "Bjørnar Kongevold"
    
    if first_name == "Eline Åsland" and last_name == "Thorsland":
        first_name = "Eline"
        last_name = "Åsland Thorsland"
    
    if first_name == "Jørund" and last_name == "Åsland":
        first_name = "Jørund Haugland"
    if last_name == "Skeiebrok":
        last_name = "Skeibrok"

    if first_name == "Live Sunniva":
        club="Kongsberg & Numedal SNK"

    if first_name == "Live Sunniva ":
        first_name="Live Sunniva"

    if first_name == "Madelen E":
        first_name = "Madelen Egelandsdal"

    if first_name == "Preben" and last_name == "Knabenes":
        first_name = "Preben Bjørnestad"
        last_name = "Knabenes"

    name = first_name + " " + last_name 
    return name, club


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/get_drivers/")
async def get_drivers(db: Session = Depends(get_db)):
    query = queries.get_all_drivers()
    
    result = db.execute(text(query))
    rows = result.fetchall()
    # Convert each tuple into a dictionary
    results_list = [
        {
            "Name": row[1],
        } for row in rows
    ]

    return results_list

@app.get("/get_parallel_results/{driver_name}")
async def get_drivers(driver_name: str, db: Session = Depends(get_db), cache=Depends(db_cache)):
    if "é" in driver_name:
        driver_name = driver_name.replace("é","e")
        
    query = queries.get_parallel_driver_results_sql(driver_name)
    cache_state = await cache(query=query)
    if cache_state:
        return cache_state



    result = db.execute(text(query))
    rows = result.fetchall()



    # Convert each tuple into a dictionary
    
    
    results_list = [
        {
            "d1_name": row[0],
            "d2_name": row[1],
            "d1_result": row[2],
            "d2_result": row[3],
            "title_day": row[4],
            "title": row[5],
            "date": row[6],
            "d1_finishtime": row[7],
            "d2_finishtime": row[8],
            "d1_snowmobile": row[9],
            "d2_snowmobile": row[10],
        } for row in rows
    ]

    await cache(query=query, data=results_list)
    #return "None"
    return results_list

@app.get("/snowmobiles/{driver_name}")
async def snowmobiles(driver_name: str, db: Session = Depends(get_db), cache=Depends(db_cache)):
    query = queries.get_snowmobiles_sql(driver_name)
    cache_state = await cache(query=query)
    if cache_state:
        return cache_state

    result = db.execute(text(query))
    rows = result.fetchall()
    # Convert each tuple into a dictionary
    results_list = [
        {
            "snowmobile": row[1],
            "date": row[2],
            "raceday":row[3],
        } for row in rows
    ]

    await cache(query=query, data=results_list)

    return results_list

@app.get("/get_ladder_results/")
async def get_ladder_results(db: Session = Depends(get_db), cache=Depends(db_cache)):
    query = queries.get_ladder_results()

    cache_state = await cache(query=query)
    if cache_state:
        return cache_state

    result = db.execute(text(query))
    rows = result.fetchall()

    # Convert each tuple into a dictionary
    results_list = [
        {
            "race_id": row[0],
            "driver_name": row[1],
            "position": row[2],
            "race_name": row[3]
        } for row in rows
    ]
    race_id = {}
    for a in results_list:
        race_id[a["race_id"]] = []
    for a in results_list:
        if len(race_id[a["race_id"]]) == 0 and a["position"] == "3":
            race_id[a["race_id"]].append({a["driver_name"], "1", a["race_name"]})
        elif len(race_id[a["race_id"]]) == 1 and a["position"] == "4":
            race_id[a["race_id"]].append({a["driver_name"], "2", a["race_name"]})
        else:
            race_id[a["race_id"]].append({a["driver_name"], a["position"], a["race_name"]})
    
    await cache(query=query, data=results_list)
    return race_id


def calculate_position(race_results, driver_id, heats, drivername):
    highest_heat = 0
    heats = heats
    driver_pair = 0

    exclude_lst = []

    highest_heat = 0
    for b in race_results:

        if isinstance(b, int):
            if driver_id in race_results[b]:
                
                if b > highest_heat:
                    highest_heat = b
                    driver_pair = race_results[b][driver_id][2]
                    snowmobile = race_results[b][driver_id][3]
                    date_run = race_results[b][driver_id][4]

     
    sorted_results = sorted(race_results[highest_heat].items(), 
                            key=lambda x: (x[1][0] != 0, x[1][2] if highest_heat == heats else float('inf'), x[1][1]))   


    if highest_heat != heats:
        for t in sorted_results:
            if t[0] in race_results[highest_heat + 1]:
                exclude_lst.append(t[0])

    elif highest_heat == heats:
        if driver_pair == 1: 
            sorted_results = [item for item in sorted_results if item[1][2] != 2]
        if driver_pair == 2:
            sorted_results = [item for item in sorted_results if item[1][2] != 1]
    count = 0

    filtered_list = [item for item in sorted_results if item[0] not in exclude_lst]
    for b in filtered_list:

        count += 1
        if b[0] == driver_id:
            break

    if highest_heat == heats:
        if driver_pair == 2:
            placement = (count + len(exclude_lst) + 2)
        else:
            placement = (count + len(exclude_lst))
    else:
        placement = (count + len(exclude_lst))
    
    res = {
            "name": drivername,
            "title_1": race_results["title1"],
            "title_2": race_results["title2"],
            "position": placement,
            "date": date_run,
            "mode": 3,
            "snowmobile": snowmobile,
            "total_drivers": race_results["drivers"],
            #"finishtime": row[8],
        } 
    


    return res


@app.get("/get_ladder_placement_sql/{driver_name}")
async def get_ladder_placement_sql(driver_name: str, db: Session = Depends(get_db), cache=Depends(db_cache)):
    if "é" in driver_name:
        driver_name = driver_name.replace("é","e")

    query = queries.get_race_entries_for_driver(driver_name)
    

    
    print(driver_name)
    
    # Check the cache
    cache_state = await cache(query=query)
    if cache_state:
        return cache_state

    result = db.execute(text(query))
    rows = result.fetchall()
    events = {}
    driver_id = ""
    results_list = []

    for a in rows:        
        
        if a[0] not in events:
            events[a[0]] = {"drivers":0, "title1":a[3], "title2": a[1]}

        if a[6] == driver_name:
            driver_id = a[5]

        if a[9] == 1:
            events[a[0]]["drivers"] += 1

        if a[9] not in events[a[0]]:
            events[a[0]][a[9]] = {}


        events[a[0]][a[9]][a[5]] = [a[8],a[7],a[10],a[11],a[12]]
        
    for b in events:
        
        results_list.append(calculate_position(events[b], driver_id, math.ceil(math.log2(events[b]["drivers"])),driver_name))

    await cache(query=query, data=results_list)
    return results_list
    
@app.post("/upload-data/")
async def upload_data(request: Request):
    deletes_entries = []
    data = await request.json()
    db = SessionLocal()
    count = 1

    for a in data:
        count += 1
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
        heat = a[0]["race_config"]["HEAT"]
        race = db.query(Race).filter(and_(Race.raceday_id == raceday_id, Race.title == title_2, Race.mode == int(mode), Race.heats == int(heats))).first()
        
        if race is None:
            new_race = Race(raceday_id=raceday_id, title=title_2, mode=mode, heats=heats)
            db.add(new_race)
            db.commit()
            db.refresh(new_race)

        
        race_id = db.query(Race).filter(and_(Race.raceday_id == raceday_id, Race.title == title_2, Race.mode == int(mode), Race.heats == int(heats))).first()
        if race_id.id not in deletes_entries:
            existing_runs = db.query(Run).filter(Run.race_id == race_id.id).all()
            if existing_runs:
                for l in existing_runs:
                    db.delete(l)
                db.commit()
                print("Deleted:",race_id.id)
            deletes_entries.append(race_id.id)

        #Insert Drivers
        for h in range(1,len(a)):
            
        #for b in a[1]['drivers']:

            #Adding driver names
            for b in a[h]["drivers"]:
                name, club = fix_names(b["first_name"],b["last_name"],b["club"])
                race_name = db.query(Drivers).filter(and_(Drivers.name == name)).first()
                if race_name == None:
                    new_entry = Drivers(name=name, club=club)
                    db.add(new_entry)
                    db.commit()
                    db.refresh(new_entry)

            race_id = db.query(Race).filter(and_(Race.raceday_id == raceday_id, Race.title == title_2, Race.mode == int(mode), Race.heats == int(heats))).first()
            race_id = race_id.id

            
            #Replace existing records for this run


        for key, h in enumerate(range(1,len(a))):
            key +=1
            
            
            for k, b in enumerate(a[h]["drivers"]):

                pair_id = a[h]["race_id"]
                name, club = fix_names(b["first_name"],b["last_name"],b["club"])

                driver_id = db.query(Drivers).filter(and_(Drivers.name == name)).first()
                k += 1

                finishtime = b["time_info"]["FINISHTIME"]
                inter_1 = b["time_info"]["INTER_1"]
                inter_2 = b["time_info"]["INTER_2"]
                penalty = b["time_info"]["PENELTY"]
                speed = b["time_info"]["SPEED"]
                vehicle = b["vehicle"]

                if "status" in b:
                    status = b["status"]
                else:
                    status = None


                # Create a new Run instance
                new_run = Run(
                    race_id=race_id,
                    run_id=heat,
                    driver_id=int(driver_id.id),
                    pair_id=int(pair_id),
                    finishtime=finishtime,
                    inter_1=inter_1,
                    inter_2=inter_2,
                    penalty=penalty,
                    speed=speed,
                    vehicle=vehicle,
                    status=status
                )
                db.add(new_run)
                db.commit()
    return {"message": "Data uploaded successfully"}


@app.get("/get_single_placement_sql/{driver_name}")
async def get_single_placement_sql(driver_name: str, db: Session = Depends(get_db), cache=Depends(db_cache)):
    if "é" in driver_name:
        driver_name = driver_name.replace("é","e")

    query = queries.get_single_placement_sql(driver_name)
    # Check the cache

    cache_state = await cache(query=query)
    if cache_state:
        return cache_state

    result = db.execute(text(query))
    rows = result.fetchall()

    results_list = [
    {
        "race_date": row[0],
        "full_race_title": row[1],
        "race_id": row[2],
        "driver_name": row[3],
        "vehicle": row[4],
        "finishtime": row[5],
        "placement": row[6],
        "totale_drivers":row[7],
    } for row in rows
]
    await cache(query=query, data=results_list)
    return results_list
