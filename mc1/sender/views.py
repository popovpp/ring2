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
import time
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException


from sender.serializers import MessageSerializer
from sender.models import Message


def acked(err, msg):
    pass


class MessageViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = MessageSerializer
    queryset = Message.objects.all().order_by('id')

    @action(methods=['GET'], detail=False, url_path="start", 
            url_name="start",
            permission_classes=[AllowAny])
    def start(self, request, **kwargs):

        START_TIME = timezone.now()
        print('START', START_TIME)
        try:
            DURATION = int(request.GET["duration"])
        except Exception as e:
            DURATION = 10
        try:
            SESSION_ID = Message.objects.latest('id').session_id + 1
            print(SESSION_ID)
        except Exception as e:
            SESSION_ID = 0
        basic_consume_loop(START_TIME, DURATION, SESSION_ID)

        return Response('STOP ' + str(timezone.now()), status=status.HTTP_200_OK)


def basic_consume_loop(START_TIME, DURATION, SESSION_ID):
    
    print('#############################3')
    print(SESSION_ID)

    conf_cons = {'bootstrap.servers': "kafka:9092",
        'group.id': "foo",
        'auto.offset.reset': 'smallest'}
    consumer = Consumer(conf_cons)

    conf1 = {'bootstrap.servers': "kafka:9092",
            'client.id': socket.gethostname()}
    producer = Producer(conf1)

    try:
        consumer.subscribe(['mc3_mc1',])
        new_message = {'session_id': SESSION_ID,
                       'MC1_timestamp':str(timezone.now()),
                       'MC2_timestamp':None, 
                       'MC3_timestamp':None,
                       'end_timestamp':None}
        serializer = MessageSerializer(new_message)
        producer.produce('mc1_mc2', key="mc1", value=json.dumps(serializer.data), 
                     callback=acked)
        producer.flush()

        running = True

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                message = msg.value()
                message = json.loads(message.decode('utf-8'))
                message['end_timestamp'] = str(timezone.now())
                print(message)
                serializer = MessageSerializer(data=message)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                try:
                    1/(DURATION - (timezone.now()-START_TIME).seconds)
                    new_message = {'session_id': SESSION_ID,
                                   'MC1_timestamp':str(timezone.now()),
                                   'MC2_timestamp':None, 
                                   'MC3_timestamp':None,
                                   'end_timestamp':None}
                    serializer = MessageSerializer(new_message)
                    producer.produce('mc1_mc2', key="mc1", value=json.dumps(serializer.data), 
                                 callback=acked)
                    producer.flush()
                except Exception as e:
                    print('STOP', timezone.now())
                    print('Session duration:', (timezone.now()-START_TIME).seconds, 'seconds')
                    print('Count of messages:', str(Message.objects.filter(session_id=SESSION_ID).count()))
                    running = False

                
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
