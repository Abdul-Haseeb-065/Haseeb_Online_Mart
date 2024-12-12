from app.setting import ALGORITHM, SECRET_KEY
from app.model.authentication import Token, TokenData, Admin, Users
from app.main import DB_SESSION
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status
from jose import jwt, JWTError
from sqlmodel import select, Session
from typing import Annotated, Union, Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get User
def get_user(db, email: str | None, session: DB_SESSION):
    correct_user = session.exec(select(db).where(db.email == email)).first()
    if correct_user:
        return correct_user

# Get Current Admin
async def get_current_admin(token: Annotated[str, Depends(oauth2_scheme)], session: DB_SESSION):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Union[str, None] = payload.get("username")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(Admin, email=token_data.email, session=session)
    if user is None:
        raise credentials_exception
    return user

# Get Current Active & Verify Admin
async def get_current_active_admin_user(current_user: Annotated[Admin, Depends(get_current_admin)]):
    if current_user.is_verified:
        print(current_user.id)
        return current_user
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user or not an instructor",
            headers={"WWW-Authenticate": "Bearer"},
        )

        ######################################################

# Get Current User
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: DB_SESSION):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Union[str, None] = payload.get("username")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(Users, email=token_data.email, session=session)
    if user is None:
        raise credentials_exception
    return user

# Get Current Active & Verify User
async def get_current_active_user(current_user: Annotated[Users, Depends(get_current_user)]):
    if current_user.is_active:
        print(current_user.id)
        return current_user
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )        