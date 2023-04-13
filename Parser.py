"""
This module implements a parser and includes a unit test for that parser.
"""
from lexer import Token,Lexer
from interpreter import *


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.errors = 0


    def next(self):
        self.lexer.next()


    def match(self, token):
        if hasattr(token, '__iter__'):
            return self.lexer.cur_tok.token in token

        return self.lexer.cur_tok.token == token



    def have(self, token):
        if self.match(token):
            self.next()
            return True
        return False


    def must_be(self, token, error_msg="Unexpected Token"):

        if self.match(token):
            self.next()
            return

        # error!
        self.errors += 1
        error_tok = self.lexer.cur_tok
        self.next()
        print("Error: %s %s:\"%s\" at Line %d Column %d"%(error_msg, 
            error_tok.token, error_tok.lex, error_tok.line, error_tok.col))


    def parse(self):

        self.next()

        result = self.parse_program()
        if self.errors == 0:
            return result
        else:
            return False


    def parse_program(self):
        block = ParseNode(eval_block, [])

        block.child.append(self.parse_function_def())

        while not self.have(Token.EOF):
            block.child.append(self.parse_function_def())
        main_call = ParseNode(eval_call, ['main'])
        block.child.append(main_call)
        return block


    def parse_function_def(self):
        """
        < Function-Def >    ::= < Signature > < Block >
        """

        fun_def = ParseNode(eval_function_def, [])
        self.parse_signature(fun_def)

        fun_def.child.append(self.parse_block())
        return fun_def


    def parse_signature(self, fun_def):

        t = self.parse_type()

        if t == Token.REAL:
            fun_def.child.append(SymType.FUN_REAL)
        else:
            fun_def.child.append(SymType.FUN_INT)

        name_token = self.lexer.cur_tok
        self.must_be(Token.IDENTIFIER)
        self.must_be(Token.LPAREN)

        # extract the name
        fun_def.child.append(name_token.lex)

        # handle signature'
        if self.have(Token.RPAREN):
            # blank param list
            fun_def.child.append([])
            return
        fun_def.child.append(self.parse_params())
        self.must_be(Token.RPAREN, "Mismatched Parenthesis")
            

    def parse_params(self):

        result = [self.parse_decl()]
        while self.have(Token.COMMA):
            result.append(self.parse_decl())
        return result


    def parse_block(self):
        block = ParseNode(eval_block, [])

        self.must_be(Token.BEGIN)

        if self.have(Token.END):
            return block
        self.parse_statement_list(block)
        self.must_be(Token.END, "Mismatched Braces")
        return block


    def parse_statement_list(self, block):
        block.child.append(self.parse_statement())

        first = (Token.REAL, Token.INT, Token.IDENTIFIER, Token.INTNUM, 
                 Token.REALNUM, Token.LPAREN, Token.WHILE, Token.IF)
        while self.match(first):
            block.child.append(self.parse_statement())


    def parse_statement(self):

        
        semi = False 
        result = None

        if self.match((Token.REAL, Token.INT)):
            semi = True
            result = ParseNode(eval_decl, self.parse_decl())
        elif self.match(Token.WHILE):
            result = self.parse_while()
        elif self.match(Token.IF):
            result = self.parse_if()
        elif self.match(Token.IDENTIFIER):
            # get the identifier
            name_token = self.lexer.cur_tok
            self.next()

            semi = True
            # Statement'
            if self.have(Token.ASSIGN):
                result = ParseNode(eval_assign, [name_token.lex, self.parse_expr()])
            elif self.have(Token.SWAP):
                result = ParseNode(eval_swap, [name_token.lex, self.parse_expr()])
            elif self.have(Token.LPAREN):
                result = self.parse_call2(name_token.lex)
            else:
                result = self.parse_expr2(ParseNode(eval_identifier, [name_token.lex]))
        else:
            semi = True
            result = self.parse_expr()
        sei=True
        # semi colon check at the end
        if semi:
            pass
        return result


    def parse_call2(self, identifier):

        if self.have(Token.RPAREN):
            args=[]
        else:
            args = self.parse_args()
        self.must_be(Token.RPAREN, "Mismatched Parenthesis")

        return ParseNode(eval_call, [identifier, *args])


    def parse_decl(self):

        t = self.parse_type()
        if t == Token.INT:
            t = SymType.VAR_INT
        else:
            t = SymType.VAR_REAL

        name_token = self.lexer.cur_tok
        self.must_be(Token.IDENTIFIER)
        return (t, name_token.lex)


    def parse_type(self):

        if self.have(Token.REAL):
            return Token.REAL
        self.must_be(Token.INT, "Expected Type")
        return Token.INT
            

    def parse_args(self):
        result = [self.parse_expr()]
        while self.have(Token.COMMA):
            result.append(self.parse_expr())
        return result


    def parse_while(self):

        self.must_be(Token.WHILE)
        self.must_be(Token.LPAREN)
        condition = self.parse_expr()
        self.must_be(Token.RPAREN, "Mismatched Parenthesis")
        body = self.parse_body()

        return ParseNode(eval_while, [condition, body])


    def parse_if(self):

        self.must_be(Token.IF)
        self.must_be(Token.LPAREN)
        condition = self.parse_expr()
        self.must_be(Token.RPAREN)
        body = self.parse_body()

        return ParseNode(eval_if, [condition, body])


    def parse_body(self):

        if self.match(Token.BEGIN):
            return self.parse_block()
        else:
            return self.parse_statement()


    def parse_expr(self):
        left = self.parse_sum()
        return self.parse_expr2(left)


    def parse_expr2(self, left):

        first = (Token.LT, Token.LTE, Token.GT, Token.GTE, Token.EQUAL)
        result = left
        while self.match(first):
            if self.have(Token.LT):
                result = ParseNode(eval_lt, [result, self.parse_sum()])
            elif self.have(Token.LTE):
                result = ParseNode(eval_lte, [result, self.parse_sum()])
            elif self.have(Token.GT):
                result = ParseNode(eval_gt, [result, self.parse_sum()])
            elif self.have(Token.GTE):
                result = ParseNode(eval_gte, [result, self.parse_sum()])
            elif self.have(Token.EQUAL):
                result = ParseNode(eval_equal, [result, self.parse_sum()])
            left = result
        return result


    def parse_sum(self):

        result = self.parse_mul()

        # sum'
        first = (Token.PLUS, Token.MINUS)
        while self.match(first):
            if self.have(Token.PLUS):
                result = ParseNode(eval_plus, [result, self.parse_mul()])
            elif self.have(Token.MINUS):
                result = ParseNode(eval_minus, [result, self.parse_mul()])
        return result


    def parse_mul(self):

        result = self.parse_value()

        # mul'
        first = (Token.TIMES, Token.DIV)
        while self.match(first):
            if self.have(Token.TIMES):
                result = ParseNode(eval_times, [result, self.parse_value()])
            elif self.have(Token.DIV):
                result = ParseNode(eval_divide, [result, self.parse_value()])
        return result


    def parse_value(self):

        if self.match(Token.INTNUM):
            result = ParseNode(eval_number, [self.lexer.cur_tok.value])
            self.next()
            return result

        elif self.match(Token.REALNUM):
            result = ParseNode(eval_number, [self.lexer.cur_tok.value])
            self.next()
            return result

        elif self.match(Token.IDENTIFIER):
            identifier = self.lexer.cur_tok.lex
            self.next()

            # value'
            if self.have(Token.LPAREN):
                return self.parse_call2(identifier)
            return ParseNode(eval_identifier, [identifier])

        self.must_be(Token.LPAREN)
        result = self.parse_expr()
        self.must_be(Token.RPAREN, "Mismatched Parenthesis")
        return result

if __name__ == '__main__':
    import sys
    file = open(sys.argv[1])
    lexer = Lexer(file)
    parser = Parser(lexer)
    if not parser.parse():
        print("Parsing failed with %d errors."%(parser.errors))
