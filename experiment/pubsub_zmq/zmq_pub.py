import signal
import time
import zmq


signal.signal(signal.SIGINT, signal.SIG_DFL)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://0.0.0.0:5555')

stateChange = False

while True:
    if stateChange:
        socket.send(b'State changed')
    else:
        socket.send(b'State unchanged')
    time.sleep(1)