<program> ::= <statement>*
<statement> ::= <functionDefinition> | <assignment> | <conditional> | <loop> | <print> | <comment>
<functionDefinition> ::= "define function" <identifier> "(" <parameters> ")" "rest" <statement>* "end" "rest"
<assignment> ::= <identifier> "=" <expression> "rest"
<conditional> ::= "if" <expression> "rest" <statement>* ("else" "rest" <statement>*)? "end" "rest"
<loop> ::= "for each" <identifier> "in" <range> "rest" <statement>* "end" "rest"
<print> ::= "print" <expression> "rest"
<comment> ::= "start" <text>
<expression> ::= <identifier> | <number> | <string> | <operation>
<identifier> ::= /[a-zA-Z_][a-zA-Z0-9_]*/
<number> ::= /[0-9]+/
<string> ::= /"[^"]*"/
<operation> ::= <expression> <operator> <expression>
<operator> ::= "+" | "-" | "*" | "/"
<parameters> ::= <identifier>* 
<range> ::= <number> "to" <number>
