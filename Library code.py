class MicrotonELibrary:
    def __init__(self):
        self.functions = {}

    def add_function(self, name, function):
        self.functions[name] = function

    def get_function(self, name):
        return self.functions.get(name)
