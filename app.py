import re

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class MicrotonELexer:
    def __init__(self):
        self.tokens = [
            ('KEYWORD', r'\b(start|define function|rest|pause|Done|constant|return|end|for each|parallel for each|if|else|while|print|try|except|lambda|break rest|continue rest)\b'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NUMBER', r'\d+'),
            ('STRING', r'"[^"]*"'),
            ('COMMENT', r'start[^\n]*'),
            ('OPERATOR', r'[+\-*/><=!]+'),
            ('WHITESPACE', r'\s+'),
        ]

    def tokenize(self, code):
        tokens = []
        while code:
            for token_type, regex in self.tokens:
                match = re.match(regex, code)
                if match:
                    text = match.group(0)
                    if token_type != 'WHITESPACE':
                        tokens.append((token_type, text))
                    code = code[len(text):]
                    break
            else:
                raise ValueError(f'Unexpected character: {code[0]}')
        return tokens

class MicrotoneInterpreter:
    def __init__(self):
        self.global_variables = {}
        self.functions = {}
        self.builtins = {
            'print': print
        }

    def parse_program(self, code):
        lines = code.split("\n")
        statements = []
        while lines:
            line = lines.pop(0).strip()
            if line:
                statements.append(self.parse_statement(line, lines))
        return statements

    def parse_statement(self, line, lines):
        if line.startswith("define function"):
            return self.parse_function_definition(line, lines)
        elif "=" in line:
            return self.parse_assignment(line)
        elif line.startswith("if"):
            return self.parse_conditional(line, lines)
        elif line.startswith("for each"):
            return self.parse_loop(line, lines)
        elif line.startswith("while"):
            return self.parse_while_loop(line, lines)
        elif line.startswith("print"):
            return self.parse_print(line)
        elif line.startswith("start"):
            return self.parse_comment(line)
        elif line.startswith("return"):
            return self.parse_return(line)
        elif line.startswith("try"):
            return self.parse_try_except(line, lines)
        elif line.startswith("lambda"):
            return self.parse_lambda(line)
        elif line.startswith("break rest"):
            return ('break',)
        elif line.startswith("continue rest"):
            return ('continue',)
        else:
            return self.parse_expression(line)

    def parse_function_definition(self, line, lines):
        match = re.match(r"define function (\w+)\((.*?)\) rest", line)
        if not match:
            raise SyntaxError(f"Invalid function definition: {line}")
        func_name, params = match.groups()
        params = [param.strip() for param in params.split(",")] if params else []
        statements = []
        while lines:
            line = lines.pop(0).strip()
            if line == "end rest":
                break
            statements.append(self.parse_statement(line, lines))
        self.functions[func_name] = (params, statements)
        return ('function', func_name, params, statements)

    def parse_assignment(self, line):
        match = re.match(r"(\w+) = (.*) rest", line)
        if not match:
            raise SyntaxError(f"Invalid assignment: {line}")
        var, expr = match.groups()
        return ('assignment', var, self.parse_expression(expr))

    def parse_conditional(self, line, lines):
        match = re.match(r"if (.*) rest", line)
        if not match:
            raise SyntaxError(f"Invalid conditional: {line}")
        expr = match.groups()[0]
        true_statements = []
        false_statements = []
        current_statements = true_statements
        while lines:
            line = lines.pop(0).strip()
            if line == "end rest":
                break
            elif line == "else rest":
                current_statements = false_statements
            else:
                current_statements.append(self.parse_statement(line, lines))
        return ('if', self.parse_expression(expr), true_statements, false_statements)

    def parse_loop(self, line, lines):
        match = re.match(r"for each (\w+) in (\d+) to (\d+) rest", line)
        if not match:
            raise SyntaxError(f"Invalid loop: {line}")
        var, start, end = match.groups()
        statements = []
        while lines:
            line = lines.pop(0).strip()
            if line == "end rest":
                break
            statements.append(self.parse_statement(line, lines))
        return ('loop', var, int(start), int(end), statements)

    def parse_while_loop(self, line, lines):
        match = re.match(r"while (.*) rest", line)
        if not match:
            raise SyntaxError(f"Invalid while loop: {line}")
        condition = match.groups()[0]
        statements = []
        while lines:
            line = lines.pop(0).strip()
            if line == "end rest":
                break
            statements.append(self.parse_statement(line, lines))
        return ('while', self.parse_expression(condition), statements)

    def parse_print(self, line):
        match = re.match(r"print (.*) rest", line)
        if not match:
            raise SyntaxError(f"Invalid print statement: {line}")
        expr = match.groups()[0]
        return ('print', self.parse_expression(expr))

    def parse_comment(self, line):
        match = re.match(r"start (.*)", line)
        if not match:
            raise SyntaxError(f"Invalid comment: {line}")
        text = match.groups()[0]
        return ('comment', text)

    def parse_return(self, line):
        match = re.match(r"return (.*) rest", line)
        if not match:
            raise SyntaxError(f"Invalid return statement: {line}")
        expr = match.groups()[0]
        return ('return', self.parse_expression(expr))

    def parse_try_except(self, line, lines):
        match = re.match(r"try rest", line)
        if not match:
            raise SyntaxError(f"Invalid try block: {line}")
        try_statements = []
        while lines:
            line = lines.pop(0).strip()
            if line == "except rest":
                break
            try_statements.append(self.parse_statement(line, lines))
        except_statements = []
        while lines:
            line = lines.pop(0).strip()
            if line == "end rest":
                break
            except_statements.append(self.parse_statement(line, lines))
        return ('try', try_statements, except_statements)

    def parse_lambda(self, line):
        match = re.match(r"lambda (\w*) \(?(.*)\)? rest", line)
        if not match:
            raise SyntaxError(f"Invalid lambda function: {line}")
        default_params, params = match.groups()
        params = [param.strip() for param in params.split(",")] if params else []
        return ('lambda', default_params, params)

    def parse_expression(self, expr):
        expr = expr.strip()
        if re.match(r"^\d+$", expr):
            return ('number', int(expr))
        elif re.match(r'^".*"$', expr):
            return ('string', expr.strip('"'))
        elif re.match(r"^\w+\(.*\)$", expr):
            match = re.match(r"(\w+)\((.*)\)", expr)
            if not match:
                raise SyntaxError(f"Invalid function call: {expr}")
            func_name, args = match.groups()
            args = [self.parse_expression(arg.strip()) for arg in args.split(",")] if args else []
            return ('call', func_name, args)
        elif re.match(r"^\[.*\]$", expr):
            elements = expr[1:-1].split(",")
            return ('list', [self.parse_expression(element.strip()) for element in elements])
        elif re.match(r"^\{.*\}$", expr):
            elements = expr[1:-1].split(",")
            return ('dictionary', {self.parse_expression(k.strip()): self.parse_expression(v.strip()) for k, v in (element.split(":") for element in elements)})
        elif re.match(r"^\w+$", expr):
            return ('identifier', expr)
        else:
            match = re.match(r"(.*?)([+\-*/><=!]+)(.*)", expr)
            if not match:
                raise SyntaxError(f"Invalid expression: {expr}")
            left, operator, right = match.groups()
            return ('operation', self.parse_expression(left.strip()), operator.strip(), self.parse_expression(right.strip()))

    def evaluate_expression(self, expr):
        if expr[0] == 'number':
            return expr[1]
        elif expr[0] == 'string':
            return expr[1]
        elif expr[0] == 'identifier':
            return self.global_variables.get(expr[1], None)
        elif expr[0] == 'operation':
            left = self.evaluate_expression(expr[1])
            right = self.evaluate_expression(expr[3])
            operator = expr[2]
            if operator == '+':
                return left + right
            elif operator == '-':
                return left - right
            elif operator == '*':
                return left * right
            elif operator == '/':
                return left / right
            elif operator == '==':
                return left == right
            elif operator == '!=':
                return left != right
            elif operator == '<':
                return left < right
            elif operator == '>':
                return left > right
            elif operator == '<=':
                return left <= right
            elif operator == '>=':
                return left >= right
            else:
                raise ValueError(f"Unknown operator: {operator}")
        elif expr[0] == 'call':
            func_name = expr[1]
            args = [self.evaluate_expression(arg) for arg in expr[2]]
            func = self.functions.get(func_name)
            if func:
                params, body = func
                if len(args) != len(params):
                    raise TypeError(f"Function {func_name} expected {len(params)} arguments, got {len(args)}")
                local_vars = dict(zip(params, args))
                old_vars = self.global_variables.copy()
                self.global_variables.update(local_vars)
                result = None
                for statement in body:
                    result = self.execute_statement(statement)
                    if isinstance(result, BreakException):
                        break
                    elif isinstance(result, ContinueException):
                        continue
                self.global_variables = old_vars
                return result
            else:
                raise NameError(f"Function {func_name} not defined")
        elif expr[0] == 'list':
            return [self.evaluate_expression(element) for element in expr[1]]
        elif expr[0] == 'dictionary':
            return {self.evaluate_expression(k): self.evaluate_expression(v) for k, v in expr[1].items()}
        else:
            raise ValueError(f"Unknown expression type: {expr[0]}")

    def execute_statement(self, statement):
        if statement[0] == 'assignment':
            var_name, expr = statement[1], statement[2]
            self.global_variables[var_name] = self.evaluate_expression(expr)
        elif statement[0] == 'function':
            func_name, params, body = statement[1], statement[2], statement[3]
            self.functions[func_name] = (params, body)
        elif statement[0] == 'print':
            value = self.evaluate_expression(statement[1])
            self.builtins['print'](value)
        elif statement[0] == 'if':
            condition, true_statements, false_statements = statement[1], statement[2], statement[3]
            if self.evaluate_expression(condition):
                for stmt in true_statements:
                    result = self.execute_statement(stmt)
                    if isinstance(result, BreakException):
                        break
                    elif isinstance(result, ContinueException):
                        continue
            else:
                for stmt in false_statements:
                    result = self.execute_statement(stmt)
                    if isinstance(result, BreakException):
                        break
                    elif isinstance(result, ContinueException):
                        continue
        elif statement[0] == 'loop':
            var_name, start, end, statements = statement[1], statement[2], statement[3], statement[4]
            for i in range(start, end + 1):
                self.global_variables[var_name] = i
                for stmt in statements:
                    result = self.execute_statement(stmt)
                    if isinstance(result, BreakException):
                        break
                    elif isinstance(result, ContinueException):
                        continue
        elif statement[0] == 'while':
            condition, statements = statement[1], statement[2]
            while self.evaluate_expression(condition):
                for stmt in statements:
                    result = self.execute_statement(stmt)
                    if isinstance(result, BreakException):
                        break
                    elif isinstance(result, ContinueException):
                        continue
        elif statement[0] == 'return':
            return self.evaluate_expression(statement[1])
        elif statement[0] == 'comment':
            pass
        elif statement[0] == 'try':
            try_statements, except_statements = statement[1], statement[2]
            try:
                for stmt in try_statements:
                    result = self.execute_statement(stmt)
                    if isinstance(result, BreakException):
                        break
                    elif isinstance(result, ContinueException):
                        continue
            except Exception:
                for stmt in except_statements:
                    result = self.execute_statement(stmt)
                    if isinstance(result, BreakException):
                        break
                    elif isinstance(result, ContinueException):
                        continue
        elif statement[0] == 'lambda':
            pass  # Lambda handling is not yet implemented
        elif statement[0] == 'break':
            raise BreakException
        elif statement[0] == 'continue':
            raise ContinueException
        else:
            raise ValueError(f"Unknown statement type: {statement[0]}")

    def execute(self, code):
        lexer = MicrotonELexer()
        tokens = lexer.tokenize(code)
        program = self.parse_program(code)
        for stmt in program:
            self.execute_statement(stmt)

# Sample usage
code = """
define function add(x, y) rest
    return x + y rest
end rest

start This is a comment
print "Hello, world!" rest
x = 10 rest
y = 20 rest
print add(x, y) rest
"""

interpreter = MicrotoneInterpreter()
interpreter.execute(code)
