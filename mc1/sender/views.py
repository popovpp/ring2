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
from confluent_kafka import Producer, Consumer


from sender.serializers import MessageSerializer
from sender.models import Message

running = True
SESSION_ID = 1
START_TIME = None
DURATION = None
consumer = None
producer = None
start = False


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
    new_message = {'session_id': SESSION_ID,
                   'MC1_timestamp':str(timezone.now()),
                   'MC2_timestamp':None, 
                   'MC3_timestamp':None,
                   'end_timestamp':None}
    serializer = MessageSerializer(new_message)
    uri = "ws://web1:8001/ws/line/"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({'message':serializer.data}))
            

async def new_kafka_message(START_TIME=None, DURATION=None, SESSION_ID=None):
    global producer

    conf = {'bootstrap.servers': "kafka:9092",
            'client.id': socket.gethostname()}
    producer = Producer(conf)
    
    print(START_TIME, DURATION, SESSION_ID)
    new_message = {'session_id': SESSION_ID,
                   'MC1_timestamp':str(timezone.now()),
                   'MC2_timestamp':None, 
                   'MC3_timestamp':None,
                   'end_timestamp':None}
    serializer = MessageSerializer(new_message)
    producer.produce('mc1_mc2', key="mc1", value=json.dumps(serializer.data), 
                     callback=acked)
    producer.poll(1)


def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced to mc2: %s" % (str(msg)))


@database_sync_to_async
def get_messages_count():
    return str(Message.objects.filter(session_id=views.SESSION_ID).count())


@database_sync_to_async
def save_message_db(message=None):

    serializer = MessageSerializer(data=message)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return message


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
        global running

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
        
#        loop = asyncio.new_event_loop()
#        asyncio.set_event_loop(loop)
#        result = loop.run_until_complete(
#            new_kafka_message(START_TIME=START_TIME, DURATION=DURATION, SESSION_ID=SESSION_ID)
#        ) 
#        start = True
        
#        t1 = threading.Thread(target=basic_consume_loop,  
#                              daemon=True)
#        t1.start()
        basic_consume_loop()

        return Response('START ' + str(timezone.now()), status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path="stop", 
            url_name="stop",
            permission_classes=[AllowAny])
    def stop(self, request, **kwargs):
        print('STOP', timezone.now())  
        return Response('STOP ' + str(timezone.now()), status=status.HTTP_200_OK)


def basic_consume_loop():
    global running
    global producer
    global SESSION_ID
    global START_TIME
    global DURATION
    global consumer
    global start
    
    print('#############################3')

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
        producer.poll(0.1)

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
 #               print(msg.value())
                message = msg.value()
                message = json.loads(message.decode('utf-8'))
                message['end_timestamp'] = str(timezone.now())
                print(message)
                serializer = MessageSerializer(data=message)
                serializer.is_valid(raise_exception=True)
                serializer.save()
#                message_instance = await save_message_db(message=message)
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
#                    producer.poll(0.1)
#                    producer.flush()
                except Exception as e:
                    print('STOP', timezone.now())
                    print('Session duration:', (timezone.now()-START_TIME).seconds, 'seconds')
                    print('Count of messages:', str(Message.objects.filter(session_id=SESSION_ID).count()))
                    shutdown()

                
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    global running
    running = False

#time.sleep(15)
#basic_consume_loop()
