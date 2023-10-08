import pyvisa
import time

class PSC44M:
    def __init__(self, address):
        self.address = address
        self.FSU = 1
        self.FSI = 1
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(self.address)
    def __repeatquarty(self,text):
        if '?' in text:
            for _ in range(3):
                result=self.inst.query(text)[:-2]
                if result!='NOP': break
                time.sleep(0.5)
        else:
             result = self.inst.query(text)[:-2]
        time.sleep(0.5)
        return result

    def identify(self):
        return self.__repeatquarty('ID?')
    def get_errors(self):
        result = self.__repeatquarty('ERR?')[:4]
        switcher = {
            'ER00': 'Not in error',
            'ER01': 'Command-systax error',
            'ER02': 'Channel-number error (non existant number)',
            'ER03': 'Numerical-value error',
            'ER04': 'Direct-command issued without FS set before (by FS command)',
        }
        return switcher.get(result)

    def get_set_voltage_current(self):
        result = self.__repeatquarty('OR?')
        if len(result) != 9: result = self.__repeatquarty('OR?')
        if len(result) == 9:
            result=tuple(map(lambda x: int(x),result.split()))
        else:
            result=(0,0)
        return round(result[0]/4095*self.FSU,1), round(result[1]/4095*self.FSI,1)
    def get_set_voltage_current_in_step(self):
        result = self.__repeatquarty('OR?')
        if len(result) == 9:
            result = tuple(map(lambda x: int(x), result.split()))
        else:
            result = (0, 0)
        return result

    def get_voltage(self):
        for _ in range(3):
            res = self.__repeatquarty('MA?')
            if res[:2] == 'MA': break
        res = int(res.split()[1])/4095*self.FSU
        return res

    def get_current(self):
        for _ in range(3):
            res = self.__repeatquarty('MB?')
            if res[:2] == 'MB': break
        res = int(res.split()[1])/4095*self.FSU
        return res
    def get_voltage_in_step(self):
        for _ in range(3):
            res = self.__repeatquarty('MA?')
            if res[:2] == 'MA': break
        res = int(res.split()[1])
        return res

    def get_current_in_step(self):
        for _ in range(3):
            res = self.__repeatquarty('MB?')
            if res[:2] == 'MB': break
        res = int(res.split()[1])
        return res
    def set_voltage_in_step(self,U:int):
        return self.__repeatquarty('SA{:04}'.format(U))
    def set_current_in_step(self,I:int):
        return self.__repeatquarty('SB{:04}'.format(I))
    def set_limit(self,U:int,I:int):
        self.FSU = U
        self.FSI = I
        return self.__repeatquarty('FA{0:02},FB{1:02}'.format(U,I))

    def set_voltage(self,U:float):
        return self.__repeatquarty('U{:06.2f}'.format(U))
    def set_current(self,I:float):
        return self.__repeatquarty('I{:06.2f}'.format(I))
    def set_RequestServiceFun_ON(self):
        return self.__repeatquarty('RQS1')
    def set_RequestServiceFun_OFF(self):
        return self.__repeatquarty('RQS0')
if __name__=="__main__":
    indtrumentname='GPIB0::8::INSTR'

    a=PSC44M(indtrumentname)
    print(a.identify())
    a.set_limit(72,20)
    print(a.get_errors())
    print(a.get_set_voltage_current())
    a.set_voltage_in_step(1000)
    a.set_current_in_step(100)
    print(a.get_set_voltage_current())

    print(a.get_voltage())
    print(a.get_current())
    print(a.set_voltage(10))
    print(a.get_errors())
    print(a.set_current(1))
    print(a.get_errors())
    print(a.get_voltage())
    print(a.get_current())
    print(a.get_set_voltage_current())
    print(a.get_set_voltage_current())
    print(a.get_set_voltage_current())
    print(a.get_voltage())
    print(a.get_current())