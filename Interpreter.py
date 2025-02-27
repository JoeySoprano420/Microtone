class MicrotonEInterpreter:
    def __init__(self):
        self.variables = {}

    def interpret(self, ast):
        for statement in ast:
            self.execute(statement)

    def execute(self, statement):
        if statement['type'] == 'function_definition':
            self.define_function(statement)
        elif statement['type'] == 'print':
            self.print(statement)

    def define_function(self, statement):
        # Define function logic
        self.variables[statement['name']] = statement

    def print(self, statement):
        value = self.evaluate_expression(statement['expression'])
        print(value)

    def evaluate_expression(self, expression):
        if expression in self.variables:
            return self.variables[expression]
        if expression.isdigit():
            return int(expression)
        return expression
