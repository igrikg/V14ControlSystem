from PyDAQmx.DAQmxFunctions import *
from PyDAQmx.DAQmxConstants import *

class NiPci6602():
    """ Class to create a

    Usage:
    """
    def __init__(self, counter="Dev1/ctr0", reset=False):
        pass

from PyDAQmx import Task
import PyDAQmx
import numpy as np


data = np.array([0,1,1,0,1,0,1,0], dtype=np.uint8)

task = Task()
task.CreateDOChan("/Dev1/port0/line0:7","",PyDAQmx.DAQmx_Val_ChanForAllLines)
task.StartTask()
task.WriteDigitalLines(1,1,10.0,PyDAQmx.DAQmx_Val_GroupByChannel,data,None,None)
task.StopTask()