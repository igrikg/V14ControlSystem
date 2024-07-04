import serial

class ST180():

    def __init__(self, comName='COM5'):
        self.serialObject = serial.Serial(comName, 9600, timeout=0.2)
    def __del__(self):
        self.serialObject.close()
    def send(self, comand:str):
        self.serialObject.write((comand+"\r").encode())
        responseToComand = self.serialObject.readline().decode()[:-1]
        responseError = self.serialObject.readline().decode()[1:-1]
        #read /r for clear buffer
        self.serialObject.readline().decode()

        print(responseToComand)
        print(responseError)
        self.__analiseAnswerErrorMessage(responseError)
    def __analiseAnswerErrorMessage(self,responseError):
        if responseError[0]=='!': # command done
            bitString = bin(int(responseError[2],16))[2:].zfill(8)
            axisNumber = int(bitString[-4:],2)
            endMax = bool(int(bitString[-5]))
            endMin = bool(int(bitString[-6]))
            refg = bool(int(bitString[-7]))
            reff = bool(int(bitString[-8]))
            print(axisNumber, endMax,endMin,refg,reff)




if __name__ == "__main__":
    a = ST180("COM5")
    a.send("A")
    a.send("A3")
    a.send("R0")
    a.send("A")

#while True:
    #data = input('Enter command: ')
    #ser.write((data+"\r").encodA1e())
    #response = ser.readline().decode().strip()
