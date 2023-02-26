from ctypes import *
from ctypes import byref

mydll = cdll.LoadLibrary("C:\\Users\\igrik\\PycharmProjects\\V14ControlSystem\\EIB741\\eib7.dll")
print(mydll.timeGetTime())
# Call a function from the DLL
text='192.168.8.27'
ip=''
result = eib7dll.EIB7GetHostIP(text, byref(ip))

# Check the result
if result != 0:
    print("my_function returned an error:", result)