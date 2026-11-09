from .parser import SafeExpressionParser, CalculationError


class CalculatorEngine:
    def __init__(self):
        self.parser = SafeExpressionParser("DEG")

    @property
    def angle_mode(self):
        return self.parser.angle_mode

    def set_angle_mode(self, mode):
        self.parser.set_angle_mode(mode)

    def calculate(self, expression):
        return self.parser.evaluate(expression)

    @property
    def answer(self):
        return self.parser.ans
