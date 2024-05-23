class Person:
    amount = 0 # Total number of objects

    def __init__(self, name, age, height):
        self.name = name
        self.age = age
        self.height = height
        Person.amount += 1

    def __str__(self):
        return f"Name: {self.name}, Age: {self.age}, Height: {self.height}"

    def __del__(self):
        print("Object deleted.")
        Person.amount -= 1

# p1 = Person("Abhie", 20, 175)
# # print(p1.name, p1.age, p1.height)
# p2 = Person("Mon2", 25, 164)
# print(p1)
# print(p2)
# print(Person.amount)

# Inheritance
class Student(Person):
    def __init__(self, name, age, height, grade):
        super().__init__(name, age, height) #will inherit this from person class
        self.grade = grade

    def __str__(self):
        # return f"Name: {self.name}, Age: {self.age}, Height: {self.height}, Grade: {self.grade}"
        text = super(Student, self).__str__()
        text += f", Grade: {self.grade}"
        return text

s1 = Student("Abhie", 20, 175, "A")
print(s1)