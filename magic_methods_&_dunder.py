# Dunder -> __ (Double underscore)

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __del__(self):
        print("Object is being deleted/destructed.")

p = Person("Abhie", 25)

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"X: {self.x}, Y: {self.y}"

    def __call__(self):
        print("I was called")

v1 = Vector(10,20)
v2 = Vector(50,60)
v3 = v1 + v2
print(v3)
v3()