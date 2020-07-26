import time
import zmq

from objects import Packet, Move, Machine, Result
from commands import Command

from loguru import logger


context = zmq.Context()

print("Connecting to server port: 5555")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


MAIN_MENU_TEXT = """
Press C to create new game
Press J to join game
Press Q to quit
"""

TRY_AGAIN_TEXT = """
Incorrect Command. Try again
"""


class MainMenu:

    def __init__(self):

        self.command_map = {
            "c": Command.CREATE.value,
            "j": Command.JOIN.value,
            "q": Command.QUIT.value,
        }

    def get_command(self) -> Command:

        logger.info("Getting command")

        self._display_menu()
        command = input().lower()

        if command not in list(self.command_map.keys()):
            return self._try_again_get_command()

        return self.command_map[command]

    def _display_menu(self):

        print(MAIN_MENU_TEXT)

    def _try_again_get_command(self):

        print(TRY_AGAIN_TEXT)
        self._display_menu()

        return self.get_command()


MOVES_TEXT = """
Press R for ROCK
Press P for PAPER
Press S for SCISSORS
"""

REMATCH_TEXT = """
REMATCH? [Y/N]:
"""


JOIN_TEXT = """
Enter game id:
"""


class Session:

    def __init__(self):

        logger.info("Initiating session")

        self.game = None
        self.player_id = None

        self.move_map = {
            'r': Move.ROCK.value,
            'p': Move.PAPER.value,
            's': Move.SCISSORS.value,
        }

    def run(self, command: Command):

        logger.info("Running session")

        received_packet = None

        if command == Command.QUIT.value:

            self.quit()

        elif command == Command.CREATE.value:

            received_packet = self.create_game(command)

        elif command == Command.JOIN.value:

            received_packet = self.join_game()

        self.game      = received_packet.get_game()
        self.player_id = received_packet.get_player_id()

        logger.info("Current game id   : {}".format(self.game.id))
        logger.info("Current player id : {}".format(self.player_id))

        self.play()

    def create_game(self, command) -> Packet:

        logger.info("Creating game")

        packet = Packet(to=Machine.SERVER.value)

        packet.set_command(command)
        return self.send_packet(packet)

    def join_game(self):

        logger.info("Joining game with")

        inp = input(JOIN_TEXT).lower()

        try:
            game_id = int(inp)
        except ValueError:
            return self._try_again_join()

        packet = Packet(to=Machine.SERVER.value)

        packet.set_command(Command.JOIN.value)
        packet.set_game_id(game_id)

        return self.send_packet(packet)

    def play(self):

        logger.info("Game in PLAY state")

        packet = Packet(to=Machine.SERVER.value)

        move = self.get_move()
        packet.set_command(Command.PLAY.value)
        packet.set_game(self.game)
        packet.set_player_id(self.player_id)
        packet.set_move(move)

        result = self.wait_for_response(packet)

        self.display_result(result)

        if self.rematch():
            logger.info("Rematch confirmed")

            self.play()

        logger.info("Leaving game")

        packet.set_command(Command.LEAVE.value)

        self.send_packet(packet)

    def rematch(self) -> bool:

        inp = input(REMATCH_TEXT).lower()

        if inp == "y":
            return True

        return False

    def display_result(self, result: Result):

        if result.is_draw():
            print(" MATCH DRAW ")
            return

        winner = result.get_winner()

        if winner.get_id() == self.player_id:
            print(" YOU WON!! ")

        else:
            print(" YOU LOST ")

        print(result.get_reason())

    def wait_for_response(self, packet: Packet):
        """Waits for server to give a valid response"""

        try:
            while True:
                received_packet = self.send_packet(packet)
                result = received_packet.get_result()

                if result.get_winner():
                    return result

                elif result.is_draw():
                    return result

                time.sleep(1)
        except KeyboardInterrupt:
            return

    def quit(self):
        logger.info("Quitting session")
        exit()

    def send_packet(self, packet: Packet) -> Packet:
        """Sends packet and returns received packet"""

        socket.send_pyobj(packet)

        return socket.recv_pyobj()

    def get_move(self):

        self._display_moves()
        move = input().lower()

        if move not in list(self.move_map.keys()):
            self._try_again_moves()

        return Move(self.move_map[move])

    def _display_moves(self):

        print(MOVES_TEXT)

    def _try_again_moves(self):

        print(TRY_AGAIN_TEXT)
        self._display_moves()

        return self.get_move()

    def _try_again_join(self):

        print(TRY_AGAIN_TEXT)

        return self.join_game()


if __name__ == '__main__':

    session = Session()

    while True:

        command_ = MainMenu().get_command()
        session.run(command_)
