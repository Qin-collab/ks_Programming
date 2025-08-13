from typing import Any, Dict, List, Optional, Callable
from ast_nodes import *
import sys

class KSRuntimeError(Exception):
    pass

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.variables: Dict[str, Any] = {}
        self.parent = parent

    def define(self, name: str, value: Any):
        self.variables[name] = value

    def get(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise KSRuntimeError(f"Undefined variable '{name}'")

    def assign(self, name: str, value: Any):
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            try:
                self.parent.assign(name, value)
                return
            except KSRuntimeError:
                pass
        raise KSRuntimeError(f"Undefined variable '{name}'")

class KSFunction:
    def __init__(self, declaration: FunctionDeclaration, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        # 创建新的函数作用域
        environment = Environment(self.closure)

        # 绑定参数
        for i, param in enumerate(self.declaration.parameters):
            if i < len(arguments):
                environment.define(param, arguments[i])
            else:
                environment.define(param, None)

        try:
            interpreter.execute_block(self.declaration.body.statements, environment)
        except ReturnValue as return_value:
            return return_value.value

        return None

class ReturnValue(Exception):
    def __init__(self, value: Any):
        self.value = value

class Interpreter(ASTVisitor):
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals

        # 内置函数
        self.define_native_functions()

    def define_native_functions(self):
        pass  # print 已经在语法中作为语句处理

    def interpret(self, program: Program):
        try:
            self.visit_program(program)
        except KSRuntimeError as e:
            print(f"Runtime Error: {e}", file=sys.stderr)
            return False
        return True

    def execute(self, stmt: Statement):
        return accept_visitor(stmt, self)

    def evaluate(self, expr: Expression) -> Any:
        return accept_visitor(expr, self)

    def execute_block(self, statements: List[Statement], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_literal(self, node: LiteralExpression) -> Any:
        return node.value

    def visit_identifier(self, node: IdentifierExpression) -> Any:
        return self.environment.get(node.name)

    def visit_binary(self, node: BinaryExpression) -> Any:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        if node.operator == '+':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif node.operator == '-':
            return left - right
        elif node.operator == '*':
            return left * right
        elif node.operator == '/':
            if right == 0:
                raise KSRuntimeError("Division by zero")
            return left / right
        elif node.operator == '%':
            return left % right
        elif node.operator == '==':
            return left == right
        elif node.operator == '!=':
            return left != right
        elif node.operator == '<':
            return left < right
        elif node.operator == '>':
            return left > right
        elif node.operator == '<=':
            return left <= right
        elif node.operator == '>=':
            return left >= right
        elif node.operator == '&&':
            return self.is_truthy(left) and self.is_truthy(right)
        elif node.operator == '||':
            return self.is_truthy(left) or self.is_truthy(right)
        else:
            raise KSRuntimeError(f"Unknown binary operator: {node.operator}")

    def visit_unary(self, node: UnaryExpression) -> Any:
        operand = self.evaluate(node.operand)

        if node.operator == '-':
            return -operand
        elif node.operator == '!':
            return not self.is_truthy(operand)
        else:
            raise KSRuntimeError(f"Unknown unary operator: {node.operator}")

    def visit_call(self, node: CallExpression) -> Any:
        callee = self.evaluate(node.function)

        arguments = []
        for arg in node.arguments:
            arguments.append(self.evaluate(arg))

        if isinstance(callee, KSFunction):
            if len(arguments) != len(callee.declaration.parameters):
                raise KSRuntimeError(f"Expected {len(callee.declaration.parameters)} arguments but got {len(arguments)}")
            return callee.call(self, arguments)
        else:
            raise KSRuntimeError("Can only call functions")

    def visit_assignment(self, node: AssignmentExpression) -> Any:
        value = self.evaluate(node.value)
        self.environment.assign(node.target.name, value)
        return value

    def visit_variable_declaration(self, node: VariableDeclaration) -> Any:
        value = None
        if node.initializer:
            value = self.evaluate(node.initializer)

        self.environment.define(node.name, value)
        return None

    def visit_function_declaration(self, node: FunctionDeclaration) -> Any:
        function = KSFunction(node, self.environment)
        self.environment.define(node.name, function)
        return None

    def visit_expression_statement(self, node: ExpressionStatement) -> Any:
        return self.evaluate(node.expression)

    def visit_block_statement(self, node: BlockStatement) -> Any:
        self.execute_block(node.statements, Environment(self.environment))
        return None

    def visit_if_statement(self, node: IfStatement) -> Any:
        condition_value = self.evaluate(node.condition)

        if self.is_truthy(condition_value):
            self.execute(node.then_branch)
        elif node.else_branch:
            self.execute(node.else_branch)

        return None

    def visit_for_statement(self, node: ForStatement) -> Any:
        # 创建新的作用域用于for循环
        environment = Environment(self.environment)
        previous = self.environment

        try:
            self.environment = environment

            # 初始化
            if node.initializer:
                self.execute(node.initializer)

            # 循环
            while True:
                # 检查条件
                if node.condition:
                    condition_value = self.evaluate(node.condition)
                    if not self.is_truthy(condition_value):
                        break

                # 执行循环体
                self.execute(node.body)

                # 增量
                if node.increment:
                    self.evaluate(node.increment)
        finally:
            self.environment = previous

        return None

    def visit_while_statement(self, node: WhileStatement) -> Any:
        while self.is_truthy(self.evaluate(node.condition)):
            self.execute(node.body)
        return None

    def visit_return_statement(self, node: ReturnStatement) -> Any:
        value = None
        if node.value:
            value = self.evaluate(node.value)

        raise ReturnValue(value)

    def visit_gorun_statement(self, node: GorunStatement) -> Any:
        value = self.evaluate(node.expression)
        print(self.stringify(value))
        return None

    def visit_program(self, node: Program) -> Any:
        for statement in node.statements:
            self.execute(statement)
        return None

    def is_truthy(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    def stringify(self, value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(value)
