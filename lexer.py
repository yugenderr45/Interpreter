
from enum import Enum,auto
from collections import namedtuple


class Token(Enum):

    INVALID = auto()
    EOF = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    BEGIN = auto()
    END = auto()
    SWAP=auto()
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIV = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
    ASSIGN = auto()
    EQUAL = auto()
    REAL = auto()
    INT = auto()
    WHILE = auto()
    IF = auto()
    INTNUM = auto()
    REALNUM = auto()
    IDENTIFIER = auto()

Lexeme = namedtuple("Lexeme", ("token", "lex", "value", "line", "col"))


class Lexer:

    def __init__(self, file):
        self.file = file
        self.line = 1
        self.col = 0
        self.cur_char = ' '
        self.cur_tok = None


    def read(self):

        self.cur_char = self.file.read(1)
        if self.cur_char:
            self.col += 1

    def consume(self):

        self.read()

 
        if self.cur_char == '\n':
            self.line += 1
            self.col = 0


    def skip_space(self):

        while self.cur_char.isspace():
            self.consume()


    def group1(self):

        tokens = (('(', Token.LPAREN), (')', Token.RPAREN), 
                  (',', Token.COMMA),
                  ('+', Token.PLUS), ('-', Token.MINUS),
                  ('*', Token.TIMES), ('/', Token.DIV))

        for lex,t in tokens:
            if self.cur_char == lex:
                self.cur_tok = Lexeme(t, lex, lex, self.line, self.col)
                self.consume()
                return True

        return False


    def group2(self):

        tokens = (('<', Token.LT), ('<=', Token.LTE),
                  ('>', Token.GT), ('>=', Token.GTE),
                  (':=', Token.ASSIGN), ('==', Token.EQUAL),(':=:',Token.SWAP))

        line = self.line
        col = self.col

        remain = lambda s : [tok for tok in tokens if tok[0].startswith(s)]

        s = '' 
        while len(remain(s + self.cur_char)) > 0:
            # add the character to our string and consume
            s = s + self.cur_char
            self.consume()

        if len(s) == 0:
            return False

        tokens = remain(s)

        for tok in tokens:
            if tok[0] == s:
                self.cur_tok = Lexeme(tok[1], s, s, line, col)
                return True

        # if we make it here, then this is a partially formed token
        self.cur_tok = Lexeme(Token.INVALID, s, None, line, col)
        return True


    def group3(self):
        if self.cur_char.isalpha():
            return self.group3_letter()
        elif self.cur_char.isdigit():
            return self.group3_number()
        return False


    def group3_letter(self):

        tokens = (('while', Token.WHILE), ('real', Token.REAL),
                  ('int', Token.INT), ('if', Token.IF),('end', Token.END),('END', Token.END),('begin', Token.BEGIN),('BEGIN', Token.BEGIN))

        line = self.line
        col = self.col
        s = ""
        if self.cur_char.isalpha():
            s = s + self.cur_char
            self.consume()
            while self.cur_char.isalpha() or self.cur_char=='[' or self.cur_char==']' or self.cur_char.isdigit():
                s = s + self.cur_char
                self.consume()

        if len(s) == 0:
            return False
        for lex,t in tokens:
            if lex == s:
                self.cur_tok = Lexeme(t, s, s, line, col)
                return True
        self.cur_tok = Lexeme(Token.IDENTIFIER, s, s, line, col)
        return True



    def group3_number(self):

        line = self.line
        col = self.col

        token = Token.INTNUM

        s = ''
        while self.cur_char.isdigit():
            s = s + self.cur_char
            self.consume()

        if len(s) == 0:
            return False

        if self.cur_char != '.':
            self.cur_tok = Lexeme(token, s, int(s), line, col)
            return True

        token = Token.INVALID
        s = s + '.'
        self.consume()

        while self.cur_char.isdigit():
            token = Token.REALNUM
            s = s + self.cur_char
            self.consume()

        # get the value
        if token == Token.REALNUM:
            value = float(s)
        else:
            value = None

        self.cur_tok = Lexeme(token, s, value, line, col)
        return True


    def next(self):

        self.skip_space()

        if not self.cur_char:
            self.cur_tok = Lexeme(Token.EOF, None, None, self.line, self.col)
            return self.cur_tok

        if self.group1():
            return self.cur_tok
        elif self.group2():
            return self.cur_tok
        elif self.group3():
            return self.cur_tok
        else:
            
            self.cur_tok = Lexeme(Token.INVALID, self.cur_char, None, self.line, self.col)
            self.consume()
            return self.cur_tok



if __name__ == '__main__':
    import sys

    file = open(sys.argv[1]) 
    lexer = Lexer(file)
    lexer.next()

    while lexer.cur_tok.token != Token.EOF:
        print(lexer.cur_tok)
        lexer.next()
    print(lexer.cur_tok)
