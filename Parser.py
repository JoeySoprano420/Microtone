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
        self.position += 2  # Skip 'define function'
        function_name = self.tokens[self.position][1]
        self.position += 1  # Skip function name
        parameters = self.parse_parameters()
        self.position += 1  # Skip 'rest'
        body = self.parse_statements_until('end rest')
        return {'type': 'function_definition', 'name': function_name, 'parameters': parameters, 'body': body}

    def parse_parameters(self):
        self.position += 1  # Skip '('
        parameters = []
        while self.tokens[self.position][1] != ')':
            parameters.append(self.tokens[self.position][1])
            self.position += 1
        self.position += 1  # Skip ')'
        return parameters

    def parse_statements_until(self, end_keyword):
        statements = []
        while self.tokens[self.position][1] != end_keyword:
            statements.append(self.parse_statement())
        self.position += 1  # Skip end keyword
        return statements

    def parse_print_statement(self):
        self.position += 1  # Skip 'print'
        expression = self.tokens[self.position][1]
        self.position += 1  # Skip expression
        self.position += 1  # Skip 'rest'
        return {'type': 'print', 'expression': expression}
