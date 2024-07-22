import re

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}

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
        elif line.startswith("print"):
            return self.parse_print(line)
        elif line.startswith("start"):
            return self.parse_comment(line)
        else:
            raise SyntaxError(f"Unknown statement: {line}")

    def parse_function_definition(self, line, lines):
        _, func_name, params = re.match(r"define function (\w+)\((.*?)\) rest", line).groups()
        params = params.split(",") if params else []
        statements = []
        while lines:
            line = lines.pop(0).strip()
            if line == "end rest":
                break
            statements.append(self.parse_statement(line, lines))
        self.functions[func_name] = (params, statements)
        return ('function', func_name, params, statements)

    def parse_assignment(self, line):
        var, expr = re.match(r"(\w+) = (.*) rest", line).groups()
        return ('assignment', var, self.parse_expression(expr))

    def parse_conditional(self, line, lines):
        _, expr = re.match(r"if (.*) rest", line).groups()
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
        _, var, start, end = re.match(r"for each (\w+) in (\d+) to (\d+) rest", line).groups()
        statements = []
        while lines:
            line = lines.pop(0).strip()
            if line == "end rest":
                break
            statements.append(self.parse_statement(line, lines))
        return ('loop', var, int(start), int(end), statements)

    def parse_print(self, line):
        _, expr = re.match(r"print (.*) rest", line).groups()
        return ('print', self.parse_expression(expr))

    def parse_comment(self, line):
        _, text = re.match(r"start (.*)", line).groups()
        return ('comment', text)

    def parse_expression(self, expr):
        expr = expr.strip()
        if re.match(r"^\d+$", expr):
            return ('number', int(expr))
        elif re.match(r'^".*"$', expr):
            return ('string', expr.strip('"'))
        elif re.match(r"^\w+$", expr):
            return ('identifier', expr)
        else:
            for op in ["+", "-", "*", "/"]:
                if op in expr:
                    left, right = expr.split(op, 1)
                    return ('operation', self.parse_expression(left), op, self.parse_expression(right))
            raise SyntaxError(f"Invalid expression: {expr}")

    def execute(self, statements):
        for statement in statements:
            self.execute_statement(statement)

    def execute_statement(self, statement):
        if statement[0] == 'assignment':
            _, var, expr = statement
            self.variables[var] = self.evaluate_expression(expr)
        elif statement[0] == 'if':
            _, expr, true_statements, false_statements = statement
            if self.evaluate_expression(expr):
                self.execute(true_statements)
            else:
                self.execute(false_statements)
        elif statement[0] == 'loop':
            _, var, start, end, statements = statement
            for i in range(start, end+1):
                self.variables[var] = i
                self.execute(statements)
        elif statement[0] == 'print':
            _, expr = statement
            print(self.evaluate_expression(expr))
        elif statement[0] == 'comment':
            pass  # Comments are ignored in execution
        elif statement[0] == 'function':
            pass  # Functions are already registered in parse phase

    def evaluate_expression(self, expr):
        if expr[0] == 'number':
            return expr[1]
        elif expr[0] == 'string':
            return expr[1]
        elif expr[0] == 'identifier':
            return self.variables.get(expr[1], None)
        elif expr[0] == 'operation':
            _, left, op, right = expr
            left_val = self.evaluate_expression(left)
            right_val = self.evaluate_expression(right)
            if op == '+':
                return left_val + right_val
            elif op == '-':
                return left_val - right_val
            elif op == '*':
                return left_val * right_val
            elif op == '/':
                return left_val / right_val

# Example usage:
code = """
define function myFunc(x) rest
    print x rest
end rest

x = 5 rest
print x rest
if x > 3 rest
    print "x is greater than 3" rest
else rest
    print "x is not greater than 3" rest
end rest

for each i in 1 to 3 rest
    print i rest
end rest
"""

interpreter = Interpreter()
statements = interpreter.parse_program(code)
interpreter.execute(statements)
