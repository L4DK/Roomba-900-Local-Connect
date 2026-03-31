"""
FilePath: "/Roomba-900-Local-Connect/main.py"
Project Title: Roomba-900-Local-Connect
File Description: FastAPI Server. No hardcoded configuration here.
Author: "Michael Landbo"
Date created: 31/03/2026
Date Modified: 01/04/2026
Version: v.1.1.3
"""

from fastapi import FastAPI
from roomba_logic import RoombaController
from contextlib import asynccontextmanager
import uvicorn

# Controller handles its own env loading
roomba = RoombaController()

@asynccontextmanager
async def lifespan(app: FastAPI):
    roomba.connect()
    yield

app = FastAPI(title="Roomba-900-Local-Connect API", lifespan=lifespan)

@app.get("/status")
async def get_status():
    return roomba.full_state

@app.get("/control/{cmd}")
async def send_cmd(cmd: str):
    roomba.send_command(cmd)
    return {"status": "command_sent", "command": cmd}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
