from enum import Enum, auto


class Command(Enum):

    CREATE = auto()  # , "c"
    JOIN   = auto()  # , "j"
    QUIT   = auto()  # , "q"
    PLAY   = auto()  # , None
    LEAVE  = auto()  # , None
    CHECK  = auto()  # , None
    STOP   = auto()  # , None

    # def __new__(cls, value, literal):
    #
    #     member = object.__new__(cls)
    #
    #     member._value_ = value
    #     member.literal = literal
    #
    #     return member
