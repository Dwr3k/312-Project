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

    def SJF(self, ready, waiting):
        processTimes = []
        counter = 0
        for x in waiting:
            time = 0
            for i in x.processInstructions:
                time = time + i[1]
            processTimes.append((counter, time))
            counter = counter + 1

        processTimes.sort(key=lambda tup: tup[1])

        newWaiting = []
        for x in processTimes:
            newWaiting.append(waiting[x[0]])

        return ready, newWaiting
