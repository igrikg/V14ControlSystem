import serial

ser = serial.Serial('COM5', 9600,timeout=3)

while True:
    data = input('Enter command: ')
    ser.write((data+"\r").encode())
    response = ser.readline().decode().strip()
    print(response)