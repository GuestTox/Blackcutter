class Event:
    def __init__(self):
        self.functions = []

    def fire(self, *args, **kwargs):
        for func in self.functions:
            func(*args, **kwargs)

    def subscribe(self, func):
        self.functions.append(func)