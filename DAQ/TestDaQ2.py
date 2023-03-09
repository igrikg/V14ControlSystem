import nidaqmx
from nidaqmx.constants import AcquisitionType, Level, Signal,Edge,CountDirection,ExportAction, TriggerType
import time

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
    def __init__(self, device:str="Dev1"):
        self.device = device
        self.generatorTask = nidaqmx.Task()
        self.timeDownCounterTask = nidaqmx.Task()
        self.inputOneCounterTask = nidaqmx.Task()
        self.inputTwoCounterTask = nidaqmx.Task()
        self.inputThreeCounterTask = nidaqmx.Task()
        self.inputFourCounterTask = nidaqmx.Task()
        self.inputFiveCounterTask = nidaqmx.Task()
        self.timeMeasInMsTask = nidaqmx.Task()
        self.__startGenerate1kHz()

    def __del__(self):
        self.generatorTask.stop()
        self.generatorTask.close()
        self.timeDownCounterTask.close()
        self.inputOneCounterTask.close()
        self.inputTwoCounterTask.close()
        self.inputThreeCounterTask.close()
        self.inputFourCounterTask.close()
        self.inputFiveCounterTask.close()
        self.timeMeasInMsTask.close()

    def __startGenerate1kHz(self):
        """create generator 1kHz using counter 7 and output PFI8"""
        counterGenerate = self.generatorTask.co_channels.add_co_pulse_chan_freq(
                                    "{:1}/ctr7".format(self.device), units=nidaqmx.constants.FrequencyUnits.HZ,
                                    idle_state=nidaqmx.constants.Level.LOW, initial_delay=0.0,
                                    freq=1000.0, duty_cycle=0.5)
        counterGenerate.co_pulse_term = "/{:1}/PFI8".format(self.device)
        self.generatorTask.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)

    def __makeCounterCountAndSource(self,count:int=0,source:str="PFI8"):
        counterCountAndSource = self.timeDownCounterTask.ci_channels.add_ci_count_edges_chan(
                                                            "{:1}/ctr0".format(self.device), edge=Edge.RISING,
                                                            initial_count=count,
                                                            count_direction=CountDirection.COUNT_DOWN)
        counterCountAndSource.ci_count_edges_term = "/{:1}/{:2}".format(self.device, source)
        # export sygnal to PFI36 for use triger in other tasks
        self.timeDownCounterTask.export_signals.export_signal(Signal.COUNTER_OUTPUT_EVENT, "/Dev1/PFI36")
        self.timeDownCounterTask.export_signals.ctr_out_event_output_behavior = ExportAction.TOGGLE
        self.timeDownCounterTask.export_signals.ctr_out_event_toggle_idle_state = Level.HIGH

        trigerStop = task.triggers.pause_trigger
        trigerStop.trig_type = TriggerType.DIGITAL_LEVEL
        trigerStop.dig_lvl_src = "/Dev1/PFI36"
        trigerStop.dig_lvl_when = Level.LOW
    def __makeCounterForInputs(self):
    #def __startTaskForStopAfterMs(self,timeInMs):







task=nidaqmx.Task()
task2=nidaqmx.Task()
task3=nidaqmx.Task()
#generator




# time counter
counter1=task.ci_channels.add_ci_count_edges_chan("Dev1/ctr0", edge=Edge.RISING,
            initial_count=2000, count_direction=CountDirection.COUNT_DOWN)
counter1.ci_count_edges_term = "/Dev1/PFI8"
task.export_signals.export_signal(Signal.COUNTER_OUTPUT_EVENT,"/Dev1/PFI36")
task.export_signals.ctr_out_event_output_behavior = ExportAction.TOGGLE
task.export_signals.ctr_out_event_toggle_idle_state = Level.HIGH
triger1 = task.triggers.pause_trigger
triger1.trig_type = TriggerType.DIGITAL_LEVEL
triger1.dig_lvl_src = "/Dev1/PFI36"
triger1.dig_lvl_when = Level.LOW






#meas data
counter2=task3.ci_channels.add_ci_count_edges_chan("Dev1/ctr1", edge=Edge.RISING,
            initial_count=0, count_direction=CountDirection.COUNT_UP)
counter2.ci_count_edges_term = "/Dev1/PFI8"
counter1=task3.ci_channels.add_ci_count_edges_chan("Dev1/ctr2", edge=Edge.RISING,
            initial_count=0, count_direction=CountDirection.COUNT_UP)
counter1.ci_count_edges_term = "/Dev1/PFI8"
triger2 = task3.triggers.pause_trigger
triger2.trig_type = TriggerType.DIGITAL_LEVEL
triger2.dig_lvl_src = "/Dev1/PFI36"
triger2.dig_lvl_when = Level.LOW
#___________________________________________________









#___________________________________________________



task2.start()
task.start()
task3.start()
time.sleep(5)
print('1 Channel 1 Sample Read: ')
data = task.read()
print(data)
data = task3.read()
print(data)

time.sleep(5)
task.stop()
task2.stop()
task3.stop()

task.close()
task2.close()
task3.close()



