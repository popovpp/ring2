from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
import requests
import time
import socket
import json
import asyncio
from confluent_kafka import Consumer, Producer

from sender.serializers import MessageSerializer


running = True
conf_prod = {'bootstrap.servers': "kafka:9092",
            'client.id': socket.gethostname()}
producer = Producer(conf_prod)


def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced to mc3: %s" % (str(msg)))


def basic_consume_loop():
    global running
    global producer

#    conf_prod = {'bootstrap.servers': "kafka:9092",
#            'client.id': socket.gethostname()}
#    producer = Producer(conf_prod)

    conf_cons = {'bootstrap.servers': "kafka:9092",
        'group.id': "foo",
        'auto.offset.reset': 'smallest'}
    consumer = Consumer(conf_cons)
    try:
        consumer.subscribe(['mc1_mc2',])

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
#                print(msg.value())
                message = msg.value()
                message = json.loads(message.decode('utf-8'))
                message['MC2_timestamp'] = str(timezone.now())
                print(message)
                serializer = MessageSerializer(message)
                producer.produce('mc2_mc3', key="mc2", value=json.dumps(serializer.data), 
                                 callback=acked)
                producer.poll(2)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False


class MessageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MessageSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.data
        instance['MC2_timestamp'] = str(timezone.now())
        response = requests.post('http://web2:8002/messages/', data=instance)
        serializer = MessageSerializer(data=response.json())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


time.sleep(10)
basic_consume_loop()
#loop = asyncio.new_event_loop()
#asyncio.set_event_loop(loop)
#result = loop.run_until_complete(
#            basic_consume_loop()
#        )
