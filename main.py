import sys
import os
import time
from PyQt5 import QtWidgets, uic, QtCore
from random import randint
import process, scheduler, enums, PCB
import threading

app = QtWidgets.QApplication(sys.argv)
window = uic.loadUi("mainwindow.ui")

numTemplates = 0
templateNames = []

allProcess = []
readyQueue = []
waitingQueue = []
# isCritical = (False, -1)

RR = scheduler.scheduler()

lock = threading.Lock()

def doSetup():
    getTemplates()
    makeCombos()


def getTemplates():#reads the name of all templates in templates folder
    global templateNames
    global numTemplates
    templateNames = os.listdir('templates')
    numTemplates = len(templateNames)


def makeCombos():#populates comboBox with choices
    global generationType_comboBox, processType_comboBox
    generationType_comboBox.addItem('Automatic')
    generationType_comboBox.addItem('Manual')

    for x in range(numTemplates):
        processType_comboBox.addItem(templateNames[x])


def startUpdate(): #attempt at making thread to constantly update loop processes
    loop = threading.Thread(target=updateClicked)
    loop.start()
    loop.join()


def updateClicked():#When clicked, would update number of processes in each state (doesnt work currently)
    global newProcess_label, runningProcess_label, waitingProcess_label, terminatedProcess_label, readyProcess_label, allProcess

    new = 0
    ready = 0
    running = 0
    waiting = 0
    terminated = 0

    for x in allProcess:
        if x.processType == enums.processTypes.READY:
            ready = ready + 1
        elif x.processType == enums.processTypes.NEW:
            new = new + 1
        elif x.processType == enums.processTypes.RUNNING:
            running = running + 1
        elif x.processType == enums.processTypes.WAITING:
            waiting = waiting + 1
        else:
            terminated = terminated + 1

        newProcess_label.setText('New: ' + str(new))
        readyProcess_label.setText('Ready: ' + str(ready))
        runningProcess_label.setText('Running: ' + str(running))
        waitingProcess_label.setText('Waiting: ' + str(waiting))
        terminatedProcess_label.setText('Terminated: ' + str(terminated))


def threadRun(p, quantum, threadName):
    timer = 0
    instruction = p.pcb.currentInstructions
    instructionCounter = instruction[1]

    pages = [-1,-1,-1,-1,-1]

    while timer < quantum:
        instructionCounter = instructionCounter - 1

        reference = randint(0,10)#make a random int, if it isnt in page list already, add new page in and take oldest page out
        if reference not in pages:
            pages.pop(4)
            pages.append(reference)


        if randint(0,100) < 5:#5% chance to get an IO interrupt
            time.sleep(1)
            print(threadName + " got an IO interrupt")

        if instructionCounter == 0: #if instruction finished
            if instruction[2] == p.criticalEnd:#if that was critical end
                lock.release()
                process.pcb.isCritical = False

            if instruction[2] == p.criticalStart:#if the start of critical section
                lock.acquire()
                p.pcb.isCritical = True

            if instruction[2] == len(p.processInstructions) - 1:#All instructions completed
                p.switchState(enums.processTypes.TERMINATED)
                return
            else:                       #Still more instructions
                instruction = p.processInstructions[instruction[2] + 1]  #go to next instruction

            if instruction[0] == enums.instructionTypes.IO: ##if its IO instruction, switch to waiting
                p.switchState(enums.processTypes.WAITING)  # switch to waiting
            elif instruction[0] == enums.instructionTypes.FORK:#make child process on next instruction
                temp = p
                temp.pcb.pid += +1
                temp.pcb.isCritical = False
                temp.switchState(enums.processTypes.WAITING)
                temp.processInstructions[instruction[2] + 1]
                p.pcb.hasChild.append(temp.pid)
                allProcess.append(temp)
                waitingQueue.append(temp)

                temp.send(temp.pcb.pid-1, "I have been born parent", temp.mid, allProcess)#sends message to parent indicating it was made
        timer = timer + 1


    p.switchState(enums.processTypes.WAITING)#if quantum time finishes and still more instrucitons, switch to waiting

    if p.pcb.isCritical: #releases lock if didnt finish before quantum was up
        lock.release()
        p.pcb.isCritical = False


def simulateAutomatic():
    global readyQueue, waitingQueue

    thread1 = threading.Thread()
    thread2 = threading.Thread()
    thread3 = threading.Thread()
    thread4 = threading.Thread()

    newQueue = []
    runningQueue = []
    runningQueue2 = []
    threads = [(0,thread1),(0,thread2),(0,thread3),(0,thread4)]

    numProcess = 10
    maxMem = 1024
    counter = 0
    terminated = 0

    while counter < numProcess:  # Makes all inital processes
        randTemplate = randint(0, numTemplates - 1)
        temp = process.process(templateNames[randTemplate])
        allProcess.append(temp)

        if maxMem - temp.memory > 0:
            readyQueue.append(temp)
            maxMem -= temp.memory
        else:
            newQueue.append(temp)

        counter += 1

    print("finished making initial processes")

    while True:
        for x in range(4):
            if len(readyQueue) >= 1:
                runningQueue.append(readyQueue.pop(0))

        readyQueue, waitingQueue, quantum = RR.roundRobin(readyQueue, waitingQueue)#gets quantum

        if len(readyQueue) >= 1:#Sees how many processes can run on memory, and makes appropriate amount of threads
            threads[0] = (1, thread1, runningQueue[0])
            thread1 = threading.Thread(target=threadRun, args=(runningQueue[0], quantum, "thread1"))
            thread1.start()
        if len(readyQueue) >= 2:
            threads[1] = (1, thread2, runningQueue[1])
            thread2 = threading.Thread(target=threadRun, args=(runningQueue[1], quantum, "thread2"))
            thread2.start()
        if len(readyQueue) >= 3:
            threads[2] = (1, thread3, runningQueue[2])
            thread3 = threading.Thread(target=threadRun, args=(runningQueue[2], quantum, "thread3"))
            thread3.start()
        if len(readyQueue) >= 4:
            threads[3] = (1, thread4, runningQueue[3])
            thread4 = threading.Thread(target=threadRun, args=(runningQueue[3], 15, "thread4"))
            thread4.start()


        if thread1.is_alive():#wait for all 4 processes to finish running
            thread1.join()
        if thread2.is_alive():
            thread2.join()
        if thread3.is_alive():
            thread3.join()
        if thread4.is_alive():
            thread4.join()

        #print("all done")

        ###Figure out what happened here###

        for x in range(4):
            if len(runningQueue) >= 1:
                temp = runningQueue.pop(0)
                maxMem += temp.memory #simulates freeing up memory

                if temp.processType == enums.processTypes.WAITING:
                    waitingQueue.append(temp)

                if temp.processType == enums.processTypes.TERMINATED:
                    for i in temp.pcb.hasChild: #Cascading Termination
                        for n in allProcess:
                            if i == n.pcb.pid:#goes through all processes and finds the id to terminate
                                n.switchState(enums.processTypes.TERMINATED)


        if len(newQueue) > 0:
            for p in newQueue:
                if maxMem - p.memory > 0:
                    temp = newQueue.pop(0)
                    temp.switchState(enums.processTypes.RUNNING)
                    readyQueue.append(temp)

        readyQueue, waitingQueue = RR.SJF(readyQueue, waitingQueue)

        startUpdate()

        done = 0
        for x in allProcess:
            if x.processType == enums.processTypes.TERMINATED:
                done += done

        break

        if done == len(allProcess):
            break


def startClicked():
    global generationType_comboBox
    if generationType_comboBox.currentText() == "Automatic":
        simulateAutomatic()


generationType_comboBox = window.findChild(QtWidgets.QComboBox, 'generationType_comboBox')
processType_comboBox = window.findChild(QtWidgets.QComboBox, 'processType_comboBox')

processNumber_spinBox = window.findChild(QtWidgets.QSpinBox, 'processNumber_spinBox')
numProcess_spinBox = window.findChild(QtWidgets.QSpinBox, 'numProcess_spinBox')
numCycles_spinBox = window.findChild(QtWidgets.QSpinBox, 'numCycles_spinBox')

pause_checkBox = window.findChild(QtWidgets.QCheckBox, 'pause_checkBox')

newProcess_label = window.findChild(QtWidgets.QLabel, 'newProcess_label')
readyProcess_label = window.findChild(QtWidgets.QLabel, 'readyProcess_label')
runningProcess_label = window.findChild(QtWidgets.QLabel, 'runningProcess_label')
waitingProcess_label = window.findChild(QtWidgets.QLabel, 'waitingProcess_label')
terminatedProcess_label = window.findChild(QtWidgets.QLabel, 'terminatedProcess_label')

start_pushButton = window.findChild(QtWidgets.QPushButton, 'start_pushButton')
start_pushButton.clicked.connect(startClicked)

statistics_pushButton = window.findChild(QtWidgets.QPushButton, 'statistics_pushButton')
statistics_pushButton.clicked.connect(startUpdate)

doSetup()

window.show()
app.exec()






