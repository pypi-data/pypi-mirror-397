
import pytest
from kytchen.repl.sandbox import REPLEnvironment, SecurityError

def test_format_exploit_prevention():
    """Test that format() method cannot be used to bypass sandbox."""
    env = REPLEnvironment(context="test")

    # Try to access __globals__ via format string
    code = """
def f(): pass
print("{0.__globals__}".format(f))
"""
    res = env.execute(code)
    assert res.error is not None
    assert "Use of 'format' method is not allowed" in res.error

def test_format_map_exploit_prevention():
    """Test that format_map() method cannot be used to bypass sandbox."""
    env = REPLEnvironment(context="test")

    code = """
def f(): pass
print("{x.__globals__}".format_map({"x": f}))
"""
    res = env.execute(code)
    assert res.error is not None
    assert "Use of 'format_map' method is not allowed" in res.error

def test_fstring_still_works():
    """Test that f-strings still work (as they are checked by AST separately)."""
    env = REPLEnvironment(context="test")

    code = """
x = 10
print(f"Value: {x}")
"""
    res = env.execute(code)
    assert res.error is None
    assert "Value: 10" in res.stdout

def test_format_builtin_removed():
    """Test that format builtin is removed."""
    env = REPLEnvironment(context="test")

    code = """
print(format(10, "x"))
"""
    # Should raise NameError because format is not in builtins
    res = env.execute(code)
    assert res.error is not None
    assert "name 'format' is not defined" in str(res.error) or "Use of name 'format' is not allowed" in str(res.error)
