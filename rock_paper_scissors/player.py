import time
import zmq

context = zmq.Context()

print("Connecting to server port: 5555")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


class Packet:

    def __init__(self):

        self.game_id   = 0
        self.player_id = 0
        self.winner    = {}
        self.game_full = False


packet = {
    'cmd'       : '',
    'game_id'   : 0,
    'player_id' : 0,
    'move'      : ''
}


state = {
    'game_id'  : 0,
    'player_id': 0,
    'move'     : ''
}


def main():

    while True:

        cmd = input("PRESS C TO CREATE GAME\nPRESS J TO JOIN\n:").lower()

        if cmd == 'c':
            print("CREATING GAME")
            packet['cmd'] = 'create'
            socket.send_pyobj(packet)

            p = socket.recv_pyobj()
            print("YOU CREATED GAME WITH ID: {}".format(p.game_id))

            return p

        if cmd == 'j':
            packet['cmd']     = 'join'
            packet['game_id'] = state['game_id'] = int(input("ENTER GAME ID: "))
            print("JOINING GAME")

            socket.send_pyobj(packet)

            p = socket.recv_pyobj()

            if p.game_full:
                print("GAME IS FULL. TRY ANOTHER ID OR CREATE A NEW GAME")
                continue

            return p

        print("TRY AGAIN")


def wait_for_response(p):
    print("WAITING FOR RESPONSE")

    while True:

        socket.send_pyobj(p)

        res = socket.recv_pyobj()

        if not res.winner:
            time.sleep(1)
            continue

        return res.winner


if __name__ == '__main__':

    moves = {
        'r': 'ROCK',
        'p': 'PAPER',
        's': 'SCISSORS'
    }

    obj = main()

    state['game_id']   = obj.game_id
    state['player_id'] = obj.player_id
    packet['cmd']      = 'play'

    print("YOU ARE PLAYER {}".format(state['player_id']))

    while True:

        move = input("ENTER MOVE\nR FOR ROCK\nP FOR PAPER\nS FOR SCISSORS\n:").lower()

        if move not in moves.keys():
            print("INVALID. TRY AGAIN")
            continue

        print("YOU PLAYED: {}".format(moves[move]))

        packet['move'] = state['move'] = move

        packet['game_id']   = state['game_id']
        packet['player_id'] = state['player_id']

        winner = wait_for_response(packet)

        print(winner['reason'])

        if winner['player'] == state['player_id']:
            print("YOU WIN")

        elif winner['player'] == -1:
            print("NO WINNER")

        else:
            print("YOU LOSE")

        ans = input("REMATCH [Y/N]?: ").lower()

        if ans == 'y':
            continue

        else:
            break
