from django.utils import timezone
import json
import time
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException

from sender.serializers import MessageSerializer


def acked(err, msg):
    pass


def basic_consume_loop():
    global running
    global producer

    running = True
    conf_prod = {'bootstrap.servers': "kafka:9092",
            'client.id': socket.gethostname()}
    producer = Producer(conf_prod)
    conf_cons = {'bootstrap.servers': "kafka:9092",
        'group.id': "foo",
        'auto.offset.reset': 'smallest'}
    consumer = Consumer(conf_cons)
    try:
        consumer.subscribe(['mc2_mc3',])

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
                producer.produce('mc3_mc1', key="mc3", value=json.dumps(serializer.data), 
                                 callback=acked)
                producer.flush()

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


time.sleep(20)
basic_consume_loop()
