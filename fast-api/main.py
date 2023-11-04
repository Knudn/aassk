from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random

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

# Pydantic model to define request body
class ItemCreate(BaseModel):
    name: str
    description: str

# Pydantic model to define response model
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

# Define a random function
@app.get("/random")
def read_random_number():
    return {"random_number": random.randint(1, 100)}

# Add an item to the database
@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: SessionLocal = Depends(get_db)):
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Retrieve all items from the database
@app.get("/items/", response_model=list[ItemResponse])
def read_items(db: SessionLocal = Depends(get_db)):
    items = db.query(Item).all()
    return items

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
