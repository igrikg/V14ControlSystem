import serial


def send(ser, msg, echo=False):
    for c in msg + "\r\n":
        ser.write(c.encode())
        if echo:
            response = ser.readline().decode()
            print(response)






ser = serial.Serial('COM8', 9600, timeout=0.2)
data = "W=003"
send(ser, data, True)
response = ser.readline().decode()
print(response)
ser.write('#\r\n'.encode())
response = ser.readline().decode()
response = ser.readline().decode()
print(response)
