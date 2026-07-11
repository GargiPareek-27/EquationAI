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

    executed_plan = execute_plan(plan)

    # TEMPORARY DEBUG: print full plan to terminal so we can see exactly what happened, even on failure
    print("\n\n===== FULL EXECUTED PLAN (DEBUG) =====")
    print(executed_plan.model_dump_json(indent=2))
    print("===== END DEBUG =====\n\n")

    verification = verify_plan_execution(executed_plan)

    if not verification.is_valid:
        detail = verification.reason
        if verification.mismatch_details:
            detail += f" | Details: {verification.mismatch_details}"
        raise HTTPException(status_code=500, detail=detail)

    return executed_plan