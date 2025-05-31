import aiofiles
from database import session
from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from models import Follow, Like, Media, Tweet, User
from schemas import TweetSchema
from sqlalchemy import delete
from sqlalchemy.future import select
from utlis import get_tweets_info, get_tweets_sort, get_user, get_users_info

router = APIRouter()


@router.get(path='/users/me')
async def get_profile_my(api_key: str = Header(default=..., alias='api-key')):
    """
     Получите информацию обо мне

    Parameters:
        api_key (str): ключ API, используемый для идентификации пользователя

    Returns:
        dict:  Информация обо мне

    Raises:
        HTTPException:  Если пользователя нет в базе данных
    """


    result_user = await get_user(api_key)
    if result_user:
        user_model = await get_users_info(result_user.id, result_user.name)
        return {
            'result': True,
            'user': user_model.model_dump(),
        }
    raise HTTPException(status_code=400, detail='No user with this api-key')


@router.post(path='/tweets')
async def tweet_post(tweet_data: TweetSchema, api_key: str = Header(default=..., alias='api-key')):
    """
    Add post.

    Parameters:
        api_key (str): Ключ API, используемый для идентификации пользователя

    Returns:
        dict:  Информация об успехе

    Raises:
        HTTPException: Если ошибка в tweet_data
    """
    user = await get_user(api_key)
    if user:
        user_id = user.id
        tweet_model = Tweet(content_data=tweet_data.tweet_data, attachments=tweet_data.tweet_media_ids, user_id=user_id)
        session.add(tweet_model)
        await session.commit()
        await session.refresh(tweet_model)
        return {
            'result': True,
            'tweet_id': tweet_model.id,
        }
    raise HTTPException(status_code=400, detail='Access denied')


@router.post(path='/medias')
async def tweet_media(file_media: UploadFile = File(...), api_key: str = Header(default=..., alias='api-key')):
    """
    Добавить медиа

    Parameters:
        file_media (UploadFile): Файл медиа
        api_key (str): ключ API, используемый для идентификации пользователя.

    Returns:
        dict: Информация об успехе
    """


    user = await get_user(api_key)
    filelocation = './images/{file}'.format(file=file_media.filename)
    async with aiofiles.open(filelocation, 'wb') as outfile:
        content_media = await file_media.read()
        await outfile.write(content_media)
    media_model = Media(path_file=filelocation, user_id=user.id)
    session.add(media_model)
    await session.commit()
    await session.refresh(media_model)

    return {
        'result': True,
        'media_id': media_model.id,
    }


@router.delete(path='/tweets/{id_tweet}')
async def tweet_delete(id_tweet, api_key: str = Header(default=..., alias='api-key')):
    """
    Удалить свой твит

    Parameters:
        id_user (int): Идентификатор пользователя
        api_key (str): ключ API, используемый для идентификации пользователя

    Returns:
        dict: Информация об успехе

    """


    user = await get_user(api_key)
    tweet_deleting = await session.execute(select(Tweet).where(
        Tweet.id == int(id_tweet), Tweet.user_id == user.id,
    ),
    )
    tweet_to_delete = tweet_deleting.scalar()
    if tweet_to_delete:
        await session.delete(tweet_to_delete)
        await session.commit()
        return {'result': True}
    raise HTTPException(status_code=404, detail='No tweet with this id')


@router.post(path='/tweets/{id_tweet}/likes')
async def tweet_like(id_tweet, api_key: str = Header(default=..., alias='api-key')):
    """
    Отметить твит как понравившийся

    Parameters:
        id_user (int): Идентификатор пользователя
        api_key (str): ключ API, используемый для идентификации пользователя

    Returns:
        dict: Информация об успехе
    """


    user = await get_user(api_key)
    like_model = Like(tweet_id=int(id_tweet), user_id=user.id)
    session.add(like_model)
    await session.commit()
    await session.refresh(like_model)
    return {'result': True}


@router.delete(path='/tweets/{id_tweet}/likes')
async def tweet_unlike(id_tweet, api_key: str = Header(default=..., alias='api-key')):
    """
    Убрать отметку Нравится

    Parameters:
        id_user (int): Идентификатор пользователя
        api_key (str): ключ API, используемый для идентификации пользователя

    Returns:
        dict: Информация об успехе
    """


    user = await get_user(api_key)
    await session.execute(
        delete(Like).where(
            Like.user_id == user.id, Like.tweet_id == int(id_tweet),
        ),
    )
    await session.commit()
    return {'result': True}


@router.post(path='/users/{id_user}/follow')
async def tweet_follow(id_user, api_key: str = Header(default=..., alias='api-key')):
    """
    Зафоловить другого пользователя

    Parameters:
        id_user (int): Идентификатор пользователя
        api_key (str): ключ API, используемый для идентификации пользователя

    Returns:
        dict: Информация об успехе

    Raises:
        HTTPException: Если пользователя нет в базе данных
    """


    user = await get_user(api_key)
    check = await session.execute(
        select(User).where(User.id == int(id_user)),
    )
    if check.scalar():
        follow_model = Follow(follower_id=user.id, followed_id=int(id_user))
        session.add(follow_model)
        await session.commit()
        await session.refresh(follow_model)
        return {'result': True}
    raise HTTPException(status_code=400, detail='User with this id doed not exist')


@router.delete(path='/users/{id_user}/follow')
async def tweet_unfollow(id_user, api_key: str = Header(default=..., alias='api-key')):
    """
    Отменить подписку на пользователя по идентификатору

    Parameters:
        id_user (int): Идентификатор пользователя
        api_key (str): ключ API, используемый для идентификации пользователя

    Returns:
        dict: Информация об успехе
    """


    user = await get_user(api_key)
    await session.execute(
        delete(Follow).where(
            Follow.follower_id == user.id, Follow.followed_id == int(id_user),
        ),
    )
    await session.commit()
    return {'result': True}


@router.get(path='/tweets')
async def tweet_get() -> dict:
    """
    Получить информацию о твитах

    Returns:
        dict: Словарь, содержащий информацию о твитах.
    """
    tweets = await get_tweets_sort()
    data_tweets = {
        'result': True,
        'tweets': [
        ],
    }
    tweets.sort(key=lambda x_1: x_1[1], reverse=True)
    for tweets_users in tweets:
        data_tweets['tweets'].extend(await get_tweets_info(tweets_users))
    return data_tweets


@router.get(path='/users/{user_id}')
async def get_profile_for_id(user_id):
    """
    Получите информацию о профиле пользователя по идентификатору пользователя.

    Parameters:
        user_id (int): идентификатор пользователя,

    Returns:
        dict: Информация о пользователе.

    Raises:
        HTTPException: Если пользователя нет в базе данных
    """
    user_select = await session.execute(
        select(User).where(User.id == int(user_id)),
    )
    name = user_select.scalar()
    if name:
        user_model = await get_users_info(user_id, name.name)
        return {
            'result': True,
            'user': user_model.model_dump(),
        }
    raise HTTPException(status_code=404, detail='No user with this id')
