from pydantic import BaseModel
from pydantic.typing import Optional


class UpdatePost(BaseModel):
    id: int
    name_posts: Optional[str]
    text_posts: Optional[str]


class EmotionalAssessment(BaseModel):
    post_id: int
    like: Optional[bool]
    dislike: Optional[bool]


class SearchResult(BaseModel):
    total: int
    items: list


class PostsEmotion(BaseModel):
    post_id: int
    user_id: int
    like: bool
    dislike: bool
