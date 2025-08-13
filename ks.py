#!/usr/bin/env python3
"""
KS语言编译器
用法: python ks.py <source_file.ks>
"""

import sys
import os
from pathlib import Path

from lexer import Lexer, TokenType
from parser import Parser, ParseError
from interpreter import Interpreter
from ast_nodes import accept_visitor

class KSCompiler:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False

    def compile_file(self, file_path: str):
        """编译并执行KS源文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source_code = file.read()

            self.run(source_code, file_path)

            if self.had_error:
                sys.exit(65)
            if self.had_runtime_error:
                sys.exit(70)

        except FileNotFoundError:
            print(f"错误: 找不到文件 '{file_path}'", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)

    def run_interactive(self):
        """交互式运行模式"""
        print("KS语言交互式解释器")
        print("输入 'exit' 退出")

        interpreter = Interpreter()

        while True:
            try:
                line = input("ks> ")
                if line.strip() == 'exit':
                    break

                if line.strip():
                    self.run(line, "<interactive>", interpreter)
                    self.had_error = False  # 重置错误状态

            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n再见!")
                break

    def run(self, source_code: str, file_name: str = "<script>", interpreter: Interpreter = None):
        """运行KS源代码"""
        try:
            # 词法分析
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()

            if self.had_error:
                return

            # 语法分析
            parser = Parser(tokens)
            ast = parser.parse()

            if self.had_error:
                return

            # 解释执行
            if interpreter is None:
                interpreter = Interpreter()

            success = interpreter.interpret(ast)
            if not success:
                self.had_runtime_error = True

        except ParseError as e:
            self.error(0, str(e))
        except Exception as e:
            self.error(0, f"意外错误: {e}")

    def error(self, line: int, message: str):
        """报告错误"""
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        """报告错误详情"""
        print(f"[行 {line}] 错误{where}: {message}", file=sys.stderr)
        self.had_error = True

    def show_tokens(self, file_path: str):
        """显示词法分析结果"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source_code = file.read()

            lexer = Lexer(source_code)
            tokens = lexer.tokenize()

            print("词法分析结果:")
            print("-" * 50)
            for token in tokens:
                if token.type != TokenType.EOF:
                    print(f"{token.type.value:<15} {token.value:<20} 行:{token.line} 列:{token.column}")

        except FileNotFoundError:
            print(f"错误: 找不到文件 '{file_path}'", file=sys.stderr)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)

    def show_ast(self, file_path: str):
        """显示抽象语法树"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source_code = file.read()

            lexer = Lexer(source_code)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            ast = parser.parse()

            print("抽象语法树:")
            print("-" * 50)
            self.print_ast(ast, 0)

        except ParseError as e:
            print(f"语法错误: {e}", file=sys.stderr)
        except FileNotFoundError:
            print(f"错误: 找不到文件 '{file_path}'", file=sys.stderr)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)

    def print_ast(self, node, indent: int):
        """递归打印AST节点"""
        indent_str = "  " * indent
        print(f"{indent_str}{type(node).__name__}")

        for field_name, field_value in node.__dict__.items():
            if isinstance(field_value, list):
                if field_value:
                    print(f"{indent_str}  {field_name}:")
                    for item in field_value:
                        if hasattr(item, '__dict__'):
                            self.print_ast(item, indent + 2)
                        else:
                            print(f"{indent_str}    {item}")
            elif hasattr(field_value, '__dict__'):
                print(f"{indent_str}  {field_name}:")
                self.print_ast(field_value, indent + 2)
            elif field_value is not None:
                print(f"{indent_str}  {field_name}: {field_value}")

def main():
    compiler = KSCompiler()

    if len(sys.argv) == 1:
        # 交互模式
        compiler.run_interactive()
    elif len(sys.argv) == 2:
        # 编译文件
        file_path = sys.argv[1]
        if not file_path.endswith('.ks'):
            print("错误: 文件必须具有 .ks 扩展名", file=sys.stderr)
            sys.exit(1)

        compiler.compile_file(file_path)
    elif len(sys.argv) == 3:
        # 特殊选项
        option = sys.argv[1]
        file_path = sys.argv[2]

        if option == "--tokens":
            compiler.show_tokens(file_path)
        elif option == "--ast":
            compiler.show_ast(file_path)
        else:
            print("用法: python ks.py [--tokens|--ast] <file.ks>", file=sys.stderr)
            sys.exit(1)
    else:
        print("用法: python ks.py [--tokens|--ast] <file.ks>", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
