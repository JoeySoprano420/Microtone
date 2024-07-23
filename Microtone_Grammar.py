import re

class Interpreter:
    def __init__(self):
        self.global_variables = {}
        self.functions = {}
        self.call_stack = []
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

    def execute(self, statements):
        i = 0
        while i < len(statements):
            statement = statements[i]
            if statement[0] == 'assignment':
                var, expr = statement[1:]
                self.set_variable(var, self.evaluate_expression(expr))
            elif statement[0] == 'print':
                print(self.evaluate_expression(statement[1]))
            elif statement[0] == 'if':
                condition, true_statements, false_statements = statement[1:]
                if self.evaluate_expression(condition):
                    self.execute(true_statements)
                else:
                    self.execute(false_statements)
            elif statement[0] == 'loop':
                var, start, end, loop_statements = statement[1:]
                for value in range(start, end + 1):
                    self.set_variable(var, value)
                    self.execute(loop_statements)
            elif statement[0] == 'while':
                condition, while_statements = statement[1:]
                while self.evaluate_expression(condition):
                    try:
                        self.execute(while_statements)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            elif statement[0] == 'comment':
                continue
            elif statement[0] == 'function':
                continue  # Functions are registered but not executed here
            elif statement[0] == 'return':
                return self.evaluate_expression(statement[1])
            elif statement[0] == 'try':
                try_statements, except_statements = statement[1:]
                try:
                    self.execute(try_statements)
                except Exception:
                    self.execute(except_statements)
            elif statement[0] == 'lambda':
                _, default_params, params = statement
                return lambda *args: self.execute_lambda(params, args)
            elif statement[0] == 'call':
                func_name, args = statement[1:]
                if func_name in self.functions:
class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class Interpreter:
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

    def execute(self, statements):
        i = 0
        while i < len(statements):
            statement = statements[i]
            if statement[0] == 'assignment':
                var, expr = statement[1:]
                self.set_variable(var, self.evaluate_expression(expr))
            elif statement[0] == 'print':
                print(self.evaluate_expression(statement[1]))
            elif statement[0] == 'if':
                condition, true_statements, false_statements = statement[1:]
                if self.evaluate_expression(condition):
                    self.execute(true_statements)
                else:
                    self.execute(false_statements)
            elif statement[0] == 'loop':
                var, start, end, loop_statements = statement[1:]
                for value in range(start, end + 1):
                    self.set_variable(var, value)
                    self.execute(loop_statements)
            elif statement[0] == 'while':
                condition, while_statements = statement[1:]
                while self.evaluate_expression(condition):
                    try:
                        self.execute(while_statements)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            elif statement[0] == 'comment':
                continue
            elif statement[0] == 'function':
                continue  # Functions are registered but not executed here
            elif statement[0] == 'return':
                return self.evaluate_expression(statement[1])
            elif statement[0] == 'try':
                try_statements, except_statements = statement[1:]
                try:
                    self.execute(try_statements)
                except Exception:
                    self.execute(except_statements)
            elif statement[0] == 'lambda':
                _, default_params, params = statement
                return lambda *args: self.execute_lambda(params, args)
            elif statement[0] == 'call':
                func_name, args = statement[1:]
                if func_name in self.functions:
                    params, body = self.functions[func_name]
                    local_variables = dict(zip(params, args))
                    local_variables.update(self.global_variables)
                    self.global_variables = local_variables
                    self.execute(body)
                else:
                    raise NameError(f"Function {func_name} not defined")
            elif statement[0] == 'break':
                raise BreakException()
            elif statement[0] == 'continue':
                raise ContinueException()
            i += 1

    def execute_lambda(self, params, args):
        local_variables = dict(zip(params, args))
        local_variables.update(self.global_variables)
        self.global_variables = local_variables
        return self.evaluate_expression(params)

    def evaluate_expression(self, expr):
        if expr[0] == 'number':
            return expr[1]
        elif expr[0] == 'string':
            return expr[1]
        elif expr[0] == 'identifier':
            return self.get_variable(expr[1])
        elif expr[0] == 'operation':
            left, operator, right = expr[1:]
            left_value = self.evaluate_expression(left)
            right_value = self.evaluate_expression(right)
            if operator == '+':
                return left_value + right_value
            elif operator == '-':
                return left_value - right_value
            elif operator == '*':
                return left_value * right_value
            elif operator == '/':
                return left_value / right_value
            elif operator == '==':
                return left_value == right_value
            elif operator == '!=':
                return left_value != right_value
            elif operator == '>':
                return left_value > right_value
            elif operator == '<':
                return left_value < right_value
            elif operator == '>=':
                return left_value >= right_value
            elif operator == '<=':
                return left_value <= right_value
            else:
                raise ValueError(f"Unsupported operator: {operator}")
        elif expr[0] == 'call':
            func_name, args = expr[1:]
            if func_name in self.functions:
                params, body = self.functions[func_name]
                local_variables = dict(zip(params, args))
                local_variables.update(self.global_variables)
                self.global_variables = local_variables
                result = self.execute(body)
                self.global_variables = {k: v for k, v in local_variables.items() if k not in params}
                return result
            else:
                raise NameError(f"Function {func_name} not defined")
        elif expr[0] == 'list':
            return [self.evaluate_expression(element) for element in expr[1]]
        elif expr[0] == 'dictionary':
            return {self.evaluate_expression(k): self.evaluate_expression(v) for k, v in expr[1].items()}
        else:
            raise ValueError(f"Unknown expression type: {expr}")

    def get_variable(self, name):
        if name in self.global_variables:
            return self.global_variables[name]
        else:
            raise NameError(f"Variable {name} not defined")

    def set_variable(self, name, value):
        self.global_variables[name] = value

# Example usage:
interpreter = Interpreter()
code = """
define function add(a, b) rest
    return a + b rest
end rest

x = 5 rest
y = 10 rest
print add(x, y) rest
"""

statements = interpreter.parse_program(code)
interpreter.execute(statements)
