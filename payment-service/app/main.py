from fastapi import FastAPI, Depends
from starlette.middleware.sessions import SessionMiddleware
from app import setting
from sqlmodel import SQLModel, create_engine, Session
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routes.payment_routes  import router
from app.model.transaction import *
from app.utils.kafka import payment_consumer
import asyncio

connectionstring = str(setting.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg2"
)

engine = create_engine(connectionstring, connect_args={"sslmode" : "require"}, pool_recycle=600, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

DB_SESSION = Annotated[Session, Depends(get_session)]


async def task_initiator():
    asyncio.create_task(payment_consumer())


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Hello World..!!!")
    create_db_and_tables()
    await task_initiator()
    yield

app = FastAPI(
    title="Payment Service",
    version="1.0.0",
    lifespan=life_span,
    contact={
        "name": "Abdul Haseeb",
        "email": "abdulhaseeb065@gmail.com",
    }
)

# SessionMiddleware must be installed to access request.session
app.add_middleware(
    SessionMiddleware, secret_key="!secret")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)

app.router.include_router(router, tags=["Payment Services"])

@app.get("/")
def get_root():
    return {"message": "welcome to Payment Service! Transaction a new payment"}