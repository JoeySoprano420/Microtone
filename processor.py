class MicrotonEProcessor:
    def __init__(self):
        self.executor = MicrotonEExecutor(MicrotonEInterpreter())

    def process(self, code):
        self.executor.execute_code(code)
