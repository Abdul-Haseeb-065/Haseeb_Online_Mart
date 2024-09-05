from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import create_engine, SQLModel, Session, Field
from typing import Annotated, Optional, AsyncGenerator
from contextlib import asynccontextmanager
from settings import DATABASE_URL

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

