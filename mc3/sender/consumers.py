import json
import websockets
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404
from channels.db import database_sync_to_async
from django.conf import settings
from django.utils import timezone

from sender.serializers import MessageSerializer


WEBSOCKET = None


class ChatConsumer(AsyncWebsocketConsumer):
    
    chanels_dict = {}

    async def connect(self):
        global WEBSOCKET
        WEBSOCKET = None
        self.room_name = 'line'
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        global WEBSOCKET

        text_data_json = json.loads(text_data)
        message = text_data_json['message']  

        # Send message to room group
        message['MC3_timestamp'] = str(timezone.now())
        uri = "ws://web:8000/ws/line/"
        try:
            await WEBSOCKET.send(json.dumps({'message':message}))
        except Exception as e:
            WEBSOCKET = await websockets.connect(uri)
            await WEBSOCKET.send(json.dumps({'message':message}))

        await self.channel_layer.group_send(
              self.room_group_name,
              {
              'type': 'chat_message',
              'message': message
              }
        )


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
        