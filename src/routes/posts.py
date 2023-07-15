import os
import mimetypes
from fastapi import APIRouter, HTTPException, Depends, Response, Form

from schemas.users import User
from schemas.posts import UpdatePost, EmotionalAssessment, SearchResult
from utils import posts
from utils.depend import get_current_user


router = APIRouter()


@router.get('/my_posts')
async def get_my_posts(current_user: User = Depends(get_current_user)):
    try:
        data_posts = await posts.get_all_posts(current_user.id)
        if data_posts:
            return data_posts
        else:
            return {"data": "Нет заметок"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/add_post')
async def add_post_user(
        name_posts=Form(),
        text_posts=Form(),
        current_user: User = Depends(get_current_user)):
    try:
        data_post = await posts.create_post_user(
            user_id=current_user.id,
            email=current_user.email,
            name_posts=name_posts,
            text_posts=text_posts)
        return data_post
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/delete_post/{post_id}')
async def delete_post_user(post_id: int, current_user: User = Depends(get_current_user)):
    try:
        user_id = current_user.id
        data = await posts.delete_post(user_id, post_id)
        if data:
            return {"data": data}
        else:
            return "Ok!"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/update_post')
async def get_update_post(
        post: UpdatePost,
        current_user: User = Depends(get_current_user)):
    try:
        user_id = current_user.id
        data = await posts.update_post_by_id(user_id, post.id, post.name_posts, post.text_posts)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/download_post", tags=["user_file"])
async def download_post(
        post_id: int,
        current_user: User = Depends(get_current_user)):
    try:
        load_filepath = await posts.create_post_file(post_id)
        mimetype = mimetypes.guess_type(load_filepath)[0]
        with open(load_filepath, 'rb') as fs:
            data_file = fs.read()
            os.remove(load_filepath)
        if not data_file:
            return {"data": "Создание файла не удалось"}
        else:
            return Response(
                content=data_file,
                media_type=mimetype,
                headers={"Content-Disposition": f'attachment; filename={load_filepath}'}
                )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search_by_posts/{search_query}", response_model=SearchResult)
async def get_search_query(
        search_text: str,
        search_by_name='off',
        search_by_text='off',
        current_user: User = Depends(get_current_user)) -> list:
    try:
        if search_by_name == 'off' and search_by_text == 'off' or not search_text:
            return {"data": "Вы не можете совершить поиск не введя текст или со снятыми флажками"}
        user_id = current_user.id
        result = await posts.get_all_posts(
            user_id,
            str(search_text),
            search_by_name,
            search_by_text
        )
        if result:
            return result
        else:
            return {"data": "По вашему запросу не найдено ни одной записи"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/emotional_assessment")
async def add_emotional(
        data: EmotionalAssessment,
        current_user: User = Depends(get_current_user)):
    try:
        if data.like is True and data.dislike is True:
            raise HTTPException(status_code=400, detail="Вы не можете одновременно поставить и like, и dislike")
        result = await posts.add_post_emotional(user_id=current_user.id, data=data)
        if result:
            return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
