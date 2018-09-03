import json
from asyncio import sleep

from aiohttp import ClientSession

from vk_post_stat.settings import VK_SERVICE_TOKEN


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


async def get_post_comments(post_link):
    post_identificator = post_link.split('-')[1]
    owner_id = post_identificator.split('_')[0]
    post_id = post_identificator.split('_')[1]
    params = {
        'v': '5.84',
        'access_token': VK_SERVICE_TOKEN,
        'owner_id': '-'+owner_id,
        'post_id': post_id,
        'offset': 0,
        'count': 1000
    }
    url = "https://api.vk.com/method/wall.getComments"

    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            text = await response.text()
            data = json.loads(text)

            print(response.real_url)

            with open("data.json", "w") as file:
                file.write(text)


async def parse_post_info():
    links = ["https://vk.com/wall-146062039_53470",
             "https://vk.com/wall-156003502_46435",
             "https://vk.com/wall-67655918_36202",
             "https://vk.com/wall-141790181_42079",
             "https://vk.com/wall-147325343_386748",
             "https://vk.com/wall-159071178_19866",
             "https://vk.com/wall-156437731_46196",
             "https://vk.com/wall-141744392_83802",
             "https://vk.com/wall-104894009_102413",
             "https://vk.com/wall-159071189_7290",
             "https://vk.com/wall-158192742_43804",
             "https://vk.com/wall-159071186_47872"
             ]



    for link in links:
        post_comments = await get_post_comments(link)
        sleep(0.2)
