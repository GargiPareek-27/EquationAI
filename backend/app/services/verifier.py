# backend/app/services/verifier.py
import sympy
from app.models.schemas import SolutionPlan


class VerificationResult:
    def __init__(
        self,
        is_valid: bool,
        reason: str = "",
        mismatch_details: str | None = None,
        hard_failure: bool = True,
    ):
        self.is_valid = is_valid
        self.reason = reason
        self.mismatch_details = mismatch_details
        # hard_failure=True means there is no usable computed answer at all
        # (execution genuinely crashed, or the plan was never solvable).
        # hard_failure=False means the engine DID produce a real answer, but
        # the LLM's independent self-check disagreed with it — the answer
        # should still be shown to the user, just flagged with reduced
        # confidence, rather than discarded.
        self.hard_failure = hard_failure


SAFE_SYMPY_NAMES = {name: getattr(sympy, name) for name in dir(sympy) if not name.startswith("_")}
APPROXIMATION_SUFFIX = " (numerically approximated - closed-form not found)"


def _parse_safely(expr_str: str):
    return sympy.sympify(expr_str)


def _strip_approximation_suffix(result_str: str) -> str:
    if result_str.endswith(APPROXIMATION_SUFFIX):
        return result_str[: -len(APPROXIMATION_SUFFIX)]
    return result_str


def _extract_comparable(value):
    """For equation objects, compare lhs - rhs. Otherwise, use the value itself."""
    if isinstance(value, sympy.Equality):
        return value.lhs - value.rhs
    return value


def _values_match(executed_value, expected_value):
    """Checks whether two sympy values represent the same answer.
    Tries numeric comparison first (works for plain numbers, with tolerance
    for rounding/approximation). Falls back to symbolic equality checking
    when the expression contains free variables (e.g. general solutions,
    line equations, indefinite integrals) that can't be reduced to a number."""
    executed_comp = _extract_comparable(executed_value)
    expected_comp = _extract_comparable(expected_value)

    # Path 1: try pure numeric comparison (fast, precise, handles rounding)
    try:
        executed_numeric = complex(sympy.N(executed_comp))
        expected_numeric = complex(sympy.N(expected_comp))
        return abs(executed_numeric - expected_numeric) <= 1e-3
    except TypeError:
        pass  # contains free symbols — fall through to symbolic comparison

    # Path 2: symbolic equality — simplify the difference and check it's exactly zero.
    # This correctly handles expressions with free variables (x, y, C1, C2, etc.)
    try:
        difference = sympy.simplify(executed_comp - expected_comp)
        return difference == 0
    except Exception:
        # As a last resort, try sympy's .equals() which can catch some cases
        # simplify() alone might miss (e.g. certain trig/log equivalences).
        try:
            return bool(executed_comp.equals(expected_comp))
        except Exception:
            return False


def verify_plan_execution(plan: SolutionPlan) -> VerificationResult:
    if not plan.is_solvable:
        return VerificationResult(False, f"Marked unsolvable: {plan.clarification_needed}", hard_failure=True)
    if not plan.steps:
        return VerificationResult(False, "No steps were generated.", hard_failure=True)

    last_step = plan.steps[-1]
    if last_step.result is None or last_step.result.startswith("ERROR"):
        return VerificationResult(
            False,
            f"Execution failed at step {last_step.step_id}: {last_step.result}",
            hard_failure=True,
        )

    if plan.expected_final_answer_sympy:
        try:
            executed_str = _strip_approximation_suffix(last_step.result)
            executed_value = _parse_safely(executed_str)
            expected_value = _parse_safely(plan.expected_final_answer_sympy)

            if isinstance(executed_value, list) and len(executed_value) == 1:
                executed_value = executed_value[0]

            if not _values_match(executed_value, expected_value):
                # SOFT failure: the engine produced a real, executed answer.
                # The mismatch is between that answer and the LLM's own
                # separate, independent guess — which itself might be the
                # thing that's wrong (this is exactly the failure mode this
                # check exists to catch). Don't discard a real computed
                # result; surface it with a confidence warning instead.
                return VerificationResult(
                    False,
                    "Mismatch between LLM's stated answer and the deterministically executed result.",
                    mismatch_details=f"LLM claimed: {plan.expected_final_answer_sympy} | Engine computed: {executed_str}",
                    hard_failure=False,
                )
        except Exception as e:
            # SOFT failure: couldn't compare (parsing issue), but the engine's
            # answer still exists and may well be correct — surface it with
            # a warning rather than hiding it.
            return VerificationResult(
                False,
                "Could not verify LLM's claimed answer against engine output (parsing error).",
                mismatch_details=str(e),
                hard_failure=False,
            )

    return VerificationResult(True, "All steps executed successfully and final answer matches LLM's independent claim.")