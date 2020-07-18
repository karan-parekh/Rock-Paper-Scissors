from enum import Enum


class Command(Enum):

    CREATE = 1
    JOIN   = 2
    PLAY   = 3
    LEAVE  = 4
    CHECK  = 5
    STOP   = 6
