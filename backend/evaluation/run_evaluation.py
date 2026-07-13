# backend/evaluation/run_evaluation.py
import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.llm_parser import parse_problem_to_plan
from app.services.symbolic_engine import execute_plan
from app.services.verifier import verify_plan_execution
from evaluation.test_problems import TEST_PROBLEMS

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
DELAY_BETWEEN_CALLS_SECONDS = 5


def load_existing_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_results(results):
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)


def run_single_test(test_case):
    problem_text = test_case["problem"]
    try:
        plan = parse_problem_to_plan(problem_text)
        executed_plan = execute_plan(plan)
        verification = verify_plan_execution(executed_plan)

        last_result = executed_plan.steps[-1].result if executed_plan.steps else None
        expected = test_case["expected_answer"]
        expect_unsolvable = test_case.get("expect_unsolvable", False)

        if expect_unsolvable:
            test_passed = not executed_plan.is_solvable
            needs_manual_review = False
        elif expected is not None:
            test_passed = verification.is_valid
            needs_manual_review = False
        else:
            test_passed = None
            needs_manual_review = True

        result = {
            "id": test_case["id"],
            "category": test_case["category"],
            "problem": problem_text,
            "expected_answer": expected,
            "is_solvable": executed_plan.is_solvable,
            "final_result": last_result,
            "verification_passed": verification.is_valid,
            "verification_reason": verification.reason,
            "mismatch_details": verification.mismatch_details,
            "test_passed": test_passed,
            "needs_manual_review": needs_manual_review,
            "status": "COMPLETED",
            "timestamp": datetime.now().isoformat(),
        }

        if not verification.is_valid:
            result["full_plan_debug"] = executed_plan.model_dump()

        return result
    except Exception as e:
        return {
            "id": test_case["id"],
            "category": test_case["category"],
            "problem": problem_text,
            "expected_answer": test_case["expected_answer"],
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def compute_test_passed(result, test_case_lookup):
    if "test_passed" in result:
        return result["test_passed"]
    if result["status"] != "COMPLETED":
        return False
    test_case = test_case_lookup.get(result["id"])
    if test_case and test_case.get("expect_unsolvable"):
        return not result.get("is_solvable", True)
    if test_case and test_case["expected_answer"] is None:
        return None  # needs manual review, old format
    return result.get("verification_passed", False)


def run_evaluation():
    results = load_existing_results()
    completed_ids = {k for k, v in results.items() if v.get("status") == "COMPLETED"}
    remaining = [t for t in TEST_PROBLEMS if t["id"] not in completed_ids]

    if not remaining:
        print("All test cases already completed successfully.")
    else:
        print(f"Running {len(remaining)} remaining/errored test case(s) out of {len(TEST_PROBLEMS)} total...\n")

    for i, test_case in enumerate(remaining):
        print(f"[{i+1}/{len(remaining)}] Running: {test_case['id']} ({test_case['category']})...")
        result = run_single_test(test_case)
        results[test_case["id"]] = result
        save_results(results)

        if result["status"] == "ERROR" and "429" in result.get("error", ""):
            print(f"\n⚠️  Rate limit hit at test {test_case['id']}. Progress saved.")
            print(f"Run this script again later to resume from here.\n")
            break

        print(f"    Status: {result['status']}")
        if result["status"] == "COMPLETED":
            if result.get("needs_manual_review"):
                print(f"    Solvable: {result['is_solvable']} | NEEDS MANUAL REVIEW — check final_result: {result['final_result']}")
            else:
                print(f"    Solvable: {result['is_solvable']} | Test passed: {result['test_passed']}")
        else:
            print(f"    Error: {result.get('error', 'unknown')[:150]}")
        time.sleep(DELAY_BETWEEN_CALLS_SECONDS)

    print_summary(results)


def print_summary(results):
    test_case_lookup = {t["id"]: t for t in TEST_PROBLEMS}

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    total = len(results)
    completed = [r for r in results.values() if r["status"] == "COMPLETED"]
    errored = [r for r in results.values() if r["status"] == "ERROR"]

    auto_scored = [r for r in completed if not r.get("needs_manual_review")]
    manual_review = [r for r in completed if r.get("needs_manual_review")]
    auto_passed = [r for r in auto_scored if compute_test_passed(r, test_case_lookup)]

    print(f"Total test cases: {total}")
    print(f"Completed: {len(completed)} | Errored: {len(errored)}")
    print(f"Auto-scored, passed: {len(auto_passed)}/{len(auto_scored)}")
    print(f"Needs manual review (multiple valid answer formats): {len(manual_review)}")
    if manual_review:
        print("  -> " + ", ".join(r["id"] for r in manual_review))

    print("\nBy category:")
    categories = set(r["category"] for r in results.values())
    for cat in sorted(categories):
        cat_results = [r for r in results.values() if r["category"] == cat]
        cat_auto = [r for r in cat_results if r["status"] == "COMPLETED" and not r.get("needs_manual_review")]
        cat_passed = [r for r in cat_auto if compute_test_passed(r, test_case_lookup)]
        cat_manual = [r for r in cat_results if r.get("needs_manual_review")]
        print(f"  {cat}: {len(cat_passed)}/{len(cat_auto)} passed" + (f" (+{len(cat_manual)} manual review)" if cat_manual else ""))

    print("\nDetailed results saved to:", RESULTS_FILE)
    print("=" * 60)


if __name__ == "__main__":
    run_evaluation()