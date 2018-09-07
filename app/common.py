import dataclasses
import json
import time
# from asyncio import sleep
from time import sleep
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Union

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from aiohttp import ClientSession
from channels.generic.websocket import AsyncWebsocketConsumer

from vk_post_stat.settings import VK_SERVICE_TOKEN

params = {
    'v': '5.84',
    'access_token': VK_SERVICE_TOKEN,
}


def delay(func):
    sleep(0.34)  # VK.com has limit no more 3 requests per second

    return func


@dataclass
class Post:
    post_link: str  # V
    club_name: str  # V
    club_link: str  # V
    members_amount: int  # V
    views: int  # V
    likes: int  # V
    # reposts: int  # ВК выключил
    comments_amount: int  # V
    comments: List[Dict[str, Any]]  # V


@delay
async def get_user_info(user_id):
    params = {
        'v': '5.84',
        'access_token': VK_SERVICE_TOKEN,
        'offset': 0,
        'count': 1000
    }
    url = "https://api.vk.com/method/wall.getComments"

    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            text = await response.text()


@delay
async def get_groups_info(links: List[str]) -> List[Dict[str, Any]]:  # get id, name, screen_name
    group_ids = [link.split('-')[1].split('_')[0] for link in links]

    params['group_ids'] = ','.join(group_ids)
    url = "https://api.vk.com/method/groups.getById"

    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            text = await response.text()
            data = json.loads(text)

            return data['response']


@delay
async def get_post_comments(owner_id: int, post_id: int) -> Tuple[int, List[Dict[str, Any]]]:
    params['owner_id'] = owner_id
    params['post_id'] = post_id
    params['count'] = 1000
    url = "https://api.vk.com/method/wall.getComments"

    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            text = await response.text()
            data = json.loads(text)

            return data['response']['count'], data['response']['items']


@delay
async def get_post_likes(owner_id: int, item_id: int) -> Tuple[int, List[int]]:
    params['type'] = 'post'
    params['owner_id'] = owner_id
    params['item_id'] = item_id
    params['count'] = 1000
    url = "https://api.vk.com/method/likes.getList"

    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            text = await response.text()
            data = json.loads(text)

            return data['response']['count'], data['response']['items']


@delay
async def get_post_reposts(owner_id: int, post_id: int) -> Tuple[List, List, List]:
    # Сейчас ВКонтакте возвращает пустые поля ответа, вряд ли это когда-то изменится
    # Связана такая ситуация с участившимися случаями посадки за репосты (ДА, ЭТО ПИЗДЕЦ)
    params['owner_id'] = owner_id
    params['post_id'] = post_id
    params['count'] = 1000
    url = "https://api.vk.com/method/wall.getReposts"

    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            text = await response.text()
            data = json.loads(text)

            return data['response']['items'], data['response']['profiles'], data['response']['groups']


@delay
async def get_community_members(group_id: Union[int, str]) -> Tuple[int, List[int]]:
    params['group_id'] = str(group_id).strip('-')
    params['count'] = 1000
    url = "https://api.vk.com/method/groups.getMembers"

    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            text = await response.text()
            data = json.loads(text)

            return data['response']['count'], data['response']['items']


@delay
async def get_post_views(owner_id: int, post_id: int) -> int:
    params['posts'] = f"{owner_id}_{post_id}"
    params['count'] = 1000
    url = "https://api.vk.com/method/wall.getById"

    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            text = await response.text()
            data = json.loads(text)

            return int(data['response'][0]['views']['count'])


def write(data: str) -> None:
    with open("data.json", "w") as file:
        file.write(data)


async def send_object_to_client(consumer: AsyncWebsocketConsumer, obj: Any) -> None:
    await consumer.send(text_data=json.dumps({
        'data': dataclasses.asdict(obj)
    }))


def get_file_name():
    str_time = str(time.time()).encode('utf-8')
    m = hashlib.md5()
    m.update(str_time)
    name_hash_part = m.hexdigest()[:10]

    return f"vk_post_stat-{name_hash_part}.xlsx"


def generate_excel(posts: List[Post]):
    wb = Workbook()
    ws = wb.create_sheet("Default", index=0)
    ws.append(['Ссылка на запись', 'Название сообщества',
               'Ссылка на сообщество', 'Количество подписчиков',
               'Охват записи', 'Количество лайков', 'Количество комментариев'])

    for i, post in enumerate(posts):
        ws.append([post.post_link, post.club_name, post.club_link, post.members_amount, post.views, post.likes, post.comments_amount])

    for i, column in enumerate(ws.columns):
        ws.column_dimensions[get_column_letter(i+1)].width = 25

    file_name = get_file_name()
    wb.save(f"./static/files/{file_name}")

    return file_name


async def parse_posts_info(links: List[str], consumer: AsyncWebsocketConsumer) -> str:
    posts = []

    groups = await get_groups_info(links)
    id_group_map = {-group['id']: group for group in groups}

    for link in links:
        try:
            owner_id = int(link.split('wall')[1].split('_')[0])  # owner -- group, public page or user
            post_id = int(link.split('-')[1].split('_')[1])

            likes, like_users = await get_post_likes(owner_id, post_id)
            comments_amount, comments = await get_post_comments(owner_id, post_id)
            # repost_items, repost_profiles, repost_groups = await get_post_reposts(owner_id, post_id)
            members, member_items = await get_community_members(owner_id)
            views = await get_post_views(owner_id, post_id)

            post = Post(club_link=id_group_map[owner_id]['screen_name'],
                        club_name=id_group_map[owner_id]['name'],
                        comments_amount=comments_amount,
                        members_amount=members,
                        comments=comments,
                        post_link=link,
                        likes=likes,
                        views=views,
                        )
            posts.append(post)

            await send_object_to_client(consumer, post)
        except Exception as e:
            print(e)

    return generate_excel(posts)
