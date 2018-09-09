from channels.generic.websocket import AsyncWebsocketConsumer
import json

from app.common import parse_posts_info, get_comment_users, get_like_users


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

        if data['method'] == 'get_posts_stat':
            archive_name = await parse_posts_info(links=links, consumer=self)

            await self.send(text_data=json.dumps({
                'method': 'report_completed',
                'archive_name': archive_name
            }))

        elif data['method'] == 'get_like_users':
            like_users_file = await get_like_users(links)

            await self.send(text_data=json.dumps({
                'method': 'like_users_parsed',
                'like_users_file': like_users_file
            }))

        elif data['method'] == 'get_comment_users':
            comment_users_file = await get_comment_users(links)

            await self.send(text_data=json.dumps({
                'method': 'comment_users_parsed',
                'comment_users_file': comment_users_file
            }))