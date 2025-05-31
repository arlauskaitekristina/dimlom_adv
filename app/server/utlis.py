from database import session
from routes import Follow, Like, Media, Tweet, User
from schemas import UserOutSchema
from sqlalchemy import func
from sqlalchemy.future import select


async def get_users_info(user_id, user_name):
    followers_data = await session.execute(
        select(Follow).where(Follow.followed_id == int(user_id)),
    )
    follow_list = [[], []]
    for followers in followers_data.scalars():
        name_user = await session.execute(
            select(User).where(User.id == followers.follower_id),
        )
        follow_list[0].append({
            'id': followers.follower_id,
            'name': name_user.scalar().name,
        })

    followers_data = await session.execute(
        select(Follow).where(Follow.follower_id == int(user_id)),
    )
    for followed in followers_data.scalars():
        name_user = await session.execute(
            select(User).where(User.id == followed.followed_id),
        )
        follow_list[1].append({
            'id': followed.followed_id,
            'name': name_user.scalar().name,
        })

    return UserOutSchema(
        id=user_id,
        name=user_name,
        followers=follow_list[0],
        following=follow_list[1],
    )


async def get_user(api_key):
    user_select = await session.execute(
        select(User).where(User.api_key == api_key),
    )
    return user_select.scalar()


async def get_tweets(id_f):
    follower_count = await session.execute(
        select(func.count()).select_from(Follow).where(Follow.followed_id == id_f),
    )
    follower_count = follower_count.scalar()
    tweet_select = await session.execute(
        select(Tweet).where(Tweet.user_id == id_f),
    )

    return tweet_select.scalars(), follower_count if isinstance(follower_count, int) else 0


async def get_likes_for_tweet(tweet_id):
    likes = []
    like_d = await session.execute(
        select(Like).where(Like.tweet_id == tweet_id),
    )
    for like in like_d.scalars():
        name_user = await session.execute(
            select(User).where(User.id == like.user_id),
        )
        likes.append({
            'user_id': like.user_id,
            'name': name_user.scalar().name,
        })
    return likes


async def get_attachments_for_tweet(tweet):
    attachments = []
    for file_id in tweet.attachments:
        attachments_d = await session.execute(
            select(Media.path_file).where(Media.id == int(file_id)),
        )
        attachments.append(attachments_d.scalar())
    return attachments


async def get_tweets_info(tweets_users):
    data_tweets = []
    for elem in tweets_users[0]:
        likes = await get_likes_for_tweet(elem.id)
        attachments = await get_attachments_for_tweet(elem)

        data_tweets.append({
            'id': elem.id,
            'content': elem.content_data,
            'attachments': attachments,
            'author': {
                'id': elem.user_id,
                'name': elem.user.name,
            },
            'likes': likes,
        })

    return data_tweets


async def get_tweets_sort():

    user = await session.execute(select(User))
    users_ids = [user.id for user in user.scalars()]
    tweets = []
    for id_f in users_ids:
        data_d = await get_tweets(id_f)
        tweets.append(data_d)
    return tweets
