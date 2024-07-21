class MicrotonEParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        statements = []
        while self.position < len(self.tokens):
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        token = self.tokens[self.position]
        if token[0] == 'KEYWORD':
            if token[1] == 'define function':
                return self.parse_function_definition()
            elif token[1] == 'print':
                return self.parse_print_statement()
            # Add other statement types here
        raise ValueError('Unexpected token: %s' % token)

    def parse_function_definition(self):
        # Parse function definition
        pass

    def parse_print_statement(self):
        # Parse print statement
        pass
