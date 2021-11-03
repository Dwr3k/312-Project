import enums
import PCB
from random import randint


class process:
    def __init__(self, template):
        path = 'templates/' + template
        instructions = []

        self.processInstructions = []
        self.criticalStart = 0
        self.criticalEnd = 0
        self.processType = enums.processTypes.NEW
        self.currentInstruction = ()

        with open(path, 'r') as file:
            for line in file:
                for word in line.split():
                    instructions.append(word)

        #print('READING ' + template)

        x = 0
        totalCycle = 0
        while x != len(instructions) - 3:
            if instructions[x] == 'CALCULATE':
                instructType = enums.instructionTypes.CALCULATE
            elif instructions[x] == 'I/O':
                instructType = enums.instructionTypes.IO
            else:
                instructType = enums.instructionTypes.FORK

            cycleLength = randint(int(instructions[x+1]), int(instructions[x+2]))
            self.processInstructions.append((instructType, cycleLength, x))

            totalCycle = totalCycle + int(instructions[x+1]) + int(instructions[x+2])

            x = x+3

        self.criticalStart = randint(0, len(self.processInstructions) - 1)
        self.criticalEnd = randint(self.criticalStart + 1, len(self.processInstructions))
        self.currentInstruction = self.processInstructions[0]
        self.pcb = PCB.pcb(self, self.currentInstruction)

    def switchState(self, newState):
        self.processType = newState
