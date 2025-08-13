from abc import ABC, abstractmethod
from typing import List, Any, Optional
from dataclasses import dataclass

# 抽象语法树基类
class ASTNode(ABC):
    pass

# 表达式基类
class Expression(ASTNode):
    pass

# 语句基类
class Statement(ASTNode):
    pass

# 字面量表达式
@dataclass
class LiteralExpression(Expression):
    value: Any
    type: str  # "number", "string", "boolean"

# 标识符表达式
@dataclass
class IdentifierExpression(Expression):
    name: str

# 二元运算表达式
@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression

# 一元运算表达式
@dataclass
class UnaryExpression(Expression):
    operator: str
    operand: Expression

# 函数调用表达式
@dataclass
class CallExpression(Expression):
    function: Expression
    arguments: List[Expression]

# 赋值表达式
@dataclass
class AssignmentExpression(Expression):
    target: IdentifierExpression
    value: Expression

# 变量声明语句
@dataclass
class VariableDeclaration(Statement):
    name: str
    initializer: Optional[Expression] = None

# 函数声明语句
@dataclass
class FunctionDeclaration(Statement):
    name: str
    parameters: List[str]
    body: 'BlockStatement'

# 表达式语句
@dataclass
class ExpressionStatement(Statement):
    expression: Expression

# 块语句
@dataclass
class BlockStatement(Statement):
    statements: List[Statement]

# if语句
@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement] = None

# for语句
@dataclass
class ForStatement(Statement):
    initializer: Optional[Statement]
    condition: Optional[Expression]
    increment: Optional[Expression]
    body: Statement

# while语句
@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: Statement

# return语句
@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression] = None

# gorun语句
@dataclass
class GorunStatement(Statement):
    expression: Expression

# 程序根节点
@dataclass
class Program(ASTNode):
    statements: List[Statement]

# AST访问者模式接口
class ASTVisitor(ABC):
    @abstractmethod
    def visit_literal(self, node: LiteralExpression) -> Any:
        pass

    @abstractmethod
    def visit_identifier(self, node: IdentifierExpression) -> Any:
        pass

    @abstractmethod
    def visit_binary(self, node: BinaryExpression) -> Any:
        pass

    @abstractmethod
    def visit_unary(self, node: UnaryExpression) -> Any:
        pass

    @abstractmethod
    def visit_call(self, node: CallExpression) -> Any:
        pass

    @abstractmethod
    def visit_assignment(self, node: AssignmentExpression) -> Any:
        pass

    @abstractmethod
    def visit_variable_declaration(self, node: VariableDeclaration) -> Any:
        pass

    @abstractmethod
    def visit_function_declaration(self, node: FunctionDeclaration) -> Any:
        pass

    @abstractmethod
    def visit_expression_statement(self, node: ExpressionStatement) -> Any:
        pass

    @abstractmethod
    def visit_block_statement(self, node: BlockStatement) -> Any:
        pass

    @abstractmethod
    def visit_if_statement(self, node: IfStatement) -> Any:
        pass

    @abstractmethod
    def visit_for_statement(self, node: ForStatement) -> Any:
        pass

    @abstractmethod
    def visit_while_statement(self, node: WhileStatement) -> Any:
        pass

    @abstractmethod
    def visit_return_statement(self, node: ReturnStatement) -> Any:
        pass

    @abstractmethod
    def visit_gorun_statement(self, node: GorunStatement) -> Any:
        pass

    @abstractmethod
    def visit_program(self, node: Program) -> Any:
        pass

# AST节点接受访问者的方法
def accept_visitor(node: ASTNode, visitor: ASTVisitor) -> Any:
    if isinstance(node, LiteralExpression):
        return visitor.visit_literal(node)
    elif isinstance(node, IdentifierExpression):
        return visitor.visit_identifier(node)
    elif isinstance(node, BinaryExpression):
        return visitor.visit_binary(node)
    elif isinstance(node, UnaryExpression):
        return visitor.visit_unary(node)
    elif isinstance(node, CallExpression):
        return visitor.visit_call(node)
    elif isinstance(node, AssignmentExpression):
        return visitor.visit_assignment(node)
    elif isinstance(node, VariableDeclaration):
        return visitor.visit_variable_declaration(node)
    elif isinstance(node, FunctionDeclaration):
        return visitor.visit_function_declaration(node)
    elif isinstance(node, ExpressionStatement):
        return visitor.visit_expression_statement(node)
    elif isinstance(node, BlockStatement):
        return visitor.visit_block_statement(node)
    elif isinstance(node, IfStatement):
        return visitor.visit_if_statement(node)
    elif isinstance(node, ForStatement):
        return visitor.visit_for_statement(node)
    elif isinstance(node, WhileStatement):
        return visitor.visit_while_statement(node)
    elif isinstance(node, ReturnStatement):
        return visitor.visit_return_statement(node)
    elif isinstance(node, GorunStatement):
        return visitor.visit_gorun_statement(node)
    elif isinstance(node, Program):
        return visitor.visit_program(node)
    else:
        raise NotImplementedError(f"Visitor not implemented for {type(node)}")
