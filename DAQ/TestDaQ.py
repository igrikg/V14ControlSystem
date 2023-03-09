from PyDAQmx.DAQmxFunctions import *
from PyDAQmx.DAQmxConstants import *
import numpy


class ContinuousPulseTrainGeneration():
    """ Class to create a continuous pulse train on a counter

    """

    def __init__(self):
        taskHandle = TaskHandle(0)
        taskHandle2 = TaskHandle(0)
        DAQmxCreateTask("", byref(taskHandle))
        DAQmxCreateTask("", byref(taskHandle2))
        DAQmxCreateCOPulseChanFreq(taskHandle, "Dev1/ctr7", "", DAQmx_Val_Hz, DAQmx_Val_Low, 0.0, 1000, 0.5)
        DAQmxCfgImplicitTiming(taskHandle, DAQmx_Val_ContSamps, 1000)
        DAQmxSetCOPulseTerm(taskHandle, "Dev1/ctr7", "/Dev1/PFI8")


        DAQmxCreateCICountEdgesChan(taskHandle2, "Dev1/ctr0", "", DAQmx_Val_Rising, 10000, DAQmx_Val_CountDown)
        DAQmxSetCICountEdgesTerm(taskHandle2, "Dev1/ctr0", "/Dev1/PFI8")

        self.taskHandle = taskHandle
        self.taskHandle2 = taskHandle2

    def start(self):

        DAQmxStartTask(self.taskHandle)
        DAQmxStartTask(self.taskHandle2)

    def stop(self):
        DAQmxStopTask(self.taskHandle)
        DAQmxStopTask(self.taskHandle2)

    def clear(self):
        DAQmxClearTask(self.taskHandle)
        DAQmxClearTask(self.taskHandle2)

    def read(self):
        read = uInt32()
        data = numpy.zeros((1000,), dtype=numpy.float64)
        DAQmxReadCounterScalarU32(self.taskHandle2,10.0,byref(read),None)
        #DAQmxReadCounterF64(self.taskHandle2, 1000, 10.0, data, 1000, byref(read), None)
        return read.value


class TryContinuousPulseTrainGeneration():
    """ Class to create a continuous pulse train on a counter
    """

    def __init__(self):
        taskHandle = TaskHandle(0)
        DAQmxCreateTask("", byref(taskHandle))
        DAQmxCreateCIFreqChan(taskHandle, "Dev1/ctr0", "", 200, 1000000, DAQmx_Val_Hz, DAQmx_Val_Rising,
                              DAQmx_Val_LowFreq1Ctr, 0.001, 10, "")
        DAQmxSetCIFreqTerm(taskHandle, "Dev1/ctr0", "/Dev1/PFI0")
        DAQmxCfgSampClkTiming(taskHandle, "/Dev1/PFI1", 100.0, DAQmx_Val_Rising, DAQmx_Val_ContSamps, 1000)
        DAQmxSetArmStartTrigType(taskHandle, DAQmx_Val_DigEdge)
        DAQmxSetDigEdgeArmStartTrigSrc(taskHandle, "/Dev1/PFI1")
        DAQmxSetDigEdgeArmStartTrigEdge(taskHandle, DAQmx_Val_Rising)
        self.taskHandle = taskHandle

    def start(self):
        DAQmxStartTask(self.taskHandle)

    def stop(self):
        DAQmxStopTask(self.taskHandle)

    def clear(self):
        DAQmxClearTask(self.taskHandle)

    def read(self):
        read = int32()
        data = numpy.zeros((1000,), dtype=numpy.float64)
        DAQmxReadCounterF64(self.taskHandle, 1000, 10.0, data, 1000, byref(read), 0)
        return read.value


if __name__ == "__main__":
    pulse_gene1 = ContinuousPulseTrainGeneration()
    pulse_gene1.start()
    while (1):
        print(pulse_gene1.read())
        a = input("Generating pulse train. Press Enter to interrupt\n")
        if a == '123': break

    pulse_gene1.stop()
    pulse_gene1.clear()
