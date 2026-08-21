# backend/tests/test_sandbox_security.py
"""
Tests for the sandbox executor's restricted-builtins boundary.

IMPORTANT: these tests confirm that *direct builtin access* is blocked.
They do NOT prove the sandbox is escape-proof — Python's object
introspection surface (walking __class__/__subclasses__ chains) is a
known, publicly documented way to reach dangerous classes without ever
calling a builtin function. That gap is not closed here; see the
module docstring in sandbox_executor.py. Closing it fully requires a
process/container boundary or an AST-allowlist evaluator, not more
tests against this implementation.
"""
import pytest
from app.services.sandbox_executor import run_in_sandbox


def test_blocks_import():
    with pytest.raises(NameError):
        run_in_sandbox("_result = __import__('os')", {})


def test_blocks_open():
    with pytest.raises(NameError):
        run_in_sandbox("_result = open('/etc/passwd')", {})


def test_blocks_eval():
    with pytest.raises(NameError):
        run_in_sandbox("_result = eval('1+1')", {})


def test_allows_sympy_solve():
    import sympy
    x = sympy.symbols("x")
    ns = {"x": x}
    run_in_sandbox("_result = solve(x**2 - 4, x)", ns)
    assert set(ns["_result"]) == {-2, 2}


def test_allows_sympy_integrate():
    import sympy
    x = sympy.symbols("x")
    ns = {"x": x}
    run_in_sandbox("_result = integrate(x, x)", ns)
    assert ns["_result"] == sympy.Rational(1, 2) * x**2