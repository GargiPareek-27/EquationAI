# backend/app/services/llm_parser.py
import json
from google import genai
from google.genai import types
from app.config import settings
from app.models.schemas import SolutionPlan
from app.prompts.system_prompts import MATH_PARSER_SYSTEM_PROMPT

client = genai.Client(
    api_key=settings.gemini_api_key,
    http_options=types.HttpOptions(timeout=60000),  # milliseconds, not seconds
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "problem_type": {"type": "string"},
        "is_solvable": {"type": "boolean"},
        "clarification_needed": {"type": "string", "nullable": True},
        "variables": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "description": {"type": "string"},
                    "domain": {"type": "string", "nullable": True},
                },
                "required": ["symbol", "description"],
            },
        },
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_id": {"type": "integer"},
                    "description_latex": {"type": "string"},
                    "sympy_expr": {"type": "string"},
                    "operation_type": {"type": "string"},
                    "depends_on": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["step_id", "description_latex", "sympy_expr", "operation_type", "depends_on"],
            },
        },
        "final_answer_variable": {"type": "string", "nullable": True},
        "final_answer_units": {"type": "string", "nullable": True},
        "expected_final_answer_sympy": {"type": "string", "nullable": True},
    },
    "required": ["problem_type", "is_solvable", "variables", "steps"],
}

MODEL_NAME = settings.gemini_model_name


def _call_llm(problem_text: str, repair_note: str | None = None) -> str:
    """Makes one Gemini call. If repair_note is set, it's appended to the user
    content so the model can self-correct a previous malformed response."""
    contents = problem_text if repair_note is None else f"{problem_text}\n\n{repair_note}"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=MATH_PARSER_SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            max_output_tokens=8192,
        ),
    )

    finish_reason = response.candidates[0].finish_reason if response.candidates else None
    if finish_reason is not None and str(finish_reason) == "MAX_TOKENS":
        raise ValueError(
            "LLM response was truncated (hit max_output_tokens limit) before completing. "
            "This problem likely requires more steps than the token budget allows."
        )

    return response.text.strip()


def parse_problem_to_plan(problem_text: str) -> SolutionPlan:
    """Parses a problem into a SolutionPlan. On a malformed/unparseable first
    response, retries once with the exact parse error appended, giving the
    model a chance to self-correct before we give up."""
    raw_text = _call_llm(problem_text)

    try:
        plan_dict = json.loads(raw_text)
        return SolutionPlan(**plan_dict)
    except Exception as first_error:
        repair_note = (
            "SYSTEM: Your previous response could not be parsed as valid JSON "
            f"matching the required schema. Error: {first_error}. "
            "Re-emit ONLY the corrected JSON object, nothing else."
        )
        raw_text = _call_llm(problem_text, repair_note=repair_note)
        plan_dict = json.loads(raw_text)  # let this raise if the retry also fails
        return SolutionPlan(**plan_dict)