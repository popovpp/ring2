from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import status
from django.utils import timezone
import requests
import socket
from datetime import datetime
from channels.db import database_sync_to_async
import asyncio
import threading
import websockets
import json

from sender.serializers import MessageSerializer
from sender.models import Message


SESSION_ID = 1
START_TIME = None
DURATION = None


def message_session(START_TIME=None, DURATION=None, SESSION_ID=None):
    while (timezone.now()-START_TIME).seconds < DURATION:
            new_message = {'session_id': SESSION_ID,
                           'MC1_timestamp':str(timezone.now()),
                           'MC2_timestamp':None, 
                           'MC3_timestamp':None,
                           'end_timestamp':None}
            serializer = MessageSerializer(new_message)
            response = requests.post('http://web1:8001/messages/', data=serializer.data)
            instance = response.json()
            instance['end_timestamp'] = str(timezone.now())
            serializer = MessageSerializer(data=instance)
            serializer.is_valid(raise_exception=True)
            serializer.save()
    count_str = str(Message.objects.filter(session_id=SESSION_ID).count())
    print('Session duration:', (timezone.now()-START_TIME).seconds, 'seconds')
    print('Count of messages:', count_str)


async def new_ws_message(START_TIME=None, DURATION=None, SESSION_ID=None):
    print(START_TIME, DURATION, SESSION_ID)
#    while (timezone.now()-START_TIME).seconds < DURATION:
    new_message = {'session_id': SESSION_ID,
                   'MC1_timestamp':str(timezone.now()),
                   'MC2_timestamp':None, 
                   'MC3_timestamp':None,
                   'end_timestamp':None}
    serializer = MessageSerializer(new_message)
    uri = "ws://web1:8001/ws/line/"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({'message':serializer.data}))
            
#    count_str = 'qqq'#str(Message.objects.filter(session_id=SESSION_ID).count())
#    print('Session duration:', (timezone.now()-START_TIME).seconds, 'seconds')
#    print('Count of messages:', count_str)


class MessageViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = MessageSerializer
    queryset = Message.objects.all().order_by('id')

    @action(methods=['GET'], detail=False, url_path="start", 
            url_name="start",
            permission_classes=[AllowAny])
    def start(self, request, **kwargs):
        global START_TIME
        global DURATION
        global SESSION_ID

        START_TIME = timezone.now()
        print('START', START_TIME)
        try:
            DURATION = int(request.GET["duration"])
        except Exception as e:
            DURATION = 10
        try:
            SESSION_ID = Message.objects.latest('id').session_id + 1
        except Exception as e:
            SESSION_ID = 0
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            new_ws_message(START_TIME=START_TIME, DURATION=DURATION, SESSION_ID=SESSION_ID)
        )       
        return Response('START ' + str(timezone.now()), status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path="stop", 
            url_name="stop",
            permission_classes=[AllowAny])
    def stop(self, request, **kwargs):
        print('STOP', timezone.now())  
        return Response('STOP ' + str(timezone.now()), status=status.HTTP_200_OK)
