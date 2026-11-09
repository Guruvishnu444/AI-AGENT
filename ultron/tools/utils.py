"""
Utility tools — data transformations, calculation engines, and text analytics.
"""

import ast
import json
import operator


# Allowed mathematical operators for safe evaluation
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type.__name__}")
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
    else:
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def register(mcp):

    @mcp.tool()
    def format_json(data: str) -> str:
        """Pretty-print and validate a JSON string with 2-space indentation."""
        try:
            parsed = json.loads(data)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError as exc:
            return f"Invalid JSON payload: {exc}"

    @mcp.tool()
    def word_count(text: str) -> dict:
        """Analyze text metrics: character count, word count, line count, and estimated reading time."""
        lines = text.splitlines()
        words = text.split()
        char_count = len(text)
        reading_time_min = round(len(words) / 200, 2)  # Avg 200 wpm
        return {
            "characters": char_count,
            "words": len(words),
            "lines": len(lines),
            "estimated_reading_minutes": reading_time_min,
        }

    @mcp.tool()
    def calculate_math(expression: str) -> str:
        """
        Safely calculate mathematical expressions (e.g., '(45 * 12) + 2**8 - 100/4').
        Protected against arbitrary code execution.
        """
        try:
            clean_expr = expression.strip()
            tree = ast.parse(clean_expr, mode='eval')
            result = _safe_eval(tree.body)
            return f"{clean_expr} = {result}"
        except Exception as exc:
            return f"Calculation failed: {exc}"
