import ctypes

# Load the DLL
from ctypes import byref

eib7dll = ctypes.WinDLL("eib7.dll")

# Call a function from the DLL
text='192.168.8.27'
ip=''
result = eib7dll.EIB7GetHostIP(text, byref(ip))

# Check the result
if result != 0:
    print("my_function returned an error:", result)