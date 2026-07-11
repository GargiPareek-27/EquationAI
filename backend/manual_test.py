# backend/manual_test.py
from app.services.llm_parser import parse_problem_to_plan
from app.services.symbolic_engine import execute_plan
from app.services.verifier import verify_plan_execution

problem = "Sara has 3 times as many apples as Tom. Together they have 20 apples. How many apples does Sara have?"

plan = parse_problem_to_plan(problem)
print("--- RAW PLAN FROM LLM ---")
print(plan.model_dump_json(indent=2))

executed_plan = execute_plan(plan)
print("\n--- AFTER SYMPY EXECUTION ---")
print(executed_plan.model_dump_json(indent=2))

verification = verify_plan_execution(executed_plan)
print(f"\n--- VERIFICATION: {verification.is_valid} — {verification.reason} ---")