"""
FilePath: "/Roomba-900-Local-Connect/main.py"
Project Title: Roomba-900-Local-Connect
File Description: FastAPI Server providing a REST API for the Roomba.
Author: "Michael Landbo"
Date created: 31/03/2026
Date Modified: 01/04/2026
Version: v.1.1.2
"""

from fastapi import FastAPI
from roomba_logic import RoombaController
from contextlib import asynccontextmanager
import uvicorn

roomba = RoombaController()

@asynccontextmanager
async def lifespan(app: FastAPI):
    roomba.connect()
    yield

app = FastAPI(title="Roomba-900-Local-Connect Dashboard", lifespan=lifespan)

@app.get("/")
async def root():
    return {"Project": "Roomba-900-Local-Connect", "Author": "Michael Landbo", "Status": "Active"}

@app.get("/status")
async def status():
    return roomba.full_state

@app.get("/control/{cmd}")
async def control(cmd: str):
    roomba.send_command(cmd)
    return {"result": "ok", "command": cmd}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
