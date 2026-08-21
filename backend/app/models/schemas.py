# backend/app/models/schemas.py
from pydantic import BaseModel
from typing import Optional, List


class Variable(BaseModel):
    symbol: str
    description: str
    domain: Optional[str] = None


class Step(BaseModel):
    step_id: int
    description_latex: str
    sympy_expr: str
    operation_type: str
    depends_on: List[int] = []
    result: Optional[str] = None


class SolutionPlan(BaseModel):
    problem_type: str
    is_solvable: bool
    clarification_needed: Optional[str] = None
    variables: List[Variable] = []
    steps: List[Step] = []
    final_answer_variable: Optional[str] = None
    final_answer_units: Optional[str] = None
    expected_final_answer_sympy: Optional[str] = None  # LLM's own claimed answer, as a sympy-parseable string
    verification_warning: Optional[str] = None  # set when the answer was computed successfully but the LLM's
    # independent self-check disagreed with it — answer is still shown, but flagged as lower-confidence


class ProblemRequest(BaseModel):
    problem_text: str