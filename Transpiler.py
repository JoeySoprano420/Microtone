class MicrotonETranspiler:
    def __init__(self):
        self.byte_code = []

    def transpile(self, ast):
        for statement in ast:
            self.byte_code.append(self.convert_to_byte_code(statement))
        return self.byte_code

    def convert_to_byte_code(self, statement):
        if statement['type'] == 'function_definition':
            return f'DEF {statement["name"]} {len(statement["parameters"])}'
        if statement['type'] == 'print':
            return f'PRINT {statement["expression"]}'
        return 'NOP'
