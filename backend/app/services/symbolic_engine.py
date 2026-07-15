# backend/app/services/symbolic_engine.py — update clean_result only, keep everything else identical
def clean_result(value):
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
            except Exception as e:
                # TEMPORARY: expose the actual error instead of silently hiding it,
                # so we can see exactly why evalf() failed in production.
                return f"{str(value)} [DEBUG: evalf failed with: {type(e).__name__}: {e}]"

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