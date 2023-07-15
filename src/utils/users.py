import os
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from jose import jwt
import requests


from models.users import users_table as users, tokens
from models.db import database
from config import pwd_context

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
API_KEY = os.getenv("API_KEY")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user_by_id(user_id: int):
    try:
        query = (
                users.select()
                .where(users.c.id == user_id)
                .where(users.c.is_active == True)
                )
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def get_user_by_email(email: str):
    try:
        query = (
                users.select()
                .where(users.c.email == email)
                )
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def check_user_token(user_id: int):
    try:
        query = tokens.select().where(tokens.c.user_id == user_id)
        return await database.fetch_one(query)
    except SQLAlchemyError:
        return None


async def get_user_by_token(token: str):
    try:
        query = tokens.join(users).select().where(
            and_(
                tokens.c.access_token == token,
                tokens.c.expires > datetime.now()
            )
        )
        return await database.fetch_one(query)
    except SQLAlchemyError:
        return None


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(weeks=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_user_token(user_id: int, email):
    data = {
                "sub": email,
                "user_id": user_id,
            }
    access_token = await create_access_token(data)
    token_obj = await check_user_token(user_id)
    try:
        if token_obj:
            token = token_obj.access_token
            token_id = token_obj.id
            if token and token_id:
                query = (
                    tokens.update()
                    .where(tokens.c.id == token_id)
                    .values(
                        id=token_id,
                        access_token=access_token,
                        expires=datetime.utcnow() + timedelta(weeks=2),
                        user_id=user_id,
                    )
                    .returning(tokens.c.access_token, tokens.c.expires)
                )
            else:
                query = (
                    tokens.insert()
                    .values(
                        access_token=access_token,
                        expires=datetime.utcnow() + timedelta(weeks=2),
                        user_id=user_id,
                    )
                    .returning(tokens.c.access_token, tokens.c.expires)
                )
        else:
            query = (
                tokens.insert()
                .values(
                    access_token=access_token,
                    expires=datetime.utcnow() + timedelta(weeks=2),
                    user_id=user_id,
                )
                .returning(tokens.c.access_token, tokens.c.expires)
            )
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def create_user(email, password):
    hashed_password = get_password_hash(password)
    try:
        query = (
            users.insert()
            .values(
                email=email,
                hashed_password=hashed_password,
                is_active=True,
                auth_token='',
            )
            .returning(
                users.c.id, users.c.email, users.c.is_active
            )
            )
        user_id = await database.execute(query)
        token = await create_user_token(user_id, email)
        user = await get_user_by_email(email)
        if not token:
            return False
        else:
            token_dict = {"token": token["access_token"], "expires": token["expires"]}
            return {"id": user.id, "name": user.email, "is_active": True, "token": token_dict}
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def delete_token(user_id: int):
    try:
        q = (
                tokens.delete()
                .where(tokens.c.user_id == user_id)
            )
        return await database.execute(q)
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def verifer_email(email: str):
    try:
        response = (
            requests.get
            (f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={API_KEY}")
            .json()
        )
        if response["data"]["status"] == "valid":
            return "valid"
        else:
            return "error"
    except requests.ConnectionError:
        return {"error": "ConnectionError"}
    except requests.exceptions.HTTPError:
        return {"error": "HTTPError"}
    except requests.exceptions.RequestException:
        return {"error": f"status_code: {response.status_code}"}
