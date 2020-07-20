import zmq

from typing import Optional

from commands import Command
from objects import Packet, Machine

from objects import GameManager


context = zmq.Context()
socket  = context.socket(zmq.REP)


print("BINDING TO PORT: 5555")
socket.bind("tcp://*:5555")


class CommandParser:

    def __init__(self, packet: Packet):

        self.received_packet = packet

    def parse(self) -> Optional[Packet]:

        command = self.received_packet.get_command()

        if command == Command.STOP.value:
            return

        if command == Command.CREATE.value:

            game   = GameManager().create_game()
            packet = Packet(to=Machine.CLIENT.value)

            packet.set_game(game)
            packet.set_player_id(game.get_player(1).get_id())

            return packet

        if command == Command.JOIN.value:

            player_id = GameManager().join_game(self.received_packet.get_game_id())

            return Packet(to=Machine.CLIENT.value).set_player_id(player_id)

        if command == Command.PLAY.value:

            game      = self.received_packet.get_game()
            player_id = self.received_packet.get_player_id()

            GameManager().set_move(
                game.get_id(),
                player_id,
                self.received_packet.get_move()
            )

            return Packet(to=Machine.CLIENT.value).set_result(game.get_result())

        if command == Command.LEAVE.value:

            GameManager().leave_game(
                self.received_packet.get_game_id(),
                self.received_packet.get_player_id()
            )

            return Packet(to=Machine.CLIENT.value)

        if command == Command.CHECK.value:

            game_full = GameManager().is_game_full(self.received_packet.get_game_id())

            return Packet(to=Machine.CLIENT.value).set_game_full(game_full)


if __name__ == '__main__':

    while True:

        received_packet = socket.recv_pyobj()
        send_packet     = CommandParser(received_packet).parse()

        if not send_packet:
            break

        socket.send_pyobj(send_packet)
