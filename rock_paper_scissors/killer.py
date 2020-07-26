import zmq

from commands import Command
from objects import Packet, Machine


context = zmq.Context()

print("Connecting to server port: 5555")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


if __name__ == '__main__':

    packet = Packet(to=Machine.SERVER.value)

    ans = input("KILL SERVER? [Y/N]: ").lower()

    if ans == 'y':
        print("KILLING SERVER")

        packet.set_command(Command.STOP.value)
        socket.send_pyobj(packet)

    else:
        print("FINE. SERVER LIVES")
