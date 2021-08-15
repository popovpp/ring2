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

from sender.serializers import MessageSerializer
from sender.models import Message


SESSION_ID = 1
#DURATION = 10


@database_sync_to_async
def get_SESSION_ID():
    count = Message.objects.latest('id').session_id
    print(count)
    return count


class MessageViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = MessageSerializer
    queryset = Message.objects.all().order_by('id')
    DURATION = 2

    @action(methods=['GET'], detail=False, url_path="start", 
            url_name="start",
            permission_classes=[AllowAny])
    def start(self, request, **kwargs):
        START_TIME = timezone.now()
        print('START', START_TIME)
        try:
            SESSION_ID = Message.objects.latest('id').session_id + 1
        except Exception as e:
            SESSION_ID = 0
        
        while (timezone.now()-START_TIME).seconds < self.DURATION:
            new_message = {'session_id': SESSION_ID,
                           'MC1_timestamp':str(timezone.now()),
                           'MC2_timestamp':None, 
                           'MC3_timestamp':None,
                           'end_timestamp':None}
            serializer = MessageSerializer(new_message)
            response = requests.post('http://web1:8001/messages/', data=serializer.data)
#            print(response.json())
            instance = response.json()
            instance['end_timestamp'] = str(timezone.now())
            serializer = MessageSerializer(data=instance)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        count_str = str(Message.objects.filter(session_id=SESSION_ID).count())
        print('Длительность сеанса:', (timezone.now()-START_TIME).seconds, 'секунд')
        print('Количество сообщений:', count_str)
        return Response('STOP ' + str(timezone.now()) + ', ' + count_str, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path="stop", 
            url_name="stop",
            permission_classes=[AllowAny])
    def stop(self, request, **kwargs):
        print('STOP', timezone.now())
        self.DURATION = 0  
        return Response('STOP ' + str(timezone.now()), status=status.HTTP_200_OK)

    def create(self, request):
        
        print('in the post of mc1')
        print(request.data)
        serializer = MessageSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.data
        instance['end_timestamp'] = str(timezone.now())
#        serializer = MessageSerializer(data=instance)
#        serializer.is_valid(raise_exception=True)
#        serializer.save()

#        if (timezone.now()-datetime.strptime(instance.MC1_timestamp, 
#        	                        "%Y-%m-%dT%H:%M:%SZ")).seconds < DURATION:
#	        new_message = Message.objects.create(session_id=SESSION_ID,
#                                  MC1_timestamp=tinezone.now(),
#                                  MC2_timestamp=None, 
#                                  MC3_timestamp=None,
#                                  end_timestamp=None)
#	        response = requests.post('http://web1_1:8001/messages/', data=new_message)

        return Response(serializer.data, status=status.HTTP_200_OK)
