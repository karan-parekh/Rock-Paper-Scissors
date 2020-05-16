import enum
import time
import zmq

context = zmq.Context()

print("Connecting to server port: 5555")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


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

        print("YOU CAN PRESS Q TO QUIT ANYTIME")

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
                print("GAME IS FULL.\nTRY ANOTHER ID OR CREATE A NEW GAME")
                continue

            if not p.game_id:
                print("NO GAME WITH ID: {}".format(state['game_id']))
                print("TRY ANOTHER ID OR CREATE A NEW GAME")
                continue

            return p

        if cmd == 'q':
            break

        print("TRY AGAIN")


def wait_for_response(p):
    print("WAITING FOR RESPONSE")

    while True:

        socket.send_pyobj(p)

        res = socket.recv_pyobj()

        if not res.result:
            time.sleep(1)
            continue

        return res.result


if __name__ == '__main__':

    moves = {
        'r': Move.ROCK,
        'p': Move.PAPER,
        's': Move.SCISSORS,
        'q': None
    }

    obj = main()

    if not obj:
        exit()

    state['game_id']   = obj.game_id
    state['player_id'] = obj.player_id
    packet['cmd']      = 'play'

    print("YOU ARE PLAYER {}".format(state['player_id']))

    while True:

        move = input("ENTER MOVE\nR FOR ROCK\nP FOR PAPER\nS FOR SCISSORS\n:").lower()

        if move not in moves.keys():
            print("INVALID. TRY AGAIN")
            continue

        print("YOU PLAYED: {}".format(moves[move].name))

        packet['move'] = state['move'] = moves[move]

        packet['game_id']   = state['game_id']
        packet['player_id'] = state['player_id']

        response = wait_for_response(packet)

        print(response['reason'])

        if response['winner'] == state['player_id']:
            print("YOU WIN")

        elif response['winner'] == -1:
            print("NO WINNER")

        else:
            print("YOU LOSE")

        ans = input("REMATCH [Y/N]?: ").lower()

        if ans == 'y':
            packet['cmd'] = 'check'
            socket.send_pyobj(packet)

            if not socket.recv_pyobj().game_full:
                print("OPPONENT LEFT\nYOU CAN WAIT OR PRESS Q TO QUIT")

            continue

        else:
            packet['cmd'] = 'leave'
            socket.send_pyobj(packet)
            print("YOU LEFT THE GAME")
            break
