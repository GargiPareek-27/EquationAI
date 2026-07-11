# backend/tests/test_symbolic_engine.py
from app.models.schemas import SolutionPlan, Step
from app.services.symbolic_engine import execute_plan

def test_simple_linear_equation():
    plan = SolutionPlan(
        problem_type="algebra",
        is_solvable=True,
        steps=[
            Step(step_id=1, description_latex="Define x", sympy_expr="x = symbols('x')", operation_type="define_variable"),
            Step(step_id=2, description_latex="Solve 3x+5=20", sympy_expr="solve(Eq(3*x+5, 20), x)", operation_type="solve", depends_on=[1]),
        ]
    )
    result = execute_plan(plan)
    assert result.steps[1].result == "[5]"
    
