from channels.generic.websocket import AsyncWebsocketConsumer
import json

from app.common import parse_post_info

class AppConsumer(AsyncWebsocketConsumer):
    # groups = ["broadcast"]

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()
        print("WebSocket DISCONNECT")

    async def receive(self, text_data, **kwargs):
        print(text_data)

        await parse_post_info()
