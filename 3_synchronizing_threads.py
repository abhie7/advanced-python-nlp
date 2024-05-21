import threading
import time

x = 8192

lock = threading.Lock() # locks thread on a 

def double():
    global x, lock
    lock.acquire() # tries to acquire the lock if its free
    while x < 16384:
        x *= 2
        print(x)
        time.sleep(0.2)
    print("Reached max")
    lock.release() # releases the lock after reaching the condition

def halve():
    global x, lock
    lock.acquire()
    while x > 1:
        x /= 2
        print(x)
        time.sleep(1)
    print("Reached min")
    lock.release()

t1 = threading.Thread(target=halve)
t2 = threading.Thread(target=double)
t1.start()
t2.start()