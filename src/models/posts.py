import sqlalchemy
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

metadata = sqlalchemy.MetaData()

Base = declarative_base(metadata=metadata)


class Posts(Base):
    __tablename__ = "posts"
    id = Column(Integer, Sequence('posts_id_seq'), primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    email = Column(String(150))
    name_posts = Column(String(100))
    text_posts = Column(String())
    date = Column(DateTime())


class EmotionAssessment(Base):
    __tablename__ = "emotion_assessment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(ForeignKey("posts.id"))
    author_id = Column(Integer)
    user_id = Column(Integer)
    like = Column(Boolean)
    dislike = Column(Boolean)
