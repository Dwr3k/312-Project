from enum import Enum


class processTypes(Enum):
    NEW = 1
    RUNNING = 2
    WAITING = 3
    READY = 4
    TERMINATED = 5


class instructionTypes(Enum):
    CALCULATE = 1
    IO = 2
    FORK = 3
