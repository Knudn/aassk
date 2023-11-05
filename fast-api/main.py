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
import os
import subprocess
import time
app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
script_dir = os.path.dirname(os.path.realpath(__file__))
static_dir = os.path.join(script_dir, 'static')
monitor_not_approved_path = os.path.join(static_dir, 'monitor-not-approved.html')
no_endpoint_path = os.path.join(static_dir, 'no-endpoint.html')

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

def open_chromium_with_message(file_path):
    # Kill any existing Chromium browser instances
    subprocess.run(["pkill", "chromium"], stderr=subprocess.DEVNULL)

    # Set the DISPLAY environment variable to use the physical display
    os.environ["DISPLAY"] = ":0"

    # Command to open Chromium browser in fullscreen with the specified local HTML file
    cmd = ["/usr/bin/chromium", "--start-fullscreen", file_path]

    # Run the command in a non-blocking way
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@app.on_event("startup")
async def startup_event():
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

        with SessionLocal() as db:
            existing_config = db.query(Config).first()
            if existing_config:
                existing_config.host_id = hostname
                existing_config.approved = False
                db.commit()
                if not existing_config.approved:
                    print(monitor_not_approved_path)
                    open_chromium_with_message(monitor_not_approved_path)
            else:
                new_config = Config(host_id=hostname, approved=False)
                db.add(new_config)
                db.commit()
                print(no_endpoint_path)
                open_chromium_with_message(no_endpoint_path)
                
                
    except requests.exceptions.RequestException as e:
        print(f"Failed to send initialization message: {e}")
        open_chromium_with_message(no_endpoint_path)
        time.sleep(1)
        open_chromium_with_message("https://vg.no")
        
@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
