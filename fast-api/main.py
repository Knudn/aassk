from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Boolean  
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
class Config(Base):
    __tablename__ = 'Global_Config'
    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(String, index=True)
    approved = Column(Boolean)

# Create the database tables
Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    print()
    hostname = socket.gethostname()

    init_msg = {
        "Hostname": hostname,
        "Init": True,
    }

    flask_app_url = 'http://192.168.1.50:7777/api/init'
    
    try:
        response = requests.post(flask_app_url, json=init_msg)
        response.raise_for_status()
        print(f"Initialization message sent successfully: {response.text}")
        existing_config = Base.query(Config).first()
        if existing_config:
            # If there's an existing config, update it
            existing_config.host_id = hostname
            existing_config.approved = False
        else:
            # If there's no existing config, create a new one
            new_config = Config(host_id=hostname, approved=False)
            Base.add(new_config)

    except requests.exceptions.RequestException as e:
        print(f"Failed to send initialization message: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
