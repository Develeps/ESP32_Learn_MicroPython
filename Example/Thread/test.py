import _thread
import time

s = True

def testThread():
    while s:
        print("Hello from thread")
        time.sleep(2)

 
t = _thread
t.start_new_thread(testThread, ())
time.sleep(2)
s = False
