
import re


class StrTool:
    _NON_WORD_PATTERN = re.compile(r"[^a-zA-Z0-9]")
    _FURMULA_PATTERN = r'^[\w\s\.\+\-\*\/\(\)\'"]+$'
    _EXCEPTION = ["()"]
    _SAFE_EVAL_SCOPE = {
        '__builtins__': None,
        'int': int,
        'str': str
    }

    @classmethod
    def to_py_field(cls, src_field):
        return cls._NON_WORD_PATTERN.sub("_", src_field)

    @classmethod
    def safe_eval(cls, expr):
        if not re.fullmatch(cls._FURMULA_PATTERN, expr):
            raise ValueError("unsafe expression: {}".format(expr))
        for k in cls._EXCEPTION:
            if k in expr:
                raise ValueError("unsafe expression: {}".format(expr))
        return str(eval(expr, cls._SAFE_EVAL_SCOPE))
