import uvicorn
from fastapi import FastAPI
from fastapi.logger import logger
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware
import os
import sys
from core.config import ENV_CONFIG
from routes import router


@asynccontextmanager
async def life_span(app: FastAPI):
    logger.info("Starting app")
    yield
    logger.info("Stopping app")


app = FastAPI(lifespan=life_span)
app.include_router(router)
if ENV_CONFIG.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ENV_CONFIG.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


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
    uvicorn.run(
        "main:app",
        host=ENV_CONFIG.backend_host,
        port=ENV_CONFIG.backend_port,
        reload=True,
    )
