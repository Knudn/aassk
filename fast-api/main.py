from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Boolean  
from sqlalchemy.orm import sessionmaker, Session, declarative_base 
import socket
import requests
import os
import subprocess
import time
from typing import List
import re
import argparse


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
html_file_path = os.path.join(static_dir, 'base.html')

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# Define the database model
class Config(Base):
    __tablename__ = 'Global_Config'
    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(String, index=True)
    approved = Column(Boolean)

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String, index=True)
    timer = Column(Integer)

class URLData(BaseModel):
    URL: str


# Create the database tables
Base.metadata.create_all(bind=engine)

def to_dict(row):
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


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


manager = ConnectionManager()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/set-url")
async def set_url(url_data: URLData):

    with open(html_file_path, 'r') as file:
        content = file.read()

    # The regex pattern to match the src attribute of the iframe
    pattern = r'src="[^"]*"'

    # Replace the captured group with the new URL
    updated_content = re.sub(pattern, f'src="{url_data.URL}"', content)

    with open(html_file_path, 'w') as file:
        file.write(updated_content)

    # Notify clients, assuming manager.broadcast is defined
    await manager.broadcast("update")

    return {"message": "URL updated and clients notified"}



@app.post("/update_index/")
async def receive_data(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

    # Delete existing records
    db.query(Asset).delete()
    db.commit()

    # Insert new data
    for item in data:
        extension = item['url'].lower().split('.')[-1]
        print(extension, flhost+item['url'].lower())
        if "."+extension in image_extensions and "http" not in item['url'].lower():
            print(flhost+item['url'].lower())
            print("asd")
        new_asset = Asset(name=item['name'], url=item['url'], timer=item['timer'])
        db.add(new_asset)
    db.commit()

    return {"message": "Data received, old data deleted, and new data stored"}

@app.get("/current_assets/")
async def get_current_assets(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    return [to_dict(asset) for asset in assets]

@app.on_event("startup")
async def startup_event():
    hostname = socket.gethostname()
    init_msg = {
        "Hostname": hostname,
        "Init": True,
    }

    flask_app_url = args.flhost + "/api/init"

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
                    #open_chromium_with_message(monitor_not_approved_path)
                    open_chromium_with_message(html_file_path)
            else:
                new_config = Config(host_id=hostname, approved=False)
                db.add(new_config)
                db.commit()
                open_chromium_with_message(no_endpoint_path)
                
                
    except requests.exceptions.RequestException as e:
        print(f"Failed to send initialization message: {e}")
        open_chromium_with_message(no_endpoint_path)
        time.sleep(1)
        
@app.get("/")
async def root():
    return {"message": "Hello World"}

async def notify_clients_of_update():
    await manager.broadcast("update")

if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Run the FastAPI server")
    parser.add_argument("--host", default="0.0.0.0", type=str, help="Host IP address")
    parser.add_argument("--port", default=8000, type=int, help="Port number")
    parser.add_argument("--flhost", default="http://192.168.1.50:7777", type=str, help="Endpoint used for to orchestrate client")
    # Parse the arguments
    args = parser.parse_args()
    flhost = args.flhost

    # Start the Uvicorn server with the specified host and port
    uvicorn.run(app, host=args.host, port=args.port)
