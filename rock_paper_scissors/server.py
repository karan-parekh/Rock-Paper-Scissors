import zmq

from typing import Optional

context = zmq.Context()
socket  = context.socket(zmq.REP)

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

        self.id      = 0
        self.players = 0
        self.p1_move = ''
        self.p2_move = ''


games = {}


def get_winner(game: Game) -> dict:

    print("DETERMINING WINNER")

    win = {
        'player': 0,
        'reason': ''
    }

    p_beat_r = "PAPER WRAPS ROCK"
    r_beat_s = "ROCK BREAKS SCISSORS"
    s_beat_p = "SCISSORS CUT PAPER"
    tie      = "GAME WAS TIED. PLAY AGAIN"

    if not game.p1_move or not game.p2_move:
        print("NOT ENOUGH MOVES")
        return win

    if game.p1_move == game.p2_move:
        win['player'] = -1
        win['reason'] = tie

        print("NO WINNER")
        return win

    state = {
        game.p1_move : 1,
        game.p2_move : 2,
    }

    chances = {
        {'p', 'r'}: {'move': 'p', 'reason': p_beat_r},
        {'r', 's'}: {'move': 'r', 'reason': r_beat_s},
        {'s', 'p'}: {'move': 's', 'reason': s_beat_p}
    }

    c = chances[{game.p1_move, game.p2_move}]

    win['player'] = state[c['move']]
    win['reason'] = c['reason']

    print("WINNER IS: {}".format(win['player']))

    return win


def set_move(turn: dict, game: Game) -> Game:

    print("SETTING MOVES")

    if turn['player_id'] == 1:
        game.p1_move = turn['move']

    if turn['player_id'] == 2:
        game.p2_move = turn['move']

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
            print("STOPPING SERVER")
            break
