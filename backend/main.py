import uvicorn
from fastapi import FastAPI
from fastapi.logger import logger
from contextlib import asynccontextmanager
import os
import sys
from routes import CaptureRouter
from dotenv import load_dotenv


@asynccontextmanager
async def life_span(app: FastAPI):
    logger.info("Starting")
    yield
    logger.info("Stopping")


app = FastAPI(lifespan=life_span)
app.include_router(CaptureRouter)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


def check_root():
    print("Checking root privileges...")
    if os.geteuid() != 0:
        print("This script must be run as root!")
        args = ["sudo", sys.executable] + sys.argv
        os.execvp("sudo", args)


if __name__ == "__main__":
    check_root()
    # uvicorn.run("main:app", host="0.0.0.0", port=8000)
    uvicorn.run("main:app", host="0.0.0.0", port=8088, reload=True)
