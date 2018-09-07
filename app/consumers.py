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

        report_name = await parse_posts_info(links=links, consumer=self)

        await self.send(text_data=json.dumps({
            'method': 'report_completed',
            'report_name': report_name
        }))
