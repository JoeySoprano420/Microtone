import re

class MicrotonELexer:
    def __init__(self):
        self.tokens = [
            ('KEYWORD', r'\b(start|define function|rest|pause|Done|constant|return|end|for each|parallel for each|if|else|while|print)\b'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NUMBER', r'\d+'),
            ('STRING', r'"[^"]*"'),
            ('COMMENT', r'start[^\n]*'),
            ('OPERATOR', r'[+\-*/]'),
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
                raise ValueError('Unexpected character: %s' % code[0])
        return tokens
