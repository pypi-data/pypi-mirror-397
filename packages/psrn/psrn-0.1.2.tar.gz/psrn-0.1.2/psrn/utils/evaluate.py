import numpy as np
import sympy
import math

from .exprutils import time_limit

def get_sympy_complexity(expr_str):
    complexity_dict = {
        "ADD": 1,
        "SUB": 1,
        "MUL": 1,
        "DIV": 2,
        "POW": 2,
        "SIN": 3,
        "COS": 3,
        "TAN": 3,
        "EXP": 3,
        "LOG": 3,
        "SQRT": 3,
        "NEG": 1,
        "ABS": 4,
        "TANH": 2,
        "SINH": 3,
        "COSH": 2,
        "INV": 2,
        "SIGN": 4,
    }
    try:
        with time_limit(1, "sleep"):
            expr = sympy.sympify(expr_str)
            ops_visual = sympy.count_ops(expr, visual=True)
            ops_visual_str = str(ops_visual)
            complexity = eval(ops_visual_str, complexity_dict)
            return complexity
    except Exception as e:
        print('ERR in get_sympy_complexity:', e)
        return 1e99


def get_reward(eta, complexity, mse):
    return (eta**complexity) / (1 + math.sqrt(mse))

