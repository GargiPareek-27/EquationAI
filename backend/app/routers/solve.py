# backend/app/routers/solve.py
from fastapi import APIRouter, HTTPException, Request
from google.genai.errors import ClientError
from app.models.schemas import ProblemRequest, SolutionPlan
from app.services.llm_parser import parse_problem_to_plan
from app.services.symbolic_engine import execute_plan
from app.services.verifier import verify_plan_execution
from app.rate_limiter import limiter

router = APIRouter()

# Rate limit chosen for a portfolio demo, not production traffic: the
# underlying Gemini free-tier key has a hard daily cap (as low as 20
# requests/day on some projects), so this exists primarily to stop one
# visitor from exhausting the entire day's quota by themselves, not to
# handle real scale.
@router.post("/solve", response_model=SolutionPlan)
@limiter.limit("5/hour")
def solve_problem(request: Request, payload: ProblemRequest):
    try:
        plan = parse_problem_to_plan(payload.problem_text)
    except ClientError as e:
        error_text = str(e)
        if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text:
            raise HTTPException(
                status_code=503,
                detail=(
                    "This demo runs on a free-tier Gemini API quota that resets daily. "
                    "The daily limit has been reached for now — please try again tomorrow, "
                    "or view the source code and architecture notes on GitHub in the meantime."
                ),
            )
        raise HTTPException(status_code=502, detail=f"LLM request failed: {error_text}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"LLM parsing failed: {e}")

    if not plan.is_solvable:
        return plan

    executed_plan = execute_plan(plan)
    verification = verify_plan_execution(executed_plan)

    if not verification.is_valid:
        if verification.hard_failure:
            detail = verification.reason
            if verification.mismatch_details:
                detail += f" | Details: {verification.mismatch_details}"
            raise HTTPException(status_code=500, detail=detail)
        else:
            warning = verification.reason
            if verification.mismatch_details:
                warning += f" | {verification.mismatch_details}"
            executed_plan.verification_warning = warning
            return executed_plan

    return executed_plan