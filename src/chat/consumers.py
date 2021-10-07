from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Thread, ChatMessage
from datetime import datetime


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """Connect to websocket """

        other_user = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user']
        self.thread,_ = await self.get_thread(self.user, other_user)
        self.group_name = f'chat_{self.thread.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        

    async def receive_json(self, content, **kwargs):
        """Receive message"""

        data = content.get('message', None)
        if data is not None:
            username = 'default'
            if self.user.is_authenticated:
                username = self.user.username
                
            await self.save_chat_messsage(self.user, data)
            content = {
                'message': data, 
                'username': username, 
                'sent_time': datetime.now().strftime('%b. %d, %Y, %I:%M%p.')
            }

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message_handle',
                    'message': content
                }
            )
            

    async def chat_message_handle(self, event):
        await self.send_json(content = event['message'])
        

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    @database_sync_to_async
    def get_thread(self, user, other_user):
        return Thread.objects.get_or_new(user, other_user)

    @database_sync_to_async
    def save_chat_messsage(self, me, msg):
        return ChatMessage.objects.create(
            thread= self.thread,
            user = me,
            message = msg
        )