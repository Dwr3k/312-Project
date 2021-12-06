import process, enums
from random import randint


class pcb:
    def __init__(self, proc, current):
        self.pid = randint(0, 10000)
        self.processType = proc.processType
        self.currentInstructions = current
        self.isCritical = False
        self.hasChild = []
