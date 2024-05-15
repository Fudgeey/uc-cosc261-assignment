''' Compiler template for COSC261 Assignment
    ## WARNING ## Your code should be derived from this template 
                  by modifying only the parts mentioned in the requirements; 
                  other changes are at your own risk. 
                  Feel free, however, to experiment during the development.
'''

import re
import sys


# Restrictions:
# Integer constants must be short.
# Stack size must not exceed 1024.
# Integer is the only type.
# Logical operators cannot be nested.

class Scanner:
    '''The interface comprises the methods lookahead and consume.
       Other methods should not be called from outside of this class.
    '''

    def __init__(self, input_file):
        '''Reads the whole input_file to input_string, which remains constant.
           current_char_index counts how many characters of input_string have
           been consumed.
           next_token holds the most recently found token and the
           corresponding part of input_string.
        '''
        # source code of the program to be compiled
        self.input_string = input_file.read()
        # index where the unprocessed part of input_string starts
        self.current_char_index = 0
        # a pair (most recently read token, matched substring of input_string)
        self.next_token = self.get_token()

    def skip_white_space(self):
        """Consumes white-space characters in input_string up to the
           next non-white-space character.
        """

        if self.current_char_index >= len(self.input_string):
            return

        current_char = self.input_string[self.current_char_index]

        while current_char.isspace():
            if len(self.input_string) > self.current_char_index + 1:
                self.current_char_index += 1
                current_char = self.input_string[self.current_char_index]
            else:
                break

    def no_token(self):
        '''Stop execution if the input cannot be matched to a token.'''
        print('lexical error: no token found at the start of ' +
              self.input_string[self.current_char_index:])
        sys.exit()

    def get_token(self):
        """Returns the next token and the part of input_string it matched.
           The returned token is None if there is no next token.
           The characters up to the end of the token are consumed.
           Call no_token() if the input contains extra characters that
           do not match any token (and are not white-space).
        """
        self.skip_white_space()
        # find the longest prefix of input_string that matches a token
        token, longest = None, ''
        for (t, r) in Token.token_regexp:
            match = re.match(r, self.input_string[self.current_char_index:])

            if match and match.end() > len(longest):
                token, longest = t, match.group()

        if token is None and self.current_char_index + 1 < len(self.input_string):
            self.no_token()

        # consume the token by moving the index to the end of the matched part
        self.current_char_index += len(longest)
        return (token, longest)

    def lookahead(self):
        '''Returns the next token without consuming it.
           Returns None if there is no next token.
        '''
        return self.next_token[0]

    def unexpected_token(self, found_token, expected_tokens):
        '''Stop execution because an unexpected token was found.
           found_token contains just the token, not its value.
           expected_tokens is a sequence of tokens.
        '''
        print('syntax error: token in ' + repr(sorted(expected_tokens)) +
              ' expected but ' + repr(found_token) + ' found')
        sys.exit()

    def consume(self, *expected_tokens):
        """Returns the next token and consumes it, if it is in
           expected_tokens. Calls unexpected_token(...) otherwise.
           If the token is a number or an identifier, not just the
           token but a pair of the token and its value is returned.
        """

        token, value = self.next_token

        if token in expected_tokens:
            self.next_token = self.get_token()

            if token in [Token.NUM, Token.ID]:
                return (token, value)
            else:
                return token
        else:
            self.unexpected_token(self.next_token, expected_tokens)


class Token:
    # The following enumerates all tokens.
    DO = 'DO'
    ELSE = 'ELSE'
    END = 'END'
    IF = 'IF'
    THEN = 'THEN'
    WHILE = 'WHILE'
    READ = 'READ'
    WRITE = 'WRITE'
    OR = 'OR'
    AND = 'AND'
    NOT = 'NOT'
    SEM = 'SEM'
    BEC = 'BEC'
    LESS = 'LESS'
    EQ = 'EQ'
    GRTR = 'GRTR'
    LEQ = 'LEQ'
    NEQ = 'NEQ'
    GEQ = 'GEQ'
    ADD = 'ADD'
    SUB = 'SUB'
    MUL = 'MUL'
    DIV = 'DIV'
    LPAR = 'LPAR'
    RPAR = 'RPAR'
    NUM = 'NUM'
    ID = 'ID'

    # The following list gives the regular expression to match a token.
    # The order in the list matters for mimicking Flex behaviour.
    # Longer matches are preferred over shorter ones.
    # For same-length matches, the first in the list is preferred.
    token_regexp = [
        (DO, 'do'),
        (ELSE, 'else'),
        (END, 'end'),
        (IF, 'if'),
        (THEN, 'then'),
        (WHILE, 'while'),
        (READ, 'read'),
        (WRITE, 'write'),
        (OR, 'or'),
        (AND, 'and'),
        (NOT, 'not'),
        (SEM, ';'),
        (BEC, ':='),
        (LESS, '<'),
        (EQ, '='),
        (GRTR, '>'),
        (LEQ, '<='),
        (NEQ, '!='),
        (GEQ, '>='),
        (ADD, '\\+'),  # + is special in regular expressions
        (SUB, '-'),
        (MUL, '\\*'),
        (DIV, '/'),
        (LPAR, '\\('),  # ( is special in regular expressions
        (RPAR, '\\)'),  # ) is special in regular expressions
        (NUM, '0+|[1-9][0-9]*'),  # is all zeros valid? is 0005 valid?
        (ID, '[a-z]+'),
    ]


class Symbol_Table:
    """A symbol table maps identifiers to locations."""

    def __init__(self):
        self.symbol_table = {}

    def size(self):
        """Returns the number of entries in the symbol table."""
        return len(self.symbol_table)

    def location(self, identifier):
        """Returns the location of an identifier. If the identifier is not in
           the symbol table, it is entered with a new location.
           Locations are numbered sequentially starting with 0.
        """
        if identifier in self.symbol_table:
            return self.symbol_table[identifier]
        index = len(self.symbol_table)
        self.symbol_table[identifier] = index
        return index


class Label:
    def __init__(self):
        self.current_label = 0

    def next(self):
        """Returns a new, unique label."""
        self.current_label += 1
        return 'l' + str(self.current_label)


def indent(s, level):
    return '    ' * level + s + '\n'


# Each of the following classes is a kind of node in the abstract syntax tree.
# indented(level) returns a string that shows the tree levels by indentation.
# code() returns a string with JVM bytecode implementing the tree fragment.
# true_code/false_code(label) jumps to label if the condition is/is not true.
# Execution of the generated code leaves the value of expressions on the stack.

class Program_AST:
    def __init__(self, program):
        self.program = program

    def __repr__(self):
        return repr(self.program)

    def indented(self, level):
        return self.program.indented(level)

    def code(self):
        program = self.program.code()
        local = symbol_table.size()
        java_scanner = symbol_table.location('Java Scanner')
        return '.class public Program\n' + \
            '.super java/lang/Object\n' + \
            '.method public <init>()V\n' + \
            'aload_0\n' + \
            'invokenonvirtual java/lang/Object/<init>()V\n' + \
            'return\n' + \
            '.end method\n' + \
            '.method public static main([Ljava/lang/String;)V\n' + \
            '.limit locals ' + str(local) + '\n' + \
            '.limit stack 1024\n' + \
            'new java/util/Scanner\n' + \
            'dup\n' + \
            'getstatic java/lang/System.in Ljava/io/InputStream;\n' + \
            'invokespecial java/util/Scanner.<init>(Ljava/io/InputStream;)V\n' + \
            'astore ' + str(java_scanner) + '\n' + \
            program + \
            'return\n' + \
            '.end method\n'


class Statements_AST:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        result = repr(self.statements[0])
        for st in self.statements[1:]:
            result += '; ' + repr(st)
        return result

    def indented(self, level):
        result = indent('Statements', level)
        for st in self.statements:
            result += st.indented(level + 1)
        return result

    def code(self):
        result = ''
        for st in self.statements:
            result += st.code()
        return result


class If_AST:
    def __init__(self, condition, then):
        self.condition = condition
        self.then = then

    def __repr__(self):
        return 'if ' + repr(self.condition) + ' then ' + \
            repr(self.then) + ' end'

    def indented(self, level):
        return indent('If', level) + \
            self.condition.indented(level + 1) + \
            self.then.indented(level + 1)

    def code(self):
        l1 = label_generator.next()
        return self.condition.false_code(l1) + \
            self.then.code() + \
            l1 + ':\n'


class If_Else_AST:
    def __init__(self, condition, then_if, then_else):
        self.condition = condition
        self.then_if = then_if
        self.then_else = then_else

    def __repr__(self):
        return 'if ' + repr(self.condition) + ' then ' + \
            repr(self.then_if) + ' else ' + repr(self.then_else) + ' end'

    def indented(self, level):
        return indent('If-Else', level) + \
            self.condition.indented(level + 1) + \
            self.then_if.indented(level + 1) + \
            self.then_else.indented(level + 1)

    def code(self):
        l1 = label_generator.next()
        l2 = label_generator.next()

        return self.condition.false_code(l1) + \
            self.then_if.code() + \
            'goto ' + l2 + '\n' + \
            l1 + ':\n' + \
            self.then_else.code() + \
            l2 + ':\n'


class While_AST:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return 'while ' + repr(self.condition) + ' do ' + \
            repr(self.body) + ' end'

    def indented(self, level):
        return indent('While', level) + \
            self.condition.indented(level + 1) + \
            self.body.indented(level + 1)

    def code(self):
        l1 = label_generator.next()
        l2 = label_generator.next()
        return l1 + ':\n' + \
            self.condition.false_code(l2) + \
            self.body.code() + \
            'goto ' + l1 + '\n' + \
            l2 + ':\n'


class Assign_AST:
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def __repr__(self):
        return repr(self.identifier) + ':=' + repr(self.expression)

    def indented(self, level):
        return indent('Assign', level) + \
            self.identifier.indented(level + 1) + \
            self.expression.indented(level + 1)

    def code(self):
        loc = symbol_table.location(self.identifier.identifier)
        return self.expression.code() + \
            'istore ' + str(loc) + '\n'


class Write_AST:
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return 'write ' + repr(self.expression)

    def indented(self, level):
        return indent('Write', level) + self.expression.indented(level + 1)

    def code(self):
        return 'getstatic java/lang/System/out Ljava/io/PrintStream;\n' + \
            self.expression.code() + \
            'invokestatic java/lang/String/valueOf(I)Ljava/lang/String;\n' + \
            'invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V\n'


class Read_AST:
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return 'read ' + repr(self.identifier)

    def indented(self, level):
        return indent('Read', level) + self.identifier.indented(level + 1)

    def code(self):
        java_scanner = symbol_table.location('Java Scanner')
        loc = symbol_table.location(self.identifier.identifier)
        return 'aload ' + str(java_scanner) + '\n' + \
            'invokevirtual java/util/Scanner.nextInt()I\n' + \
            'istore ' + str(loc) + '\n'


class Comparison_AST:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return repr(self.left) + self.op + repr(self.right)

    def indented(self, level):
        return indent(self.op, level) + \
            self.left.indented(level + 1) + \
            self.right.indented(level + 1)

    def true_code(self, label):
        op = {'<': 'if_icmplt', '=': 'if_icmpeq', '>': 'if_icmpgt',
              '<=': 'if_icmple', '!=': 'if_icmpne', '>=': 'if_icmpge'}
        return self.left.code() + \
            self.right.code() + \
            op[self.op] + ' ' + label + '\n'

    def false_code(self, label):
        # Negate each comparison because of jump to "false" label.
        op = {'<': 'if_icmpge', '=': 'if_icmpne', '>': 'if_icmple',
              '<=': 'if_icmpgt', '!=': 'if_icmpeq', '>=': 'if_icmplt'}
        return self.left.code() + \
            self.right.code() + \
            op[self.op] + ' ' + label + '\n'


class Expression_AST:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return '(' + repr(self.left) + self.op + repr(self.right) + ')'

    def indented(self, level):
        return indent(self.op, level) + \
            self.left.indented(level + 1) + \
            self.right.indented(level + 1)

    def code(self):
        op = {'+': 'iadd', '-': 'isub', '*': 'imul', '/': 'idiv'}
        return self.left.code() + \
            self.right.code() + \
            op[self.op] + '\n'


class Boolean_Expression_AST:
    def __init__(self, terms):
        self.terms = terms

    def __repr__(self):
        return "Boolean_Expression_AST"

    def indented(self, level):
        output = ""

        for term in self.terms:
            output += term.indented(level)

        return output

    def true_code(self, label):
        result = ""

        for term in self.terms:
            result += term.code(label)

        return result

    def false_code(self, label):
        l1 = label_generator.next()
        result = ""

        for term in self.terms:
            result += term.code(l1)

        result += f"goto {label}\n{l1}:\n"
        return result


class Boolean_Term_AST:
    def __init__(self, factors):
        self.factors = factors

    def __repr__(self):
        return "Boolean_Term_AST"

    def indented(self, level):
        output = ""

        for factor in self.factors:
            output += factor.indented(level)

        return output

    def code(self, label):
        l1 = label_generator.next()
        result = ""

        for factor in self.factors:
            result += factor.true_code(l1)

        result += f"goto {label}\n{l1}:\n"
        return result

class Boolean_Factor_AST:
    def __init__(self, factor):
        self.factor = factor

    def __repr__(self):
        return f"({self.factor})"

    def indented(self, level):
        if type(self.factor) is Comparison_AST:
            return self.factor.indented(level)

    def true_code(self, label):
        return self.factor.false_code(label)

    def false_code(self, label):
        return self.factor.true_code(label)


class Number_AST:
    def __init__(self, number):
        self.number = number

    def __repr__(self):
        return self.number

    def indented(self, level):
        return indent(self.number, level)

    def code(self):  # works only for short numbers
        return 'sipush ' + self.number + '\n'


class Identifier_AST:
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return self.identifier

    def indented(self, level):
        return indent(self.identifier, level)

    def code(self):
        loc = symbol_table.location(self.identifier)
        return 'iload ' + str(loc) + '\n'


# The following functions comprise the recursive-descent parser.

def program():
    sts = statements()
    return Program_AST(sts)


def statements():
    result = [statement()]
    while scanner.lookahead() == Token.SEM:
        scanner.consume(Token.SEM)
        st = statement()
        result.append(st)
    return Statements_AST(result)


def statement():
    if scanner.lookahead() == Token.IF:
        return if_statement()
    elif scanner.lookahead() == Token.WHILE:
        return while_statement()
    elif scanner.lookahead() == Token.ID:
        return assignment()
    elif scanner.lookahead() == Token.WRITE:
        return write()
    elif scanner.lookahead() == Token.READ:
        return read()
    else:  # error
        return scanner.consume(Token.IF, Token.WHILE, Token.ID)


def if_statement():
    scanner.consume(Token.IF)
    condition = boolean_expression()
    scanner.consume(Token.THEN)
    then_if = statements()

    if scanner.lookahead() == Token.ELSE:
        scanner.consume(Token.ELSE)
        then_else = statements()
        scanner.consume(Token.END)
        return If_Else_AST(condition, then_if, then_else)
    else:
        scanner.consume(Token.END)
        return If_AST(condition, then_if)


def while_statement():
    scanner.consume(Token.WHILE)
    condition = boolean_expression()
    scanner.consume(Token.DO)
    body = statements()
    scanner.consume(Token.END)
    return While_AST(condition, body)


def assignment():
    ident = identifier()
    scanner.consume(Token.BEC)
    expr = expression()
    return Assign_AST(ident, expr)


def write():
    scanner.consume(Token.WRITE)
    expr = expression()
    return Write_AST(expr)


def read():
    scanner.consume(Token.READ)
    ident = identifier()
    return Read_AST(ident)


operator = {Token.LESS: '<', Token.EQ: '=', Token.GRTR: '>',
            Token.LEQ: '<=', Token.NEQ: '!=', Token.GEQ: '>=',
            Token.ADD: '+', Token.SUB: '-', Token.MUL: '*', Token.DIV: '/'}

boolean_operator = {Token.OR: 'or', Token.AND: 'and', Token.NOT: 'not'}


def comparison():
    left = expression()
    op = scanner.consume(Token.LESS, Token.EQ, Token.GRTR,
                         Token.LEQ, Token.NEQ, Token.GEQ)
    right = expression()
    return Comparison_AST(left, operator[op], right)


def boolean_expression():
    terms = [boolean_term()]

    while scanner.lookahead() == Token.OR:
        scanner.consume(Token.OR)
        term = boolean_term()
        terms.append(term)

    return Boolean_Expression_AST(terms)


def boolean_term():
    factors = [boolean_factor()]

    while scanner.lookahead() == Token.AND:
        scanner.consume(Token.AND)
        factor = boolean_factor()
        factors.append(factor)

    return Boolean_Term_AST(factors)


def boolean_factor():
    if scanner.lookahead() == Token.NOT:
        scanner.consume(Token.NOT)
        result = boolean_factor()
        return Boolean_Factor_AST(result)
    else:
        result = comparison()
        return Boolean_Factor_AST(result)


def expression():
    result = term()
    while scanner.lookahead() in [Token.ADD, Token.SUB]:
        op = scanner.consume(Token.ADD, Token.SUB)
        tree = term()
        result = Expression_AST(result, operator[op], tree)
    return result


def term():
    result = factor()
    while scanner.lookahead() in [Token.MUL, Token.DIV]:
        op = scanner.consume(Token.MUL, Token.DIV)
        tree = factor()
        result = Expression_AST(result, operator[op], tree)
    return result


def factor():
    if scanner.lookahead() == Token.LPAR:
        scanner.consume(Token.LPAR)
        result = expression()
        scanner.consume(Token.RPAR)
        return result
    elif scanner.lookahead() == Token.NUM:
        value = scanner.consume(Token.NUM)[1]
        return Number_AST(value)
    elif scanner.lookahead() == Token.ID:
        return identifier()
    else:  # error
        return scanner.consume(Token.LPAR, Token.NUM, Token.ID)


def identifier():
    value = scanner.consume(Token.ID)[1]
    return Identifier_AST(value)


# Initialise scanner, symbol table and label generator.

scanner = Scanner(sys.stdin)
symbol_table = Symbol_Table()
symbol_table.location('Java Scanner')  # fix a location for the Java Scanner
label_generator = Label()

# Uncomment the following to test the scanner without the parser.
# Show all tokens in the input.
#
# token = scanner.lookahead()
# while token != None:
#     if token in [Token.NUM, Token.ID]:
#         token, value = scanner.consume(token)
#         print(token, value)
#     else:
#         print(scanner.consume(token))
#     token = scanner.lookahead()
# sys.exit()

# Call the parser.

ast = program()
if scanner.lookahead() != None:
    print('syntax error: end of input expected but token ' +
          repr(scanner.lookahead()) + ' found')
    sys.exit()

# Uncomment the following to test the parser without the code generator.
# Show the syntax tree with levels indicated by indentation.
#
# print(ast.indented(0), end='')
# sys.exit()

# Call the code generator.

# Translate the abstract syntax tree to JVM bytecode.
# It can be assembled to a class file by Jasmin: http://jasmin.sourceforge.net/

print(ast.code(), end='')
