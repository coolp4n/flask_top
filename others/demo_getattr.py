class Person(object):

    def __init__(self, name):
        self.name = name


p1 = Person("xiaoming")
print(p1.name)
print(getattr(p1, "name"))
# print(getattr(author, "author_id"))
# print(getattr(fans, "user_id"))



