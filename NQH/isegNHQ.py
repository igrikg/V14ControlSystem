
import serial
import time


class IsegNHQ:
    def __init__(self, resource_name):
        self.instr = serial.Serial(resource_name, 9600, timeout=2)

    def __del__(self):
        self.instr.close()

    def send_command(self, command):
        command += '\r\n'
        for _ in range(3):# try repeat 3 times
            for i in command: self.instr.write(i.encode())
            response1 = self.instr.readline().decode().strip()
            if response1 == command: break
        response2 = self.instr.readline().decode().strip()

        return response2
    def get_identifier(self):
        response = self.send_command('#')
        responseSplit = response.split(';')
        if len(responseSplit) == 4:
            SerialNumber, SoftwareRelease, VoutMax, IoutMax = responseSplit
            response = {'SerialNumber' : SerialNumber,
             'SoftwareRelease' : SoftwareRelease,
             'VoutMax': VoutMax,
             'IoutMax' : IoutMax[:-2]}
        else:
            response = {'SerialNumber': '',
                        'SoftwareRelease': '',
                        'VoutMax': '',
                        'IoutMax': ''}
        return response
    def __getfloatvalue(self,command):
        response = self.send_command(command)
        try:
            response = float(response)
        except ValueError:
            response = 0.0
        return response
    def __getintvalue(self,command):
        response = self.send_command(command)
        try:
            response = int(response)
        except ValueError:
            response = 0
        return response
    def get_delay_time(self):
        return self.__getintvalue('W')
    def set_delay_time(self,value:int):
        response = self.send_command('W={:03}'.format(value))

    def get_meas_voltage(self,channel):
        return self.__getfloatvalue('U'+str(channel))
    def get_meas_current(self,channel):
        return self.__getfloatvalue('I'+str(channel))
    def get_limit_voltage(self,channel):
        return self.__getintvalue('M'+str(channel))
    def get_limit_current(self,channel):
        return self.__getintvalue('N'+str(channel))
    def get_set_voltage(self,channel):
        return self.__getfloatvalue('D'+str(channel))
    def get_ramp_speed(self,channel):
        return self.__getintvalue('V'+str(channel))
    def get_current_trip(self,channel):
        return self.__getfloatvalue('L'+str(channel))
    def get_auto_start(self,channel):
        return self.__getintvalue('A'+str(channel))==8

    def get_status_module(self, channel):
        return self.__getintvalue('T' + str(channel))

    def get_status(self, channel):
        return self.send_command('S' + str(channel))

    def set_ramp_speed(self, channel:int, value: int):
       self.send_command('V{channel}={value:03}'.format(channel=channel,value=value))

    def set_voltage(self, channel:int, value: float):
        self.send_command('D{channel}={value:06.1f}'.format(channel=channel,value=value))

    def set_current_trip(self, channel:int, value: int):
        self.send_command('L{channel}={value:04}'.format(channel=channel,value=value))

    def set_auto_start_int(self, channel:int, value: int):
        self.send_command('A{channel}={value:03}'.format(channel=channel,value=value))

    def set_auto_start_int(self, channel : int,
                           enableAutoStart : bool,
                           saveCurrentTrip : bool,
                           saveSetVoltage : bool,
                           saveRampSpeed : bool):
        self.set_auto_start_int(channel, enableAutoStart * 8 + saveCurrentTrip * 4 + saveSetVoltage * 2 + saveRampSpeed)

    def set_start_ramp(self,channel:int):
        self.send_command('G{channel}'.format(channel=channel))

if __name__=="__main__":
    a=IsegNHQ("COM7")
    print(a.get_identifier())
    print(a.get_meas_voltage(1))
    #print(a.get_auto_start(1))
    #print(a.get_status_module(1))
    #print(a.get_status(1))
    print(a.get_current_trip(1))
    print(a.get_limit_current(1))
    print(a.get_limit_voltage(1))
    print(a.get_meas_current(1))
    print(a.get_ramp_speed(1))
    print(a.get_set_voltage(1))


