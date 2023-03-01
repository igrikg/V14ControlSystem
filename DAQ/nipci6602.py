import nidaqmx
from nidaqmx.constants import AcquisitionType, Level, Signal,Edge,CountDirection,ExportAction, TriggerType
import time

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
class NiPci6602():
    """ Class to working with NIPSI6602

    Usage:
        device='Dev1' Name in system

    """
    WORK = False
    def __init__(self, device:str="Dev1"):
        self.device = device
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
        list(map(lambda x: x.close(), self.inputTimeCounterTasksList))

    def __startGenerate1kHz(self):
        """create generator 1kHz using counter 7 and output PFI8"""
        counterGenerate = self.generatorTask.co_channels.add_co_pulse_chan_freq(
                                    "{:}/ctr7".format(self.device), units=nidaqmx.constants.FrequencyUnits.HZ,
                                    idle_state=nidaqmx.constants.Level.LOW, initial_delay=0.0,
                                    freq=1000.0, duty_cycle=0.5)
        counterGenerate.co_pulse_term = "/{:}/PFI8".format(self.device)
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
                                                            "{:}/ctr6".format(self.device), edge=Edge.RISING,
                                                            initial_count=count-1,
                                                            count_direction=CountDirection.COUNT_DOWN)
        counterCountAndSource.ci_count_edges_term = "/{:}/{:}".format(self.device, source)
        # export sygnal to PFI36 for use triger in other tasks
        self.timeDownCounterTask.export_signals.export_signal(Signal.COUNTER_OUTPUT_EVENT, "/Dev1/PFI36")
        self.timeDownCounterTask.export_signals.ctr_out_event_output_behavior = ExportAction.TOGGLE
        self.timeDownCounterTask.export_signals.ctr_out_event_toggle_idle_state = Level.HIGH

        trigerStop = self.timeDownCounterTask.triggers.pause_trigger
        trigerStop.trig_type = TriggerType.DIGITAL_LEVEL
        trigerStop.dig_lvl_src = "/Dev1/PFI36"
        trigerStop.dig_lvl_when = Level.LOW

    def __makeInputTasks(self, counter:int=0, source:str=None):
        """
        create a task
        :param counter:
        :param source:
        """
        counterTask = self.inputTimeCounterTasksList[counter].ci_channels.add_ci_count_edges_chan(
            "{:}/ctr{:}".format(self.device,counter), edge=Edge.RISING,
            initial_count=0,
            count_direction=CountDirection.COUNT_UP)
        if source is not None:
            counterTask.ci_count_edges_term = "/{:}/{:}".format(self.device, source)

        trigerStop = self.inputTimeCounterTasksList[counter].triggers.pause_trigger
        trigerStop.trig_type = TriggerType.DIGITAL_LEVEL
        trigerStop.dig_lvl_src = "/Dev1/PFI36"
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
        #self.__data =[x for x in self.inputTimeCounterTasksList]

        self.__data.append(self.timeDownCounterTask.read())
        if self.__data[-1] == 4294967295:# end measurment
            self.__data[-1] = 0
            self.WORK=False
    def __readDataWait(self):
        while self.WORK:
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


if __name__ == "__main__":
    a = NiPci6602()
    #a.startMeasurmentForTimeMs(15000)
    #a.startMeasurmentForCounts(3000,5)
    time.sleep(2)
    a.readData()

    print(a.data)
    print(a.WORK)
    a.Stop()


