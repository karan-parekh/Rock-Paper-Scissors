import zmq

from typing import Optional

context = zmq.Context()
socket = context.socket(zmq.REP)

print("BINDING TO PORT: 5555")
socket.bind("tcp://*:5555")


class Packet:

    def __init__(self):

        self.game_id   = 0
        self.player_id = 0
        self.winner    = {}
        self.game_full = False


class Game:

    def __init__(self):

        self.id       = 0
        self.players  = 0
        self.player_1 = ''
        self.player_2 = ''


games = {}


def get_winner(game: Game) -> dict:

    p_beat_r = "PAPER WRAPS ROCK"
    r_beat_s = "ROCK BREAKS SCISSORS"
    s_beat_p = "SCISSORS CUT PAPER"

    win = {
        'player': 0,
        'reason': ''
    }

    if not game.player_1 or not game.player_2:
        return win

    if game.player_1 == 'p' and game.player_2 == 'r':
        win['player'] = 1
        win['reason'] = p_beat_r
        return win

    if game.player_1 == 'r' and game.player_2 == 'p':
        win['player'] = 2
        win['reason'] = p_beat_r
        return win

    if game.player_1 == 'r' and game.player_2 == 's':
        win['player'] = 1
        win['reason'] = r_beat_s
        return win

    if game.player_1 == 's' and game.player_2 == 'r':
        win['player'] = 2
        win['reason'] = r_beat_s
        return win

    if game.player_1 == 's' and game.player_2 == 'p':
        win['player'] = 1
        win['reason'] = s_beat_p
        return win

    if game.player_1 == 'p' and game.player_2 == 's':
        win['player'] = 2
        win['reason'] = s_beat_p
        return win


def set_move(turn: dict, game: Game) -> Game:

    if turn['player_id'] == 1:
        game.player_1 = turn['move']

    if turn['player_id'] == 2:
        game.player_2 = turn['move']

    return game


def get_game(id_: int) -> Optional[Game]:

    g = games.get(id_)

    if not g:
        return

    g.players += 1

    return g


def create_game() -> Game:

    id_ = 1

    if games:
        id_ = max(list(games.keys())) + 1

    g = Game()
    g.id = id_
    g.players += 1

    games[id_] = g

    return g


while True:

    obj = socket.recv_pyobj()
    command = obj['cmd']

    if command == 'create':
        g = create_game()
        p = Packet()

        p.game_id   = g.id
        p.player_id = 1

        socket.send_pyobj(p)
        continue

    if command == 'join':
        g = get_game(obj['id'])
        p = Packet()

        if not g:
            socket.send_pyobj(p)
            continue

        if g.players >= 2:
            p.game_id   = g.id
            p.game_full = True

            socket.send_pyobj(p)
            continue

        p.game_id   = g.id
        p.player_id = 2

        socket.send_pyobj(p)
        continue

    if command == 'play':
        g = set_move(obj, get_game(obj['id']))
        p = Packet()

        winner = get_winner(g)

        p.game_id   = g.id
        p.player_id = obj['player_id']

        if not winner['player']:
            socket.send_pyobj(p)
            continue

        p.winner = winner

        socket.send_pyobj(p)
        continue

    if command == 'stop':
        break
