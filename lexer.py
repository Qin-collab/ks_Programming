import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # 字面量
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    IDENTIFIER = "IDENTIFIER"

    # 关键字
    LET = "LET"
    FUNC = "FUNC"
    IF = "IF"
    ELSE = "ELSE"
    FOR = "FOR"
    WHILE = "WHILE"
    RETURN = "RETURN"
    GORUN = "GORUN"
    TRUE = "TRUE"
    FALSE = "FALSE"

    # 运算符
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    ASSIGN = "ASSIGN"

    # 比较运算符
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"

    # 逻辑运算符
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    # 分隔符
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"

    # 特殊
    EOF = "EOF"
    NEWLINE = "NEWLINE"
    WHITESPACE = "WHITESPACE"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

        # 关键字映射
        self.keywords = {
            'let': TokenType.LET,
            'func': TokenType.FUNC,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'for': TokenType.FOR,
            'while': TokenType.WHILE,
            'return': TokenType.RETURN,
            'gorun': TokenType.GORUN,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
        }

        # 运算符映射
        self.operators = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '=': TokenType.ASSIGN,
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '&&': TokenType.AND,
            '||': TokenType.OR,
            '!': TokenType.NOT,
        }

        # 分隔符映射
        self.delimiters = {
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
        }

    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def peek_char(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def advance(self):
        if self.pos < len(self.text) and self.text[self.pos] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1

    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()

    def skip_comment(self):
        # 跳过单行注释 //
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()

    def read_number(self) -> Token:
        start_line, start_column = self.line, self.column
        number_str = ''

        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            number_str += self.current_char()
            self.advance()

        return Token(TokenType.NUMBER, number_str, start_line, start_column)

    def read_string(self) -> Token:
        start_line, start_column = self.line, self.column
        string_value = ''

        # 跳过开始的引号
        self.advance()

        while self.current_char() and self.current_char() != '"':
            if self.current_char() == '\\':
                self.advance()
                if self.current_char() in 'ntr\\"':
                    escape_chars = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"'}
                    string_value += escape_chars.get(self.current_char(), self.current_char())
                    self.advance()
                else:
                    string_value += self.current_char()
                    self.advance()
            else:
                string_value += self.current_char()
                self.advance()

        # 跳过结束的引号
        if self.current_char() == '"':
            self.advance()

        return Token(TokenType.STRING, string_value, start_line, start_column)

    def read_identifier(self) -> Token:
        start_line, start_column = self.line, self.column
        identifier = ''

        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            identifier += self.current_char()
            self.advance()

        # 检查是否为关键字
        token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
        if token_type == TokenType.TRUE or token_type == TokenType.FALSE:
            token_type = TokenType.BOOLEAN

        return Token(token_type, identifier, start_line, start_column)

    def read_operator(self) -> Token:
        start_line, start_column = self.line, self.column

        # 检查双字符运算符
        two_char = self.current_char() + (self.peek_char() or '')
        if two_char in self.operators:
            self.advance()
            self.advance()
            return Token(self.operators[two_char], two_char, start_line, start_column)

        # 单字符运算符
        char = self.current_char()
        if char in self.operators:
            self.advance()
            return Token(self.operators[char], char, start_line, start_column)

        raise SyntaxError(f"Unknown operator: {char} at line {self.line}, column {self.column}")

    def tokenize(self) -> List[Token]:
        self.tokens = []

        while self.pos < len(self.text):
            self.skip_whitespace()

            char = self.current_char()
            if not char:
                break

            # 跳过注释
            if char == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue

            # 换行符
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, char, self.line, self.column))
                self.advance()

            # 数字
            elif char.isdigit():
                self.tokens.append(self.read_number())

            # 字符串
            elif char == '"':
                self.tokens.append(self.read_string())

            # 标识符和关键字
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())

            # 分隔符
            elif char in self.delimiters:
                self.tokens.append(Token(self.delimiters[char], char, self.line, self.column))
                self.advance()

            # 运算符
            elif char in '+-*/%=<>!&|':
                self.tokens.append(self.read_operator())

            else:
                raise SyntaxError(f"Unexpected character: {char} at line {self.line}, column {self.column}")

        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
