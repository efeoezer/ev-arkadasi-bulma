import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL'den sohbet (conversation) ID'sini alıyoruz
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Oda ismini belirliyoruz (örn: chat_room_12)
        self.room_group_name = f'chat_room_{self.room_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']

        # Mesajı veritabanına kaydet
        await self.save_message(self.room_id, self.user.id, message_content)

        # Odadaki herkese mesajı fırlat
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_id': self.user.id,
            }
        )

    async def chat_message(self, event):
        # Front-end'e JSON gönder
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id']
        }))

    @database_sync_to_async
    def save_message(self, room_id, sender_id, content):
        # Senin Message modeline göre kayıt işlemi
        return Message.objects.create(
            conversation_id=room_id,
            sender_id=sender_id,
            content=content
        )