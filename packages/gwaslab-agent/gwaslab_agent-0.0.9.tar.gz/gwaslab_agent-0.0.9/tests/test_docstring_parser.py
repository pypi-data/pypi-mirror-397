import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)
sys.path.insert(0, "/home/yunye/work/gwaslab/src")

from gwaslab_agent.g_docstring_parser import parse_numpy_style_params


def example_func():
    """
    Example function with parameters.

    Parameters
    ----------
    x : int, default=10
        Description of x with default.
    y : {"low", "medium", "high"}
        Description of y with enum.
    z : array-like
        Description of z with array type.

    Returns
    -------
    result : bool
        Description of return value.
    """
    pass


def multi_section_func():
    """
    Function with multiple parameter sections.

    Parameters
    ----------
    a : str
        Description of a.

    Less Used Parameters
    --------------------
    b : float or string, optional, default=None
        Description of b with union type and default.

    Parameters
    ----------
    c : int
        Description of c (repeated section).
    """
    pass


class TestDocstringParser(unittest.TestCase):
    def test_basic_parse(self):
        out = parse_numpy_style_params(example_func)
        params = out["parameters"]
        self.assertEqual(params["x"]["type"], "integer")
        self.assertEqual(params["x"]["default"], 10)
        self.assertEqual(params["y"]["type"], "string")
        self.assertEqual(params["y"]["enum"], ["low", "medium", "high"])
        self.assertEqual(params["z"]["type"], "array")
        self.assertIn("description", out)

    def test_multi_sections_and_required(self):
        out = parse_numpy_style_params(multi_section_func)
        params = out["parameters"]
        self.assertEqual(params["a"]["type"], "string")
        self.assertEqual(params["b"]["type"], "number")  # float or string -> prefers object, but code maps; ensure number present
        self.assertIn("required", params["b"])  # optional flag present
        self.assertEqual(params["b"]["default"], None)
        self.assertEqual(params["c"]["type"], "integer")


if __name__ == "__main__":
    unittest.main()
