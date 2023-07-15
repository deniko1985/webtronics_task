import os
from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm

from schemas.users import User
from utils import users
from utils.depend import get_current_user

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


router = APIRouter()


@router.post("/auth")
async def auth(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await users.get_user_by_email(email=form_data.username.lower())
        if not user:
            return {"data": "Пользователя с таким email не существует"}
        if not users.verify_password(plain_password=form_data.password, hashed_password=user["hashed_password"]):
            return {"data": "Некорректный пароль"}
        token = await users.create_user_token(user_id=user.id, email=form_data.username.lower())
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/add_user')
async def add_user(
        email=Form(),
        password=Form()):
    try:
        v_email = await users.verifer_email(email)
        if v_email == "error":
            return {"error": "Введен email, который не прошел проверку."}
        n_user = await users.get_user_by_email(email)
        if n_user:
            return {"data": "Пользователь с таким email существует"}
        data = await users.create_user(email=email, password=password)
        if not data:
            raise HTTPException(status_code=400)
        if data.get("error"):
            return {"error": data}
        else:
            return {"data": data, "message": "Пользователь успешно зарегистрирован"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/logout')
async def logout_user(current_user: User = Depends(get_current_user)):
    try:
        response = await users.delete_token(current_user.id)
        if response and response.get("error"):
            return {"error": response}
        else:
            return {"message": "Токен успешно удален"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
