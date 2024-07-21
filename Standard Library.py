class MicrotonELibrary:
    def __init__(self):
        self.library = {
            'factorial': self.factorial
        }

    def factorial(self, n):
        if n == 0:
            return 
