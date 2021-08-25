import json
import asyncio
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404
from channels.db import database_sync_to_async
from django.conf import settings
from django.utils import timezone

from sender.models import Message
from sender.serializers import MessageSerializer
from sender import views


WEBSOCKET = None


@database_sync_to_async
def get_messages_count():
    return str(Message.objects.filter(session_id=views.SESSION_ID).count())


@database_sync_to_async
def save_message_db(message=None):

    serializer = MessageSerializer(data=message)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return message


@database_sync_to_async
def read_db(amount_of_records=None):
    items_list = list(Message.objects.all().order_by('-pk'))
    length = len(items_list)
    if length < amount_of_records:
        return items_list[:length]
    else:
        return items_list[:amount_of_records]


class ChatConsumer(AsyncWebsocketConsumer):
    
    chanels_dict = {}

    async def connect(self):
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
        message['end_timestamp'] = str(timezone.now())

        await self.channel_layer.group_send(
              self.room_group_name,
              {
              'type': 'chat_message',
              'message': message
              }
        )

        # Send message to room group

        message_instance = await save_message_db(message=message)  

        uri = "ws://web1:8001/ws/line/"

        try:
            1/(views.DURATION - (timezone.now()-views.START_TIME).seconds)
            new_message = {'session_id': views.SESSION_ID,
                           'MC1_timestamp':str(timezone.now()),
                           'MC2_timestamp':None, 
                           'MC3_timestamp':None,
                           'end_timestamp':None}
            try:
                await WEBSOCKET.send(json.dumps({'message':new_message}))
            except Exception as e:
                WEBSOCKET = await websockets.connect(uri)
                await WEBSOCKET.send(json.dumps({'message':new_message}))
        except Exception as e:
            print('STOP', timezone.now())
            print('Session duration:', (timezone.now()-views.START_TIME).seconds, 'seconds')
            print('Count of messages:', await get_messages_count())


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
        