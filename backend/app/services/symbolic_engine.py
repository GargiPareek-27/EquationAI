# backend/app/services/symbolic_engine.py
import sympy
from app.models.schemas import SolutionPlan

SAFE_SYMPY_NAMES = {name: getattr(sympy, name) for name in dir(sympy) if not name.startswith("_")}

def clean_number(value):
    """Cleans a single numeric value: integer-valued floats become ints."""
    if isinstance(value, (sympy.Float, float)):
        if float(value) == int(float(value)):
            return sympy.Integer(int(float(value)))
        return round(float(value), 4)
    return value

def clean_result(value):
    """Recursively cleans numbers inside lists, tuples, and dicts, then stringifies.
    Also forces evaluation of lazy expressions and falls back to numerical
    approximation when a closed-form symbolic result can't be found."""
    try:
        if hasattr(value, "doit"):
            try:
                value = value.doit()
            except Exception:
                pass

        if isinstance(value, sympy.Basic) and value.has(sympy.Integral):
            try:
                numeric_value = value.evalf()
                if isinstance(numeric_value, sympy.Basic) and numeric_value.has(sympy.Integral):
                    raise ValueError("Still unevaluated after evalf()")
                return f"{clean_result(numeric_value)} (numerically approximated - closed-form not found)"
            except Exception:
                return str(value)

        if isinstance(value, (list, tuple)):
            cleaned = [clean_number(v) for v in value]
            return str(cleaned)
        elif isinstance(value, dict):
            cleaned = {k: clean_number(v) for k, v in value.items()}
            return str(cleaned)
        else:
            return str(clean_number(value))
    except Exception:
        return str(value)

def execute_plan(plan: SolutionPlan) -> SolutionPlan:
    safe_globals = {"__builtins__": {}}
    safe_globals.update(SAFE_SYMPY_NAMES)
    namespace = {}

    for step in plan.steps:
        code = step.sympy_expr.strip()
        try:
            exec(f"_result = ({code})", safe_globals, namespace)
            step.result = clean_result(namespace.get("_result"))
        except SyntaxError:
            try:
                keys_before = set(namespace.keys())
                exec(code, safe_globals, namespace)
                keys_after = set(namespace.keys())
                new_keys = keys_after - keys_before

                if new_keys:
                    assigned = {k: clean_result(namespace[k]) for k in new_keys}
                    step.result = str(assigned) if len(assigned) > 1 else list(assigned.values())[0]
                else:
                    step.result = "OK"
            except Exception as e:
                step.result = f"ERROR: {e}"
                break
        except Exception as e:
            step.result = f"ERROR: {e}"
            break

    return plan