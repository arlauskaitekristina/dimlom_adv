from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from python_advanced_diploma.app.server.models import User
from python_advanced_diploma.app.server.utlis import get_user, get_users_info, get_tweets


async def test_route_get_user():
    user = await get_user('test')
    assert user.api_key == 'test'
    assert user.id == 1


async def test_route_get_user_info():
    user = await get_users_info(1, 'test_user')
    assert user.name == 'test_user'
    assert user.id == 1


async def test_route_get_tweets_info():
    tweet = await get_tweets(1)
    assert tweet[1] == 0



async def test_route_user_me(client, session):
    async with session:
        res = await session.execute(select(User).where(User.id == 1))

    get_user: User | None = res.scalar()
    api_key: str | None = get_user.api_key
    response = await client.get(
        "http://testhost/api/users/me", headers={"api-key": api_key}
    )
    assert response.status_code == 200
    assert response.json()["result"] is True
    assert 'name' in response.json()['user']


async def test_route_user_me_invalid_api_key(client):
    response = await client.get(
        'http://testhost/api/users/me', headers={'api-key': '123'}
    )
    assert response.status_code == 400

async def test_route_user_id(client, session):
    async with session:
        res = await session.execute(select(User).where(User.id == 1))

    get_user: User | None = res.scalar()
    api_key: str | None = get_user.api_key
    response = await client.get(
        "http://testhost/api/users/1", headers={"api-key": api_key}
    )
    assert response.status_code == 200
    assert response.json()["result"] is True

async def test_route_user_id_nonexistent(client):
    response = await client.get("http://testhost/api/users/999")
    assert response.status_code == 404

async def test_route_follow(client, session):
    async with session:
        res = await session.execute(select(User).where(User.id == 1))

    get_user: User | None = res.scalar()
    api_key: str | None = get_user.api_key
    response = await client.post(
        "http://testhost/api/users/2/follow", headers={"api-key": api_key}
    )
    assert response.status_code == 200
    assert response.json()["result"] is True

async def test_route_unfollow(client, session):
    async with session:
        res = await session.execute(select(User).where(User.id == 1))

    get_user: User | None = res.scalar()
    api_key: str | None = get_user.api_key
    response = await client.delete(
        "http://testhost/api/users/2/follow", headers={"api-key": api_key}
    )
    assert response.status_code == 200
    assert response.json()["result"] is True


async def test_route_tweet_post(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar()
    api_key: str | None = get_user.api_key

    new_tweet = {
        "tweet_data": "test tweet 1",
        "tweet_media_ids": []
    }
    response = await client.post(
        "http://testhost/api/tweets",
        headers={"api-key": api_key},
        json=new_tweet,
    )

    assert response.status_code == 200
    assert response.json()["result"] is True

async def test_route_tweet_get(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar()
    api_key: str | None = get_user.api_key

    response = await client.get(
        "http://testhost/api/tweets",
        headers={"api-key": api_key},
    )

    assert response.status_code == 200
    assert response.json()["result"] is True
    assert response.json()['tweets'][0]['content'] == 'test tweet 1'

async def test_route_tweet_like(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar()
    assert get_user.id == 1
    api_key: str | None = get_user.api_key
    response = await client.post(
        "http://testhost/api/tweets/1/likes",
        headers={"api-key": api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] is True

async def test_route_tweet_dislike(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar()
    api_key: str | None = get_user.api_key
    response = await client.delete(
        "http://testhost/api/tweets/1/likes",
        headers={"api-key": api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] is True

async def test_route_tweet_delete(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar()
    api_key: str | None = get_user.api_key
    response = await client.delete(
        "http://testhost/api/tweets/1",
        headers={"api-key": api_key},
    )
    assert response.status_code == 200
    assert response.json()["result"] is True

async def test_route_tweet_post_no_access(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar()

    new_tweet = {
        "tweet_data": "test tweet 1",
        "tweet_media_ids": []
    }
    response = await client.post(
        "http://testhost/api/tweets",
        headers={"api-key": '123'},
        json=new_tweet,
    )

    assert response.status_code == 400



async def test_route_follow_nonexistent_user(client, session):
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar()
    api_key: str | None = get_user.api_key
    response = await client.post(
        "http://testhost/api/users/999/follow", headers={"api-key": api_key}
    )
    assert response.status_code == 400
    assert response.json()['detail'] == 'User with this id doed not exist'

async def test_route_tweet_post_missing_fields(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar()
    api_key: str | None = get_user.api_key

    new_tweet = {
        "tweet_media_ids": []
    }
    response = await client.post("http://testhost/api/tweets", headers={"api-key": api_key}, json=new_tweet)
    assert response.status_code == 422

async def test_route_mass_tweet_creation(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar()
    api_key: str | None = get_user.api_key

    for i in range(100):  # Создаем 100 твитов
        new_tweet = {
            "tweet_data": f"test tweet {i}",
            "tweet_media_ids": []
        }
        response = await client.post("http://testhost/api/tweets", headers={"api-key": api_key}, json=new_tweet)
        assert response.status_code == 200
        assert response.json()['result'] is True


async def test_route_tweet_delete_nonexistent(session: AsyncSession, client: AsyncClient) -> None:
    async with session:
        get_user_select = await session.execute(select(User).where(User.id == 1))
    get_user: User | None = get_user_select.scalar()
    api_key: str | None = get_user.api_key

    response = await client.delete("http://testhost/api/tweets/999", headers={"api-key": api_key})
    assert response.status_code == 404
    assert  response.json()['detail'] == 'No tweet with this id'

async def test_route_tweet_media_missing_api_key(client):
    response = await client.post("http://testhost/api/medias", files={"file_media": ("test.jpg", b"test")})
    assert response.status_code == 422