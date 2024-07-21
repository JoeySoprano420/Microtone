class MicrotonEExecutor:
    def __init__(self, interpreter):
        self.interpreter = interpreter

    def execute_code(self, code):
        lexer = MicrotonELexer()
        tokens = lexer.tokenize(code)
        parser = MicrotonEParser(tokens)
        ast = parser.parse()
        self.interpreter.interpret(ast)
