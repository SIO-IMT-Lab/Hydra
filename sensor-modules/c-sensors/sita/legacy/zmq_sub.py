# This module is an example of a networked message queue implemented with zeroMQ.
# This subscriber will run on the Hydra supervisor and receive SITA measurements published
# using zmq_pub.py running on the SITA SBC Raspberry Pi controller. The SITA controller
# will also log time-stamped surface tension measurements.
import zmq
host = '127.0.0.1'
port = 6789
ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect('tcp://%s:%s' % (host, port))
topics = ['weather']
for topic in topics:
    sub.setsockopt(zmq.SUBSCRIBE, topic.encode('utf-8'))
while True:
    topic_bytes, message_bytes = sub.recv_multipart()
    topic = topic_bytes.decode('utf-8')
    message = message_bytes.decode('utf-8')
    print('Subscribe: Topic:<%s> Message:<%s>' % (topic, message))
    