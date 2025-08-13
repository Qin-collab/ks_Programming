from typing import List, Optional, Union
from lexer import Token, TokenType, Lexer
from ast_nodes import *

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [token for token in tokens if token.type not in [TokenType.WHITESPACE, TokenType.NEWLINE]]
        self.current = 0

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()

        current_token = self.peek()
        raise ParseError(f"{message}. Got {current_token.type.value} at line {current_token.line}")

    def parse(self) -> Program:
        statements = []
        while not self.is_at_end():
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def declaration(self) -> Optional[Statement]:
        try:
            if self.match(TokenType.FUNC):
                return self.function_declaration()
            if self.match(TokenType.LET):
                return self.variable_declaration()
            return self.statement()
        except ParseError as e:
            self.synchronize()
            raise e

    def function_declaration(self) -> FunctionDeclaration:
        name = self.consume(TokenType.IDENTIFIER, "Expected function name").value

        self.consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        parameters = []

        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self.match(TokenType.COMMA):
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")

        self.consume(TokenType.LEFT_BRACE, "Expected '{' before function body")
        body = self.block_statement()

        return FunctionDeclaration(name, parameters, body)

    def variable_declaration(self) -> VariableDeclaration:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value

        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VariableDeclaration(name, initializer)

    def statement(self) -> Statement:
        if self.match(TokenType.GORUN):
            return self.gorun_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return self.block_statement()

        return self.expression_statement()

    def gorun_statement(self) -> GorunStatement:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'gorun'")
        expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after gorun expression")
        self.consume(TokenType.SEMICOLON, "Expected ';' after gorun statement")
        return GorunStatement(expr)

    def return_statement(self) -> ReturnStatement:
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after return statement")
        return ReturnStatement(value)

    def if_statement(self) -> IfStatement:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition")

        then_branch = self.statement()
        else_branch = None

        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return IfStatement(condition, then_branch, else_branch)

    def for_statement(self) -> ForStatement:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'")

        # 初始化器
        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.LET):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()

        # 条件
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after for loop condition")

        # 增量
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses")

        body = self.statement()
        return ForStatement(initializer, condition, increment, body)

    def while_statement(self) -> WhileStatement:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition")
        body = self.statement()
        return WhileStatement(condition, body)

    def block_statement(self) -> BlockStatement:
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        return BlockStatement(statements)

    def expression_statement(self) -> ExpressionStatement:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExpressionStatement(expr)

    def expression(self) -> Expression:
        return self.assignment()

    def assignment(self) -> Expression:
        expr = self.logical_or()

        if self.match(TokenType.ASSIGN):
            value = self.assignment()
            if isinstance(expr, IdentifierExpression):
                return AssignmentExpression(expr, value)
            raise ParseError("Invalid assignment target")

        return expr

    def logical_or(self) -> Expression:
        expr = self.logical_and()

        while self.match(TokenType.OR):
            operator = self.previous().value
            right = self.logical_and()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def logical_and(self) -> Expression:
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous().value
            right = self.equality()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def equality(self) -> Expression:
        expr = self.comparison()

        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.previous().value
            right = self.comparison()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def comparison(self) -> Expression:
        expr = self.term()

        while self.match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL, 
                         TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self.previous().value
            right = self.term()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def term(self) -> Expression:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous().value
            right = self.factor()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def factor(self) -> Expression:
        expr = self.unary()

        while self.match(TokenType.DIVIDE, TokenType.MULTIPLY, TokenType.MODULO):
            operator = self.previous().value
            right = self.unary()
            expr = BinaryExpression(expr, operator, right)

        return expr

    def unary(self) -> Expression:
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous().value
            right = self.unary()
            return UnaryExpression(operator, right)

        return self.call()

    def call(self) -> Expression:
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break

        return expr

    def finish_call(self, callee: Expression) -> CallExpression:
        arguments = []

        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                arguments.append(self.expression())

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        return CallExpression(callee, arguments)

    def primary(self) -> Expression:
        if self.match(TokenType.TRUE):
            return LiteralExpression(True, "boolean")

        if self.match(TokenType.FALSE):
            return LiteralExpression(False, "boolean")

        if self.match(TokenType.NUMBER):
            value = self.previous().value
            if '.' in value:
                return LiteralExpression(float(value), "number")
            else:
                return LiteralExpression(int(value), "number")

        if self.match(TokenType.STRING):
            return LiteralExpression(self.previous().value, "string")

        if self.match(TokenType.IDENTIFIER):
            return IdentifierExpression(self.previous().value)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr

        current_token = self.peek()
        raise ParseError(f"Unexpected token {current_token.type.value} at line {current_token.line}")

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in [TokenType.FUNC, TokenType.LET, TokenType.FOR,
                                   TokenType.IF, TokenType.WHILE, TokenType.GORUN,
                                   TokenType.RETURN]:
                return

            self.advance()
