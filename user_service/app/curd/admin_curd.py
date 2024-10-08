from datetime import datetime, timedelta, timezone
from sqlmodel import select
from fastapi import HTTPException
from app.models.admin_schemas import AdminLoginForm, Admin, AdminCreateModel # type: ignore
from app.main import DB_SESSION # type: ignore 
from app.curd.kong_controller import create_consumer_in_kong, create_jwt_credential_in_kong # type: ignore
from app.settings import ADMIN_EXPIRE_TIME, ADMIN_SECRET_KEY, ALGORITHM, SECRET_KEY, ADMIN_TOPIC # type: ignore
from app.utils.kafka_producer import KAFKA_PRODUCER # type: ignore
from jose import jwt
import json


def admin_verify(admin_form: AdminLoginForm, session: DB_SESSION):
    admin_email: str = admin_form.admin_email
    admin_password: str = admin_form.admin_password

    if not (admin_form.admin_secret == ADMIN_SECRET_KEY):
        raise HTTPException(status_code=404, detail="")

    admin = session.exec(select(Admin).where(
        (Admin.admin_email == admin_email)
        and (Admin.admin_password == admin_password)
    )).one_or_none()

    if not admin:
        HTTPException(status_code=404,
                      detail="Admin not found from this details!")
    token = generateToken(admin, admin_form.admin_secret, ADMIN_EXPIRE_TIME)
    return {
        "admin_token": token,
        "type": "bearer"
    }


async def create_admin_func(admin_form: AdminCreateModel, session: DB_SESSION, producer: KAFKA_PRODUCER):
    admin_email = admin_form.admin_email 
    message = {
        "email": admin_email,
        "notification_type": "welcome_user"
    }
    try:
        await producer.send_and_wait(value=json.dumps(message).encode("utf-8"), topic=ADMIN_TOPIC)
    except Exception as x:
        print(f"Error sending message to Kafka: {x}")
    
    if not (admin_form.admin_secret == ADMIN_SECRET_KEY):
        raise HTTPException(status_code=404, detail="")
    admin_exist = session.exec(select(Admin).where(
        Admin.admin_email == admin_form.admin_email)).one_or_none()
    if admin_exist:
        raise HTTPException(status_code=404, detail="")
    admin = Admin(
        admin_name=admin_form.admin_name,
        admin_email=admin_form.admin_email,
        admin_password=admin_form.admin_password
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    create_consumer_in_kong(admin.admin_name)
    create_jwt_credential_in_kong(
        admin.admin_name, admin.admin_kid, admin_form.admin_secret)
    return admin_form


def generateToken(admin: Admin, admin_secret: str, expires_delta: timedelta) -> str:
    """
    Generate a token.

    Args:
        data (dict): User data to be encoded.
        expires_delta (timedelta): Expiry time for the token.

    Returns:
        str: Generated token.
    """

    # Calculate expiry time
    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "admin_name": admin.admin_name,
        "admin_email": admin.admin_email,
        "exp": expire
    }
    headers = {
        "kid": admin.admin_kid,
        "secret": admin_secret,
        "iss": admin.admin_kid
    }

    # Encode token with user data and secret key
    token = jwt.encode(payload, SECRET_KEY,
                       algorithm=ALGORITHM, headers=headers)
    return token
