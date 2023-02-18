import pyvisa
import time


class IsegNHQ:
    def __init__(self, resource_name):
        rm = pyvisa.ResourceManager()
        self.instr = rm.open_resource(resource_name)
        self.instr.write_termination = '\r'
        self.instr.read_termination = '\r'

    def send_command(self, command):
        response = self.instr.query(command)
        return response.strip()

    def get_status(self):
        response = self.send_command('sstat?')
        return int(response)

    def set_voltage(self, voltage):
        response = self.send_command('vol {:0.2f}'.format(voltage))
        return float(response)

    def get_voltage(self):
        response = self.send_command('vol?')
        return float(response)

    def set_current_limit(self, current_limit):
        response = self.send_command('cmax {:0.2f}'.format(current_limit))
        return float(response)

    def get_current_limit(self):
        response = self.send_command('cmax?')
        return float(response)

    def enable_output(self):
        response = self.send_command('on')
        return response == '1'

    def disable_output(self):
        response = self.send_command('off')
        return response == '0'

    def wait_for_voltage(self, voltage, timeout=60):
        start_time = time.time()
        while True:
            current_voltage = self.get_voltage()
            if abs(current_voltage - voltage) < 0.01:
                return True
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.1)