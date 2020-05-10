import zmq

context = zmq.Context()

print("Connecting to server port: 5555")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

print("SENDING Hello")
socket.send(b"Hello")

print("WAITING FOR ANSWER")
msg = socket.recv()
print("RECEIVED RESPONSE: {}".format(msg))

