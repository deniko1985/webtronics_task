from fastapi import FastAPI
from models.db import database
import asyncio

from routes import posts, users


app = FastAPI()

loop = asyncio.get_event_loop()


app.include_router(users.router)
app.include_router(posts.router)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
