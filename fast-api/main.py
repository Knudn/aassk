from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random
import socket
import hashlib
import requests

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the database model
class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic models to define request and response data shapes
class ItemCreate(BaseModel):
    name: str
    description: str

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    print("Asdasd")
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    id_hash = hashlib.md5(f"{hostname}{ip_address}".encode()).hexdigest()

    init_msg = {
        "Hostname": hostname,
        "IP": ip_address,
        "ID": id_hash
    }

    flask_app_url = 'http://192.168.1.50:7777/api/init'
    
    try:
        response = requests.post(flask_app_url, json=init_msg)
        response.raise_for_status()
        print(f"Initialization message sent successfully: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send initialization message: {e}")

@app.get("/random")
def read_random_number():
    return {"random_number": random.randint(1, 100)}

@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: SessionLocal = Depends(get_db)):
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[ItemResponse])
def read_items(db: SessionLocal = Depends(get_db)):
    items = db.query(Item).all()
    return items

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
