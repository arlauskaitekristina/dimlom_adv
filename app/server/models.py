from sqlalchemy import ARRAY, Column, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, declarative_base, relationship

Base: DeclarativeBase = declarative_base()


class User(Base):
    """Модель пользователя"""

    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False, unique=True)
    api_key: str = Column(String, unique=True, index=True)
    tweets = relationship('Tweet', back_populates='user')
    likes = relationship('Like', back_populates='user')

    followers = relationship(
        'Follow',
        back_populates='followed',
        foreign_keys='[Follow.followed_id]',
        lazy='selectin',
    )
    following = relationship(
        'Follow',
        back_populates='follower',
        foreign_keys='[Follow.follower_id]',
        lazy='selectin',
    )


class Tweet(Base):
    """Модель твит"""

    __tablename__ = 'tweets'
    __table_args__ = {'extend_existing': True}
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    content_data: str = Column(String, nullable=False)
    attachments = Column(ARRAY(Integer))
    user = relationship('User', back_populates='tweets', lazy='joined')
    likes = relationship('Like', back_populates='tweet', lazy='select', cascade='all, delete-orphan')


class Like(Base):
    """Модель лацк"""

    __tablename__ = 'likes'
    __table_args__ = {'extend_existing': True}
    tweet_id: int = Column(Integer, ForeignKey('tweets.id'), nullable=False, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=False, primary_key=True)
    tweet = relationship('Tweet', back_populates='likes')
    user = relationship('User', back_populates='likes')


class Media(Base):
    """Модель медиа"""

    __tablename__ = 'medias'
    __table_args__ = {'extend_existing': True}
    id: int = Column(Integer, primary_key=True)
    path_file: str = Column(String, nullable=False)
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=False)


class Follow(Base):
    """Модель зафолловить"""

    __tablename__ = 'followers'
    __table_args__ = {'extend_existing': True}
    follower_id: int = Column(Integer, ForeignKey('users.id'), primary_key=True)
    followed_id: int = Column(Integer, ForeignKey('users.id'), primary_key=True)
    follower = relationship('User', foreign_keys=[follower_id])
    followed = relationship('User', foreign_keys=[followed_id])