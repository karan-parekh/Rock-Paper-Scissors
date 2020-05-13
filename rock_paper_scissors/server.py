import enum
import zmq

from typing import Optional

context = zmq.Context()
socket  = context.socket(zmq.REP)

print("BINDING TO PORT: 5555")
socket.bind("tcp://*:5555")


class Status(enum.Enum):

    PLAYING = 1
    WAITING = 2
    DONE    = 3


class Move(enum.Enum):

    ROCK     = 1, "ROCK BREAKS SCISSORS"
    PAPER    = 2, "PAPER WRAPS ROCK"
    SCISSORS = 3, "SCISSORS CUT PAPER"
    DRAW     = -1, "GAME DRAW"

    def __new__(cls, value, reason):

        new_obj = object.__new__(cls)
        new_obj._value_ = value
        new_obj.reason  = reason

        return new_obj


class Packet:

    def __init__(self):

        self.game_id   = 0
        self.player_id = 0
        self.result    = {}
        self.game_full = False


class Player:

    def __init__(self, id_: int):

        self.id     = id_
        self.move   = None
        self.status = None


class Game:

    def __init__(self):

        self.id      = 0
        self.players = 0
        self.p1      = Player(1)
        self.p2      = Player(2)


games = {}


def get_result(game: Game) -> dict:

    print("DETERMINING WINNER")

    result = {
        'winner': 0,
        'reason': ''
    }

    if not game.p1.move or not game.p2.move:
        print("NOT ENOUGH MOVES")
        return result

    if game.p1.move.value % 3 + 1 == game.p2.move.value:
        result['winner'] = game.p2.id
        result['reason'] = game.p2.move.reason

    elif game.p2.move.value % 3 + 1 == game.p1.move.value:
        result['winner'] = game.p1.id
        result['reason'] = game.p1.move.reason

    else:
        result['player'] = -1
        result['reason'] = Move.DRAW.reason

    return result


def update_status(game: Game, pid: int, status: Status) -> Game:

    print("PLAYER {} STATUS UPDATED TO {}".format(pid, status.name))

    if pid == 1:
        game.p1.status = status.value

    if pid == 2:
        game.p2.status = status.value

    return game


def set_move(turn: dict, game: Game) -> Game:

    print("SETTING MOVES")

    if turn['player_id'] == 1:
        game.p1.move = turn['move']
        update_status(game, 1, Status.PLAYING)

    if turn['player_id'] == 2:
        game.p2.move = turn['move']
        update_status(game, 2, Status.PLAYING)

    return game


def get_game(id_: int) -> Optional[Game]:

    print("LOOKING FOR GAME WITH ID: {}".format(id_))

    g = games.get(id_)

    if not g:
        return

    print("FOUND GAME")

    return g


def create_game() -> Game:
    print("CREATING GAME")

    id_ = 1

    if games:
        id_ = max(list(games.keys())) + 1

    g = Game()
    g.id = id_
    g.players += 1

    games[id_] = g

    print("GAME CREATED WITH ID: {}".format(id_))

    return g


def reset_moves(game: Game) -> Game:

    game.p1.move = None
    game.p2.move = None

    return game


if __name__ == '__main__':

    while True:

        obj     = socket.recv_pyobj()
        command = obj['cmd']

        print("RECEIVED COMMAND: {}".format(command))

        if command == 'create':
            g = create_game()
            p = Packet()

            p.game_id   = g.id
            p.player_id = 1

            print("TOTAL PLAYERS: {}".format(g.players))

            socket.send_pyobj(p)
            continue

        if command == 'join':
            g = get_game(obj['game_id'])
            p = Packet()

            if not g:
                socket.send_pyobj(p)
                continue

            g.players += 1

            print("TOTAL PLAYERS: {}".format(g.players))

            if g.players > 2:
                p.game_id   = g.id
                p.game_full = True

                socket.send_pyobj(p)
                continue

            p.game_id   = g.id
            p.player_id = 2

            socket.send_pyobj(p)
            continue

        if command == 'play':
            g = set_move(obj, get_game(obj['game_id']))
            p = Packet()

            p.game_id   = g.id
            p.player_id = obj['player_id']

            res = get_result(g)

            if not res['winner']:
                g = update_status(g, obj['player_id'], Status.WAITING)
                socket.send_pyobj(p)
                continue

            p.result = res

            g = update_status(g, obj['player_id'], Status.DONE)

            if g.p1.status == Status.DONE.value and \
               g.p2.status == Status.DONE.value:
                g = reset_moves(g)

            socket.send_pyobj(p)
            continue

        if command == 'stop':
            print("STOPPING SERVER")
            break
