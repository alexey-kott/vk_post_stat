from channels.generic.websocket import AsyncWebsocketConsumer
import json

from app.common import parse_posts_info


class AppConsumer(AsyncWebsocketConsumer):
    # groups = ["broadcast"]

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()
        print("WebSocket DISCONNECT")

    async def receive(self, text_data, **kwargs):
        data = json.loads(text_data)

        links = [link.strip(' ') for link in data['data'].split('\n') if link != '']

        for i in links:
            print(i)

        # links = ["https://vk.com/true_lentach?w=wall-125004421_2045921",
        #          "https://vk.com/wall-146062039_53470",
        #          "https://vk.com/wall-156003502_46435",
        #          "https://vk.com/wall-67655918_36202",
        #          "https://vk.com/wall-141790181_42079",
        #          "https://vk.com/wall-147325343_386748",
        #          "https://vk.com/wall-159071178_19866",
        #          "https://vk.com/wall-156437731_46196",
        #          "https://vk.com/wall-141744392_83802",
        #          "https://vk.com/wall-104894009_102413",
        #          "https://vk.com/wall-159071189_7290",
        #          "https://vk.com/wall-158192742_43804",
        #          "https://vk.com/wall-159071186_47872"
        #          ]

        posts = await parse_posts_info(links)
