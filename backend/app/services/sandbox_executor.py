# backend/app/services/sandbox_executor.py
"""
Executes untrusted, LLM-generated SymPy expressions.

KNOWN LIMITATION: restricting __builtins__ to a curated allowlist blocks
direct calls to dangerous builtins (open, __import__, eval, exec,
getattr, globals, etc.), but does not fully close Python's object-
introspection surface (e.g. reaching classes via attribute chains on
any object). This is a well-known class of Python sandbox escape. A
production deployment handling untrusted traffic should run this in a
subprocess/container boundary rather than relying on __builtins__
restriction alone, or use a real allowlist-based AST evaluator that
never calls exec()/eval() directly.

See backend/tests/test_sandbox_security.py for exactly what is and
isn't currently tested/blocked.

SAFE_BUILTINS exists because LLM-generated math code routinely and
legitimately needs ordinary Python builtins (min/max over a list of
solutions, sum over a series, abs, len, round, sorted) — these are
NOT security-relevant (no filesystem/network/process/import access),
so blocking them only breaks correct code without adding any real
protection. Deliberately excluded: __import__, open, eval, exec,
compile, getattr, setattr, delattr, vars, dir, globals, locals —
these are the actual introspection/execution primitives that matter.
"""
import sympy

SAFE_SYMPY_NAMES = {name: getattr(sympy, name) for name in dir(sympy) if not name.startswith("_")}

SAFE_BUILTINS = {
    "min": min,
    "max": max,
    "sum": sum,
    "abs": abs,
    "len": len,
    "round": round,
    "sorted": sorted,
    "list": list,
    "tuple": tuple,
    "dict": dict,
    "set": set,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


def run_in_sandbox(code: str, namespace: dict) -> None:
    """Executes `code` with a restricted builtins namespace (SAFE_BUILTINS
    only, no dangerous builtins) and SymPy names injected. Mutates
    `namespace` in place, matching exec()'s normal semantics."""
    safe_globals = {"__builtins__": SAFE_BUILTINS}
    safe_globals.update(SAFE_SYMPY_NAMES)
    exec(code, safe_globals, namespace)