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
        'group.id': "foo2",
        'auto.offset.reset': 'smallest'}
    consumer = Consumer(conf_cons)
    try:
        consumer.subscribe(['mc1-mc2_1',])
        print('mc2 is ready')
        count_of_loop = 0
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
                message['MC2_timestamp'] = str(timezone.now())
                serializer = MessageSerializer(message)
                producer.produce('mc2-mc3_1', key="mc2", value=json.dumps(serializer.data), 
                                 callback=acked)
                producer.poll(1)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


time.sleep(10)
basic_consume_loop()
