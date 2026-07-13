# backend/app/services/llm_parser.py
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.models.schemas import SolutionPlan
from app.prompts.system_prompts import MATH_PARSER_SYSTEM_PROMPT

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
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

MODEL_NAME = "gemini-2.5-flash"


def parse_problem_to_plan(problem_text: str) -> SolutionPlan:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=problem_text,
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

    raw_text = response.text.strip()
    plan_dict = json.loads(raw_text)
    return SolutionPlan(**plan_dict)