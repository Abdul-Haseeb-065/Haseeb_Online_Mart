from fastapi import HTTPException
from typing import Annotated, Optional
from sqlmodel import SQLModel, Session, Field, select
from app.models.user_schemas import UserBase, User,UserMain, UpdatingUser, UserCredentials # type: ignore
from app.utils.auth import generateToken, verifyPassword, passwordIntoHash # type: ignore
from settings import ACCESS_TOKEN_EXPIRE_TIME, USER_TOPIC # type: ignore
from app.main import DB_SESSION  # type: ignore
from app.utils.kafka_producer import KAFKA_PRODUCER # type: ignore
from datetime import timedelta
import json

def user_login(user_auth_detail: UserCredentials, session: DB_SESSION):
    print("User Details from login function: ", user_auth_detail)
    statement = select(User).where(User.user_email == user_auth_detail.user_email)
    db_user = session.exec(statement).one_or_none()

    if not db_user:
        raise HTTPException(status_code=401, detail=f"User does not exist in Database from email:{user_auth_detail.user_email}")

    is_password_exist = verifyPassword(
        user_auth_detail.user_password, db_user.user_password)

    if not is_password_exist:
        raise HTTPException(
            status_code=404, detail="User does not exist with this password!")

    # Generate JWT token
    token = generateToken(db_user, ACCESS_TOKEN_EXPIRE_TIME)
    if token:
        db_user.is_verified = True
        session.add(db_user)
        session.commit()
    return {"access_token": token, "token_type": "bearer"}

async def create_user_func(user_form: UserBase, session: DB_SESSION, producer: KAFKA_PRODUCER):
   
    users = session.exec(select(User))
    user_email: str = user_form.user_email
    user_password: str = user_form.user_password
    for user in users:
        password_exist = verifyPassword(user_password, user.user_password)
        if user.user_email == user_email and password_exist:
            raise HTTPException(
                status_code=404, detail="email and password already exist!")
        elif user.user_email == user_email:
            raise HTTPException(
                status_code=404, detail="This email already exist!")
        elif password_exist:
            raise HTTPException(
                status_code=404, detail="This password already exist!")
    user = await add_user_in_db_func(user_form, session)
    # kong_func(user.user_name, user.kid, secret_key=None)
    user_details = {
        "user_email": user_email,   
        "user_password": user_password
    }

    
    # Login the newly registered user and return the data
    token_data = user_login(user_auth_detail=UserCredentials(**user_details), session=session)
    print("data from login", token_data)

    message = {
        "email": user_email,
        "notification_type": "welcome_user"
    }

    # TODO: Produce message to notification topic to welcome user through email
    await producer.send_and_wait(value=json.dumps(message).encode("utf-8"), topic=USER_TOPIC)
    return token_data




async def add_user_in_db_func(user_form: UserBase, session: Session):
    try:
        hashed_password = passwordIntoHash(user_form.user_password)
        user_form.user_password = hashed_password
        if not hashed_password:
            raise HTTPException(
                status_code=500, detail="Due to some issues, password has not convert into hashed format.")
        user = User(**user_form.model_dump())
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as x:
        raise HTTPException(status_code=500, detail=str(x))
    return user

def get_user_by_id_func(user_id: int, session: DB_SESSION):
    user = session.get(User, user_id)
    if user is None:
        HTTPException(status_code=400, detail="User not found")
    return user


def update_user_func(user_id: int, user_details: UpdatingUser, session: DB_SESSION):
    user = session.get(User, user_id)
    if not user:
        HTTPException(status_code=400, detail="User not found")
    updated_user = user_details.model_dump(exclude_unset=True)
    for key, value in updated_user.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user_func(user_id: int, session: DB_SESSION):
    user = session.get(User, user_id)
    if not user:
        HTTPException(status_code=400, detail="User not found")

    session.delete(user)
    session.commit()
    return f"User has been successfully deleted of this id: {user_id}"
