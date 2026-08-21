# backend/app/routers/solve.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import ProblemRequest, SolutionPlan
from app.services.llm_parser import parse_problem_to_plan
from app.services.symbolic_engine import execute_plan
from app.services.verifier import verify_plan_execution

router = APIRouter()


@router.post("/solve", response_model=SolutionPlan)
def solve_problem(request: ProblemRequest):
    try:
        plan = parse_problem_to_plan(request.problem_text)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"LLM parsing failed: {e}")

    # If the LLM correctly identified the problem as unsolvable/ambiguous,
    # this is NOT an error — return it as a normal 200 response so the frontend
    # can display the clarification message nicely, instead of as a scary error.
    if not plan.is_solvable:
        return plan

    executed_plan = execute_plan(plan)
    verification = verify_plan_execution(executed_plan)

    if not verification.is_valid:
        if verification.hard_failure:
            # No usable answer exists at all (execution genuinely crashed,
            # or nothing was generated) — this really is a hard error.
            detail = verification.reason
            if verification.mismatch_details:
                detail += f" | Details: {verification.mismatch_details}"
            raise HTTPException(status_code=500, detail=detail)
        else:
            # The engine DID produce a real answer — the LLM's own separate
            # self-check just disagreed with it. Don't discard a correct
            # computation because of that; surface it with a warning so the
            # user (and you, during eval review) can see both the answer
            # and the fact that confidence is reduced.
            warning = verification.reason
            if verification.mismatch_details:
                warning += f" | {verification.mismatch_details}"
            executed_plan.verification_warning = warning
            return executed_plan

    return executed_plan