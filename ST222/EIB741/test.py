from ctypes import *
from ctypes import byref


eib7dll = ctypes.WinDLL("D:\V14ControlSystem\EIB741\eib7.dll")

mydll = cdll.LoadLibrary("C:\\Users\\igrik\\PycharmProjects\\V14ControlSystem\\EIB741\\eib7.dll")
print(mydll.timeGetTime())
# Call a function from the DLL
text='192.168.8.27'
ip='192.168.8.27'
#my_string = "Hello, world!".encode('utf-8')
#result = my_function(ctypes.c_char_p(my_string))
my_int = ctypes.c_ulong(0)
#result = my_function(ctypes.byref(my_int))
print(my_int)
result = eib7dll.EIB7GetHostIP(text.encode('utf-8'), ctypes.byref(my_int))
print(my_int)

#my_function = mydll.my_function
#my_function.argtypes = [ctypes.POINTER(ctypes.c_int)]
#my_function.restype = ctypes.c_int

print(result)
# Check the result
if result != 0:
    print("my_function returned an error:", result)