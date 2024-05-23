import threading
import time

semaphore = threading.BoundedSemaphore(value = 5) # at most 5 threads can acquire a semaphore at the same time

def access(thread_number):
    print(f"{thread_number} is trying to access.")
    semaphore.acquire()
    print(f"{thread_number} was granted access.")
    time.sleep(5)
    print(f"{thread_number} is now releasing.")
    semaphore.release()

for thread_number in range(1, 11):
    t = threading.Thread(target=access, args=(thread_number,))
    t.start()
    time.sleep(1) # to see the output clearly