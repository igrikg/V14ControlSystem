import nidaqmx
#import loguru
import threading
import time
from nidaqmx.constants import AcquisitionType, Level, Signal, Edge, CountDirection, \
    ExportAction, TriggerType, LineGrouping



SOURCE_LIST = ["PFI39","PFI35","PFI31","PFI27","PFI23","PFI19"]
"""
Измерение за определенное время
(в соответствии с вводом в секундах).
Счетчики 1-5 установлены таким образом
Что вместе перестают считать,
если условие прекращения (время истекло)
было выполнено.
Счетчик 7 формирует последовательность импульсов (1 кГц).
Счетчик 0 считает импульсы от счетчика 7 и, таким образом, подсчитывает время измерения. По истечении отведенного времени сигнал на ВЫХОДЕ счетчика 0 меняется с высокого на низкий, вызывая остановку счетчиков 1-5.
Во время счета загорается красный светодиод.
Подсчет можно остановить досрочно, нажав кнопку «Отмена».
(отмена = 1).
"""
class NiPci6602DAQ():
    """ Class to working with NIPSI6602

    Usage:
        device='Dev1' Name in system

    """
    WORK = False
    def __init__(self, device:str="Dev1"):
        self.__device = device
        self.generatorTask = nidaqmx.Task()
        self.timeDownCounterTask = nidaqmx.Task()
        self.inputTimeCounterTasksList = [nidaqmx.Task() for _ in range(6)]
        self.__startGenerate1kHz()
        self.__data = []

    @property
    def data(self):
        return(self.__data)
    def __del__(self):
        self.generatorTask.stop()
        self.generatorTask.close()
        self.timeDownCounterTask.close()
        list(map(lambda x: x.stop(), self.inputTimeCounterTasksList))
        list(map(lambda x: x.close(), self.inputTimeCounterTasksList))

    def __startGenerate1kHz(self):
        """create generator 1kHz using counter 7 and output PFI8"""
        counterGenerate = self.generatorTask.co_channels.add_co_pulse_chan_freq(
                                    "{:}/ctr7".format(self.__device), units=nidaqmx.constants.FrequencyUnits.HZ,
                                    idle_state=nidaqmx.constants.Level.LOW, initial_delay=0.0,
                                    freq=1000.0, duty_cycle=0.5)
        counterGenerate.co_pulse_term = "/{:}/PFI8".format(self.__device)
        self.generatorTask.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
        self.generatorTask.start()

    def __makeCounterCountAndSource(self,count:int=0,source:str="PFI8"):
        """
        Create counter for organasing time meas or counts meas
        count:int=0 count or time what must be use
        source:str="PFI8" souse where need calculate
        Using counter CTH6
        """
        counterCountAndSource = self.timeDownCounterTask.ci_channels.add_ci_count_edges_chan(
                                                            "{:}/ctr6".format(self.__device), edge=Edge.RISING,
                                                            initial_count=count-1,
                                                            count_direction=CountDirection.COUNT_DOWN)
        counterCountAndSource.ci_count_edges_term = "/{:}/{:}".format(self.__device, source)
        # export sygnal to PFI36 for use triger in other tasks
        self.timeDownCounterTask.export_signals.export_signal(Signal.COUNTER_OUTPUT_EVENT, "/{:}/PFI36".format(self.__device))
        self.timeDownCounterTask.export_signals.ctr_out_event_output_behavior = ExportAction.TOGGLE
        self.timeDownCounterTask.export_signals.ctr_out_event_toggle_idle_state = Level.HIGH


        trigerStop = self.timeDownCounterTask.triggers.pause_trigger
        trigerStop.trig_type = TriggerType.DIGITAL_LEVEL
        trigerStop.dig_lvl_src = "/{:}/PFI36".format(self.__device)
        trigerStop.dig_lvl_when = Level.LOW

    def __makeInputTasks(self, counter:int=0, source:str=None):
        """
        create a task
        :param counter:
        :param source:
        """
        counterTask = self.inputTimeCounterTasksList[counter].ci_channels.add_ci_count_edges_chan(
            "{:}/ctr{:}".format(self.__device,counter), edge=Edge.RISING,
            initial_count=0,
            count_direction=CountDirection.COUNT_UP)
        if source is not None:
            counterTask.ci_count_edges_term = "/{:}/{:}".format(self.__device, source)

        trigerStop = self.inputTimeCounterTasksList[counter].triggers.pause_trigger
        trigerStop.trig_type = TriggerType.DIGITAL_LEVEL
        trigerStop.dig_lvl_src = "/{:}/PFI36".format(self.__device)
        trigerStop.dig_lvl_when = Level.LOW

    def __makeCounterForInputs(self):
        for i,_ in enumerate(self.inputTimeCounterTasksList):
            if i==0: # 0: use for meas time
                self.__makeInputTasks(i,"PFI8")
            else:
                self.__makeInputTasks(i)

    def __startCounting(self):
        list(map(lambda task: task.start(), self.inputTimeCounterTasksList))
        self.WORK =True
        self.__data = []
        self.timeDownCounterTask.start()

    def __stopCounting(self):
        self.timeDownCounterTask.stop()
        list(map(lambda task: task.stop(), self.inputTimeCounterTasksList))
        self.WORK = False

    def __readData(self):
        self.__data = list(map(lambda x: x.read(), self.inputTimeCounterTasksList))
        self.__data.append(self.timeDownCounterTask.read())
        if self.__data[-1] == 4294967295:# end measurment
            self.__data[-1] = 0
            self.WORK=False

    def __readDataWait(self):
        while self.WORK:
            self.__readData()

    def readDataNow(self):
        self.__readData()

    def readData(self):
        self.__readDataWait()

    def Stop(self):
        self.__stopCounting()

    def startMeasurmentForTimeMs(self, timeValue:int):
        self.__stopCounting()
        self.__makeCounterCountAndSource(count=timeValue)
        self.__makeCounterForInputs()
        self.__startCounting()

    def startMeasurmentForCounts(self, countValue:int, inputChannel:int):
        self.__stopCounting()
        self.__makeCounterCountAndSource(count=countValue,source=SOURCE_LIST[inputChannel])
        self.__makeCounterForInputs()
        self.__startCounting()




class NiPci6602DIO():
    """ Class to working with NIPSI6602 Input output

    Usage:
        device='Dev1' Name in system
        set 1-4 use as Input
        set 5-8 use as Output
        expoStopInputOconfig: use input for stop exposition It is not work eat

        Input
        [1,2,3,4] number channel
        Output
        [5,6,7,8] number channel
    """
    def __init__(self, device:str="Dev1"):
        self.__device = device


        self.__inputTask = nidaqmx.Task()
        self.__outputTask = nidaqmx.Task()
        self.__dataInput = [False,False,False,False]
        self.__dataOutput = [False,False,False,False]
        self.__init_input()
        self.__init_output()

    @property
    def dataInput(self):
        self.__readInput()
        return self.__dataInput

    @property
    def dataOutput(self):
        return self.__dataOutput

    @dataOutput.setter
    def dataOutput(self,value:list):
        if len(value)==4:
            self.__dataOutput = value
        self.__writeOutput()

    def __init_input(self):
        self.__inputTask.di_channels.add_di_chan(
            "{:}/port0/line0:3".format(self.__device), line_grouping=LineGrouping.CHAN_PER_LINE)
        self.__inputTask.start()

    def __init_output(self):
        self.__outputTask.do_channels.add_do_chan(
            "{:}/port0/line4:7".format(self.__device), line_grouping=LineGrouping.CHAN_PER_LINE)
        self.__outputTask.start()

    def __readInput(self):
        self.__dataInput=self.__inputTask.read()

    def __writeOutput(self):
        self.__outputTask.write(self.__dataOutput)

    def writeAll(self,value:list):
        """write all """
        self.__dataOutput=value
        self.__writeOutput()
    def writeOneOut(self,channel:int,value:bool):
        """write value to channel
            channel can be from 1 to 4
         """
        self.__dataOutput[channel-1]=value
        self.__writeOutput()
    def write(self):
        """write data from self.dataInput"""
        self.__writeOutput()

    def readData(self):
        self.__readInput()

    def __del__(self):
        self.__inputTask.stop()
        self.__outputTask.stop()
        self.__inputTask.close()
        self.__outputTask.close()




if __name__ == "__main__":
    # a = NiPci6602DAQ('Dev2')
    # a.startMeasurmentForTimeMs(15000)
    #a.startMeasurmentForCounts(3000,5)
    b = NiPci6602DIO()
    print(b.dataInput)
    b.dataOutput=[True, True, False, False]
    print(b.dataInput)
    b.dataOutput = [False, False, False, False]
    print(b.dataInput)

    b.writeOneOut(2, True)
    #b.readData()
    print(b.dataInput)

    b.dataOutput = [False, False, False, False]
    print(b.dataInput)
    # time.sleep(2)
    # a.readData()
    #
    # print(a.data)
    # print(a.WORK)
    # a.Stop()


