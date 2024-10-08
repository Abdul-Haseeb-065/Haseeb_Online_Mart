from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.controllers.auth_admin import admin_verify, create_admin_func # type: ignore
from app.models.admin_model import Admin # type: ignore

admin_route = APIRouter()


@admin_route.post("/verify_admin", response_model=dict[str, str])
def verify_admin(admin_token: Annotated[dict[str, str], Depends(admin_verify)]):
    if not admin_token:
        raise HTTPException(status_code=404, detail="Admin has not verified!")
    return admin_token


@admin_route.post("/create_verify", response_model=Admin)
def create_admin(admin: Annotated[Admin, Depends(create_admin_func)]):
    if not admin:
        raise HTTPException(status_code=404, detail="Admin has not created successfully!")
    return admin
