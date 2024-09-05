from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import create_engine, SQLModel, Session, Field
from typing import Annotated, Optional, AsyncGenerator
from contextlib import asynccontextmanager
from settings import DATABASE_URL
from app.models.user_schemas import User # type: ignore
from aiokafka import AIOKafkaProducer # type: ignore
from .curd.users_curd import hash_password, get_db, UserCreate# type: ignore
from app.utils.user_producer import produce_user_registered# type: ignore
from app.api import admin_api, user_api # type: ignore
import asyncio
connection_string = str(DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)

def get_session():
    with Session(engine) as session:
        yield session

DB_SESSION = Annotated[Session, Depends(get_session)]


def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Haseeb Ecommerce", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8000", 
            "description": "Development Server"
        }
        ])

@app.get("/")
def home():
    return "Welcome to User service"


app.include_router(router=user_api.user_routes,
                    tags=["Users"])
app.include_router(router=admin_api.admin_route,
                    tags=["Admin"])

