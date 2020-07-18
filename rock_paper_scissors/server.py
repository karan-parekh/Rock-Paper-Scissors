import zmq


from typing import Optional


context = zmq.Context()
socket  = context.socket(zmq.REP)

print("BINDING TO PORT: 5555")
socket.bind("tcp://*:5555")


if __name__ == '__main__':

    while True:

        packet = socket.recv_pyobj()


