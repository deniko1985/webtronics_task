from datetime import datetime
import uuid
from sqlalchemy import desc, func, or_, select, insert, update, delete
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import ResponseError

from models.posts import Posts, EmotionAssessment as Emotion
from models.db import database, redis_cli
from schemas.posts import PostsEmotion


async def get_all_posts(
        user_id,
        search_text=None,
        search_by_name="off",
        search_by_text="off"):
    try:
        cond = []
        if search_by_name == 'on':
            cond.append(func.to_tsvector(Posts.name_posts).bool_op("@@")(
                            func.phraseto_tsquery(search_text)))
        if search_by_text == 'on':
            cond.append(func.to_tsvector(Posts.text_posts).bool_op("@@")(
                            func.phraseto_tsquery(search_text)))
        q = select(func.count()).where(Posts.user_id == user_id)
        if search_text:
            q = q.where(or_(*cond))
        total_row = await database.execute(q)
        query = select([Posts]).where(Posts.user_id == user_id)
        if search_text:
            query = query.where(or_(*cond))
        query = (
                query
                .order_by(desc(Posts.id))
                )
        records = await database.fetch_all(query)
        data = []
        for record in records:
            new_record = dict(record)
            emotion = redis_cli.hgetall(record.id)
            new_record["emotion"] = emotion
            data.append(new_record)
        response = {
            "total": total_row,
            "items": data
        }
        return response
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def create_post_user(user_id, email, name_posts, text_posts):
    try:
        query = insert(Posts).values(
            user_id=user_id,
            email=email,
            name_posts=name_posts,
            text_posts=text_posts,
            date=datetime.now(),
        )
        post_id = await database.execute(query)
        redis_cli.hset(
            post_id,
            mapping={
                "like": 0,
                "dislike": 0
            }
        )
        return post_id
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def delete_post(user_id, post_id):
    try:
        q = (
            delete(Emotion)
            .where(Emotion.post_id == post_id)
        )
        await database.execute(q)
        query = (
            delete(Posts)
            .where(Posts.user_id == user_id)
            .where(Posts.id == post_id)
        )
        return await database.execute(query)
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def create_post_file(post_id):
    try:
        new_file = uuid.uuid4()
        export_filepath = "temp/" + f"{new_file}.txt"
        q = (
            select([Posts])
            .where(Posts.id == post_id)
        )
        res = await database.fetch_one(q)
        with open(export_filepath, "+a") as file:
            file.writelines(res.name_posts)
            file.writelines("\n")
            file.writelines(res.text_posts)
        return export_filepath
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def get_post_by_id(id, user_id):
    try:
        q = (
            select([Posts])
            .where(Posts.id == id)
            .where(Posts.user_id == user_id)
        )
        return await database.fetch_one(q)
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def update_post_by_id(user_id, id, name_posts, text_posts):
    try:
        q = (
            update(Posts)
            .where(Posts.user_id == user_id)
            .where(Posts.id == id)
        )
        if name_posts:
            q = q.values(name_posts=name_posts)
        if text_posts:
            q = q.values(text_posts=text_posts)
        await database.execute(q)
        query = (
            select([Posts])
            .where(Posts.user_id == user_id)
            .where(Posts.id == id)
        )
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        return {"error": str(error)}


async def add_post_emotional(user_id: int, data: PostsEmotion):
    try:
        q = (
            select(Posts)
            .where(Posts.id == data.post_id)
        )
        r = await database.fetch_one(q)
        if not r:
            return "Поста с данным id не существует"
        else:
            if r.user_id == user_id:
                return "Вы не можете оценивать свои посты"
            else:
                q_select = (
                    select(Emotion)
                    .where(Emotion.post_id == r.id)
                    .where(Emotion.user_id == user_id)
                )
                r_select = await database.fetch_one(q_select)
                if r_select:
                    if r_select.like == data.like or r_select.dislike == data.dislike:
                        return "Вы не можете повторно ставить посту такую же оценку"
                    if data.like and r_select.dislike is True:
                        q_update = (
                            update(Emotion)
                            .where(Emotion.post_id == r.id)
                            .where(Emotion.user_id == user_id)
                            .values(like=True, dislike=False)
                        )
                        await database.execute(q_update)
                        redis_cli.hincrby(data.post_id, "like", 1)
                        redis_cli.hincrby(data.post_id, "dislike", -1)
                        return redis_cli.hgetall(data.post_id)
                    if data.dislike and r_select.like is True:
                        q_update = (
                            update(Emotion)
                            .where(Emotion.post_id == r.id)
                            .where(Emotion.user_id == user_id)
                            .values(like=False, dislike=True)
                        )
                        await database.execute(q_update)
                        redis_cli.hincrby(data.post_id, "like", -1)
                        redis_cli.hincrby(data.post_id, "dislike", 1)
                        return redis_cli.hgetall(data.post_id)
                query = insert(Emotion).values(
                    author_id=r.user_id,
                    user_id=user_id,
                    post_id=r.id,
                    like=data.like,
                    dislike=data.dislike
                )
                await database.execute(query)
                if data.like:
                    redis_cli.hincrby(data.post_id, "like", 1)
                if data.dislike:
                    redis_cli.hincrby(data.post_id, "dislike", 1)
                return redis_cli.hgetall(data.post_id)
    except SQLAlchemyError as error:
        return {"error": str(error)}
    except ResponseError as error:
        return {"error": str(error)}
