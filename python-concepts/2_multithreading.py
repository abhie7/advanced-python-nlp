import threading

def function1():
    for i in range(10000):
        print("ONE")

def function2():
    for i in range(10000):
        print("TWO")

t1 = threading.Thread(target = function1)
t2 = threading.Thread(target = function2)
# t1.start()
# t2.start()

def hello():
    for i in range(50):
        print("Hello")

d1 = threading.Thread(target=hello)
d1.start()
d1.join() # wont start next statement until d1 is done
print("Boom")