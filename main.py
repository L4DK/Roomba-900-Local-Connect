"""
FilePath: "/Roomba-900-Local-Connect/main.py",
Project Title: Roomba-900-Local-Connect,
File Description: Integrated FastAPI Server. References 'app' to satisfy linter.
Author: "Michael Landbo",
Date Modified: "01/04/2026",
Version: "v.1.2.5"
"""

from contextlib import asynccontextmanager
from typing import Literal

import uvicorn
from fastapi import FastAPI, HTTPException

from roomba_logic import RoombaController

# 1. Initialize the controller
roomba = RoombaController()


# 2. Define lifespan logic
@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    # 'app_instance' usage: Logging the title on start
    print(f"Starting {app_instance.title}...")
    roomba.connect()
    yield
    roomba.disconnect()


# 3. Create the app object
app = FastAPI(title="Roomba-900-Local-Connect API", lifespan=lifespan)


@app.get("/")
async def root():
    return {
        "project": app.title,  # Functional usage of the 'app' object
        "status": "online" if roomba.is_connected else "offline",
    }


@app.get("/status")
async def get_status():
    """Returns telemetry data."""
    return roomba.full_state


@app.get("/control/{cmd}")
async def control(cmd: Literal["start", "stop", "pause", "resume", "dock"]):
    """Validates and dispatches mission commands."""
    if not roomba.is_connected:
        raise HTTPException(status_code=503, detail="Robot is offline.")
    roomba.send_command(cmd)
    return {"result": "success", "command": cmd}


# 4. Explicit runner
if __name__ == "__main__":
    # Explicitly accessing 'app' for uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
