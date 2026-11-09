"""Safe AST-based mathematical expression evaluator. Never uses eval()."""
import ast
import math
import operator
from decimal import Decimal, InvalidOperation

_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


class CalculationError(ValueError):
    """Raised when an expression is invalid or outside the supported domain."""


class SafeExpressionParser:
    def __init__(self, angle_mode="DEG"):
        self.angle_mode = angle_mode.upper()
        self.ans = 0.0
        self.functions = {
            "sqrt": math.sqrt, "cbrt": self._cbrt,
            "log": math.log10, "ln": math.log,
            "exp": math.exp, "abs": abs,
            "sin": self._sin, "cos": self._cos, "tan": self._tan,
            "asin": self._asin, "acos": self._acos, "atan": self._atan,
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "factorial": self._factorial,
        }
        self.constants = {"pi": math.pi, "e": math.e, "ans": 0.0}

    def set_angle_mode(self, mode):
        if mode not in ("DEG", "RAD"):
            raise CalculationError("Angle mode must be DEG or RAD.")
        self.angle_mode = mode

    def evaluate(self, expression):
        expression = expression.strip().replace("×", "*").replace("÷", "/").replace("−", "-")
        expression = expression.replace("^", "**")
        if not expression:
            raise CalculationError("Enter a calculation first.")
        try:
            tree = ast.parse(expression, mode="eval")
            self.constants["ans"] = self.ans
            result = self._visit(tree.body)
            if isinstance(result, complex):
                raise CalculationError("This operation does not have a real-number result.")
            if not math.isfinite(float(result)):
                raise CalculationError("The result is outside the supported numeric range.")
            self.ans = result
            return result
        except CalculationError:
            raise
        except ZeroDivisionError:
            raise CalculationError("Cannot divide by zero.")
        except (OverflowError, ValueError):
            raise CalculationError("The input is outside the valid range for this function.")
        except (SyntaxError, TypeError, KeyError):
            raise CalculationError("Invalid expression. Check the numbers and operators.")

    def _visit(self, node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in self.constants:
                return self.constants[node.id]
            raise CalculationError(f"Unknown constant: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            left, right = self._visit(node.left), self._visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10000:
                raise CalculationError("Exponent is too large.")
            return _BINARY[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
            return _UNARY[type(node.op)](self._visit(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in self.functions or node.keywords or len(node.args) != 1:
                raise CalculationError("Unsupported function or function arguments.")
            return self.functions[name](self._visit(node.args[0]))
        raise CalculationError("Only numbers, supported operators, constants and functions are allowed.")

    @staticmethod
    def _cbrt(x):
        return math.copysign(abs(x) ** (1 / 3), x)

    def _to_radians(self, x):
        return math.radians(x) if self.angle_mode == "DEG" else x

    def _from_radians(self, x):
        return math.degrees(x) if self.angle_mode == "DEG" else x

    def _sin(self, x): return math.sin(self._to_radians(x))
    def _cos(self, x): return math.cos(self._to_radians(x))
    def _tan(self, x):
        r = self._to_radians(x)
        if abs(math.cos(r)) < 1e-12:
            raise CalculationError("tan is undefined at this angle.")
        return math.tan(r)
    def _asin(self, x): return self._from_radians(math.asin(x))
    def _acos(self, x): return self._from_radians(math.acos(x))
    def _atan(self, x): return self._from_radians(math.atan(x))

    @staticmethod
    def _factorial(x):
        if not float(x).is_integer() or x < 0 or x > 170:
            raise CalculationError("Factorial requires an integer from 0 to 170.")
        return math.factorial(int(x))
