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
isCritical = (False, -1)

RR = scheduler.scheduler()

def doSetup():
    getTemplates()
    makeCombos()


def getTemplates():
    global templateNames
    global numTemplates
    templateNames = os.listdir('templates')
    numTemplates = len(templateNames)


def makeCombos():
    global generationType_comboBox, processType_comboBox
    generationType_comboBox.addItem('Automatic')
    generationType_comboBox.addItem('Manual')

    for x in range(numTemplates):
        processType_comboBox.addItem(templateNames[x])


def startUpdate():
    loop = threading.Thread(target=updateClicked())
    loop.start()


def updateClicked():
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


def runProcess(p, quantum):
    global readyQueue, waitingQueue, RR, isCritical

    timer = 0
    instruction = p.pcb.currentInstructions
    instructionCounter = instruction[1]

    while timer < quantum:
        instructionCounter = instructionCounter - 1

        if instructionCounter == 0:
            if instruction[2] == p.criticalEnd:
                isCritical = False, -1
                p.pcb.isCritical = False


            if instruction[2] == len(p.processInstructions) - 1: #if last instruction
                p.switchState(enums.processTypes.TERMINATED) #Terminate Process
                RR.roundRobin(readyQueue, waitingQueue)
            else:
                instruction = p.processInstructions[instruction[2] + 1] #switch intsturciton

                if instruction[2] == p.criticalStart:
                    isCritical = (True, p.pcb.pid)
                    p.pcb.isCritical = True

                if instruction[0] == enums.instructionTypes.IO:
                    p.switchState(enums.processTypes.WAITING)#switch ti waiting
                    RR.roundRobin(readyQueue, waitingQueue)

        timer = timer + 1


def simulateAutomatic():
    global numTemplates, waitingQueue, readyQueue, isCritical, RR, allProcess, processNumber_spinBox
    numProcess = randint(0, 10)

    waitingQueue = []
    readyQueue = []

    counter = 0
    while counter < numProcess:
        randTemplate = randint(0, numTemplates - 1)
        temp = process.process(templateNames[randTemplate])
        allProcess.append(temp)
        temp.switchState(enums.processTypes.READY)

        readyQueue.append(temp)
        readyQueue, waitingQueue, quantum = RR.roundRobin(readyQueue, waitingQueue)

        if not isCritical[0] or (isCritical[0] and isCritical[1] == readyQueue[0].pcb.pid):
            readyQueue[0].switchState(enums.processTypes.RUNNING)
            runProcess(readyQueue[0], quantum)
        else:
            temp = readyQueue[0]
            temp.switchState(enums.processTypes.WAITING)
            waitingQueue.append(temp)
            del readyQueue[0]

        readyQueue, waitingQueue, quantum = RR.roundRobin(readyQueue, waitingQueue)

        counter = counter + 1

        #updateClicked()

    #print(allProcess)


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

doSetup()

startUpdate()

window.show()
app.exec()







