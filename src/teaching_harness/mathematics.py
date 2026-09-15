"""有限有理数算术；无 eval、名字解析或任意代码执行。"""

import ast
from fractions import Fraction


def calculate(expression: str) -> str:
    if len(expression) > 500:
        raise ValueError("表达式过长")
    tree = ast.parse(expression, mode="eval")
    if len(list(ast.walk(tree))) > 80:
        raise ValueError("表达式过于复杂")

    def walk(node: ast.AST, depth: int = 0) -> Fraction:
        if depth > 15:
            raise ValueError("表达式嵌套过深")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = Fraction(str(node.value))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = walk(node.operand, depth + 1) * (-1 if isinstance(node.op, ast.USub) else 1)
        elif isinstance(node, ast.BinOp):
            left, right = walk(node.left, depth + 1), walk(node.right, depth + 1)
            if isinstance(node.op, ast.Add):
                value = left + right
            elif isinstance(node.op, ast.Sub):
                value = left - right
            elif isinstance(node.op, ast.Mult):
                value = left * right
            elif isinstance(node.op, ast.Div):
                value = left / right
            elif isinstance(node.op, ast.Pow) and right.denominator == 1 and abs(right) <= 12:
                value = left ** int(right)
            else:
                raise ValueError("仅支持有限加减乘除与整数幂")
        else:
            raise ValueError("不支持变量、函数或代码")
        if value.numerator.bit_length() > 512 or value.denominator.bit_length() > 512:
            raise ValueError("计算超出数值范围")
        return value

    return str(walk(tree.body))
