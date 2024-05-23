import threading
import time

path = "./1_oops.py"
text = ""

def readFile():
    global path, text
    while True:
        with open("./1_oops.py", "r") as f:
            text = f.read()
        time.sleep(5)

def printLoop():
    for i in range(30):
        print(text)
        time.sleep(1)

t1 = threading.Thread(target=readFile, daemon=True)
t2 = threading.Thread(target=printLoop)

t1.start()
t2.start()