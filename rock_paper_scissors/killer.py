import zmq

context = zmq.Context()

print("Connecting to server port: 5555")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


if __name__ == '__main__':
    ans = input("KILL SERVER? [Y/N]: ").lower()

    if ans == 'y':
        print("KILLING SERVER")
        socket.send_pyobj({'cmd': 'stop'})

    else:
        print("FINE. SERVER LIVES")
