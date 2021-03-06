from lexer import Lexer
from ast import Expr, AddExpr, MultExpr, UnaryMinus, IDExpr, IntLitExpr

class Parser:

    def __init__(self, fn: str):

        self.lex = Lexer(fn)
        self.tg = self.lex.token_generator()
        self.currtok = next(self.tg)

    """
        Expr  →  Term { (+ | -) Term }
        Term  → Fact { (* | / | %) Fact }
        Fact  → [ - ] Primary
        Primary  → ID | INTLIT | ( Expr )
        
        Recursive descent parser. Each non-terminal corresponds 
        to a function.
        
        -7  -(7 * 5)  -b   unary minus
    """

    def expr(self) -> Expr:
        """
        Expr  →  Term { + Term }
        """

        left = self.term()

        while self.currtok[0] in { Lexer.PLUS, Lexer.MINUS }:
            self.currtok = next(self.tg)  # advance to the next token
                                          # because we matched a +
            right = self.term()
            left = AddExpr(left,right)

        return left

    def term(self) -> Expr:
        """
        Term  → Fact { * Fact }
        """
        left = self.fact()

        while self.currtok[0] in { Lexer.MULT }:
            self.currtok = next(self.tg)
            right = self.fact()
            left = MultExpr(left, right)

        return left

    def fact(self) -> Expr:
        """
        Fact  → [ - ] Primary
            e.g., -a  -(b+c)  -6    (b+c) a 6
        """

        # only advance to the next token on a successful match.
        if self.currtok[0] == Lexer.MINUS:
            self.currtok = next(self.tg)
            tree = self.primary()
            return UnaryMinus(tree)

        return self.primary()

    def primary(self) -> Expr:
        """
        Primary  → ID | INTLIT | ( Expr )
        """

        # TODO Add real literals

        # parse an ID
        if self.currtok[0] == Lexer.ID:
            tmp = self.currtok
            self.currtok = next(self.tg)
            return IDExpr(tmp[1])

        # parse an integer literal
        if self.currtok[0] == Lexer.INTLIT:
            tmp = self.currtok
            self.currtok = next(self.tg)
            return IntLitExpr(tmp[1])

        # parse a parenthesized expression
        if self.currtok[0] == Lexer.LPAREN:
            self.currtok = next(self.tg)
            tree = self.expr()
            if self.currtok[0] == Lexer.RPAREN:
                self.currtok = next(self.tg)
                return tree
            else:
                # use the line number from your token object
                raise SLUCSyntaxError("ERROR: Missing right paren on line {0}".format(-1))

        # what if we get here we have a problem
        raise SLUCSyntaxError("ERROR: Unexpected token {0} on line {1}".format(self.currtok[1], -1))



# create our own exception by inheriting
# from Python's exception
class SLUCSyntaxError(Exception):
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message

if __name__ == '__main__':

    p = Parser('simple.c')
    t = p.expr()
    print(t)