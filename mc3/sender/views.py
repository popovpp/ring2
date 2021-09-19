from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from django.utils import timezone
import time
import json
import socket
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException

from sender.serializers import MessageSerializer


class MessageViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = MessageSerializer


def acked(err, msg):
    pass


def basic_consume_loop():

    running = True
    conf_prod = {'bootstrap.servers': "kafka:9092",
            'client.id': socket.gethostname()}
    producer = Producer(conf_prod)
    conf_cons = {'bootstrap.servers': "kafka:9092",
        'group.id': "foo3",
        'auto.offset.reset': 'smallest'}
    consumer = Consumer(conf_cons)
    try:
        consumer.subscribe(['mc2-mc3_1',])
        print('mc3 is ready.')
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
                message['MC3_timestamp'] = str(timezone.now())
                serializer = MessageSerializer(message)
                producer.produce('mc3-mc1_1', key="mc3", value=json.dumps(serializer.data), 
                                 callback=acked)
                producer.poll(1)

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


time.sleep(10)
basic_consume_loop()
