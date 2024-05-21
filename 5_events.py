import threading

event = threading.Event()

def myFunction():
    print("Waiting for event to trigger...")
    event.wait() # waits until the event is set
    print("Performing action XYZ now...")

t1 = threading.Thread(target=myFunction)
t1.start()

x = input("Do you want to trigger the event? (y/n):\n")
if x == "y":
    event.set() # sets the event
    print("Event is triggered.")