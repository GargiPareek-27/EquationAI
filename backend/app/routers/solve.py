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
        # This IS a genuine failure (execution crashed, or LLM's answer didn't
        # match the engine's computed result) — a real error worth flagging distinctly.
        detail = verification.reason
        if verification.mismatch_details:
            detail += f" | Details: {verification.mismatch_details}"
        raise HTTPException(status_code=500, detail=detail)

    return executed_plan