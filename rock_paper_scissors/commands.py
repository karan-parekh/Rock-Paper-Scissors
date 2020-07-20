from enum import Enum


class Command(Enum):

    CREATE = 1  # , "c"
    JOIN   = 2  # , "j"
    PLAY   = 3  # , None
    LEAVE  = 4  # , "q"
    CHECK  = 5  # , None
    STOP   = 6  # , None

    def __new__(cls, value, literal):

        member = object.__new__(cls)

        member._value_  = value
        member.literal = literal

        return member
