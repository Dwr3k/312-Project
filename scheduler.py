import process, PCB
from math import floor


class scheduler:
    def roundRobin(self, ready, waiting):
        total = 0
        for x in ready:
            for y in x.processInstructions:
                total = total + y[1]

            total = floor(total / len(x.processInstructions))

        if total < 5:
            total = 12

        #print("quantum is: " + str(total))

        return ready, waiting, total

