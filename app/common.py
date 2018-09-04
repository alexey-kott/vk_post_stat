import json
from asyncio import sleep
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Union

from aiohttp import ClientSession

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
    name: str  # V
    club_link: str  # V
    community_members: int  # V
    coverage: int
    likes: int  # V
    reposts: int  # ???
    comment_amount: int  # V
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

            print(response.real_url)

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
async def get_post_stat(owner_id: int, post_id: int):
    params['owner_id'] = owner_id
    params['post_id'] = post_id
    params['count'] = 1000
    url = "https://api.vk.com/method/stats.getPostReach"

    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            text = await response.text()
            data = json.loads(text)

            print(response.real_url)

            print(data)


def write(data: str) -> None:
    with open("data.json", "w") as file:
        file.write(data)


async def parse_post_info():
    links = ["https://vk.com/true_lentach?w=wall-125004421_2045921",
             # "https://vk.com/wall-146062039_53470",
             # "https://vk.com/wall-156003502_46435",
             # "https://vk.com/wall-67655918_36202",
             # "https://vk.com/wall-141790181_42079",
             # "https://vk.com/wall-147325343_386748",
             # "https://vk.com/wall-159071178_19866",
             # "https://vk.com/wall-156437731_46196",
             # "https://vk.com/wall-141744392_83802",
             # "https://vk.com/wall-104894009_102413",
             # "https://vk.com/wall-159071189_7290",
             # "https://vk.com/wall-158192742_43804",
             # "https://vk.com/wall-159071186_47872"
             ]

    posts = set()

    groups = await get_groups_info(links)
    id_group_map = {group['id']: group for group in groups}

    for link in links:
        try:
            owner_id = int(link.split('wall')[1].split('_')[0])  # owner -- group, public page or user
            post_id = int(link.split('-')[1].split('_')[1])

            # likes, like_users = await get_post_likes(owner_id, post_id)
            # comments_amount, comments = await get_post_comments(owner_id, post_id)

            # repost_items, repost_profiles, repost_groups = await get_post_reposts(owner_id, post_id)

            # members, member_items = await get_community_members(owner_id)

            stat = await get_post_stat(owner_id, post_id)



        except KeyError as e:
            print(e)
