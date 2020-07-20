from typing import Optional

from enum import Enum


class Move(Enum):

    ROCK     = 1,  "ROCK BREAKS SCISSORS"
    PAPER    = 2,  "PAPER WRAPS ROCK"
    SCISSORS = 3,  "SCISSORS CUT PAPER"
    DRAW     = -1, "GAME DRAW"

    def __new__(cls, value, reason):

        new_obj = object.__new__(cls)
        new_obj._value_ = value
        new_obj.reason  = reason

        return new_obj


class Status(Enum):

    PLAYING = 1
    WAITING = 2
    DONE    = 3


class Player:

    def __init__(self, id_: int, assigned: bool=False):

        self.id       = id_
        self.assigned = assigned

        self.move   = None
        self.status = None

    def reset(self):

        self.assigned = False
        self.move     = None
        self.status   = None

    def assign(self):

        self.assigned = True

    def is_assigned(self):

        return self.assigned

    def get_id(self) -> int:

        return self.id

    def set_move(self, move: Move):

        self.move = move

    def get_move(self) -> Move:

        return self.move

    def set_status(self, status: Status):

        self.status = status


class Result:

    def __init__(self):

        self.winner = None
        self.reason = None
        self.draw   = False

    def set_winner(self, player: Player):

        self.winner = player

    def get_winner(self) -> Player:

        return self.winner

    def set_reason(self, reason: Move):

        self.reason = reason

    def get_reason(self) -> Move:

        return self.reason

    def set_draw(self):
        self.draw = True

    def is_draw(self) -> bool:
        return self.draw


class Game:

    MAX_PLAYERS = 2

    def __init__(self):

        self.id = None
        self.no_of_players = 0
        self.player_1 = Player(1)
        self.player_2 = Player(2)
        self.game_full = False

    def get_result(self) -> Result:

        result = Result()

        move_1 = self.player_1.get_move()
        move_2 = self.player_2.get_move()

        if not move_1 or not move_2:

            return result

        if move_1 % 3 + 1 == move_2:
            winner = self.player_2

        elif move_2 % 3 + 1 == move_1:
            winner = self.player_1

        else:
            result.set_draw()
            result.set_reason(Move.DRAW.reason)

            return result

        result.set_winner(winner)
        result.set_reason(winner.get_move().reason)

    def set_full(self):

        self.game_full = True

    def is_full(self) -> bool:

        return self.game_full

    def set_id(self, id_: int):

        self.id = id_

    def get_id(self) -> int:

        return self.id

    def get_no_players(self) -> int:

        return self.no_of_players

    def remove_player(self, id_: int):

        if id_ == 1:
            self.player_1.reset()
            self.decrement_player()

        elif id_ == 2:
            self.player_2.reset()
            self.decrement_player()

    def increment_players(self):

        if self.no_of_players < self.MAX_PLAYERS:
            self.no_of_players += 1

    def decrement_player(self):

        if self.no_of_players <= 0:
            return

        self.no_of_players -= 1

    def get_player(self, id_: int) -> Player:

        if id_ == self.player_1.get_id():
            return self.player_1

        if id_ == self.player_2.get_id():
            return self.player_2


class GameManager:

    def __init__(self):

        self.games = {}

    def create_game(self) -> Game:

        game = Game()

        id_ = self.generate_game_id()
        game.set_id(id_)
        game.increment_players()
        game.player_1.assign()

        self.add_game(game)

        return game

    def join_game(self, game_id: int) -> Optional[int]:
        """Joins game and returns player_id"""

        game = self.get_game(game_id)

        if game.is_full():
            return

        player = None

        if not game.player_1.is_assigned():
            player = game.player_1

        elif not game.player_2.is_assigned():
            player = game.player_2

        player.assign()
        player_id = player.get_id()
        game.increment_players()

        return player_id

    def leave_game(self, game_id: int, player_id: int):

        game = self.get_game(game_id)
        game.remove_player(player_id)

    def set_move(self, game_id: int, player_id: int, move: Move) -> Game:

        game   = self.get_game(game_id)
        player = game.get_player(player_id)

        player.set_move(move)

        return game

    def add_game(self, game: Game):

        self.games[game.get_id()] = game

    def get_game(self, id_: int) -> Game:

        return self.games.get(id_)

    def is_game_full(self, game_id: int):

        game = self.get_game(game_id)

        return game.is_full()

    def remove_game(self, game: Game):

        id_ = game.get_id()

        if self.games.get(id_):
            del self.games[id_]

    def generate_game_id(self):
        return max(list(self.games.keys()))

    def get_total_games(self) -> int:
        return len(list(self.games.keys()))


class Machine(Enum):

    SERVER = "server"
    CLIENT = "client"


class Packet:

    def __init__(self, to: Machine):

        self.to = to

        self.command   = None
        self.game      = None
        self.game_id   = None
        self.player_id = None
        self.move      = None
        self.result    = None
        self.game_full = False

    def set_command(self, command):

        self.command = command

    def get_command(self):

        return self.command

    def set_game(self, game: Game):

        self.game = game

    def get_game(self) -> Game:

        return self.game

    def set_game_id(self, game_id: int):

        self.game_id = game_id

    def get_game_id(self) -> int:

        return self.game_id

    def set_move(self, move: Move):

        self.move = move

    def get_move(self):

        return self.move

    def set_result(self, result: Result):

        self.result = result

    def get_result(self) -> Result:

        return self.result

    def set_player_id(self, id_: int):

        self.player_id = id_

    def get_player_id(self) -> int:

        return self.player_id

    def set_game_full(self, flag: bool):

        self.game_full = flag

    def is_game_full(self) -> bool:

        return self.game_full
