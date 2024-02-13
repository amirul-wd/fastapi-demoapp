import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter

from core.logger import logger
from app.schemas import *
from app.db.base import engine

from app.models import Base
from scheduler.invitation import invitation_scheduler
from app.routes import router as api_router

from middleware import casbin_auth_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Started!!")
    Base.metadata.create_all(bind=engine)
    logger.info("DB connected!!")
    yield
    logger.info("Shutdown!!")
    logger.info("DB disconnected!!")


app = FastAPI(lifespan=lifespan, debug=True)

origins = ["*"]

app.middleware("http")(casbin_auth_middleware)

# app.add_middleware(middleware_class=casbin_auth_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    invitation_scheduler.start()
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
