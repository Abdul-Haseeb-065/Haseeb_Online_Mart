from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.curd.users_curd import user_login, create_user_func, get_user_by_id_func, update_user_func, delete_user_func # type: ignore
from app.models.user_schemas import User # type: ignore

user_route = APIRouter()


@user_route.get("/get_users")
def get_user(user: Annotated[User, Depends(get_user_by_id_func)]):
    return user


@user_route.post("/add_user")
async def add_user(token: Annotated[dict, Depends(create_user_func)]):
    if not token:
        HTTPException(
            status_code=400, detail="Try again, something occurred while generating token from library. ")
    return token


@user_route.post("/login_user")
async def authenticate_user(token: Annotated[dict, Depends(user_login)]):
    if not token:
        HTTPException(
            status_code=400, detail="Try again, something occurred while generating token from library. ")
    return token


@user_route.put("/update_user")
def update_user(updated_user: Annotated[User, Depends(update_user_func)]):
    return updated_user


@user_route.delete("/delete_user")
def delete_user(message: Annotated[str, Depends(delete_user_func)]):
    return message
