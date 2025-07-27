# See: https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html

import zmq
import random
import time

host = '*'
port = 6789
ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind('tcp://%s:%s' % (host, port))

time.sleep(1)
print('Publish: weather fine')
topic = 'weather'.encode('utf-8')
message = 'fine'.encode('utf-8')
pub.send_multipart([topic, message])