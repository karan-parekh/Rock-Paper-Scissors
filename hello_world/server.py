import zmq

from time import sleep

context = zmq.Context()
socket = context.socket(zmq.REP)

print("BINDING TO PORT: 5555")
socket.bind("tcp://*:5555")

while True:
    msg = socket.recv()

    print("RECEIVED REQUEST {}".format(msg))
    sleep(0.5)
    socket.send(b"World")
