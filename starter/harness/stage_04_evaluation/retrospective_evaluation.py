"""Loop 02 component: make a separate model call that reviews finished evidence."""

from __future__ import annotations

import json
from typing import Any


REQUIRED_KEYS = {
    "task_status",
    "efficiency_score",
    "critique",
    "systemic_failure_root_cause",
    "workflow_adjustments",
}

ALLOWED_TASK_STATUSES = {"SUCCESS", "FAILED", "PARTIAL_SUCCESS"}

EVALUATION_INSTRUCTIONS = """
You are a retrospective evaluator for a completed Vehicle EDA harness run.
Judge the run using ONLY the supplied evidence object. Do not invent tool
results, dataset values, or private model reasoning.

Evaluate:
1. Goal fulfillment against the original prompt.
2. Loop or stall behavior visible in the execution_trace.
3. Tool efficiency visible in the tool_run_log (avoidable repeats, missing
   needed calls, or useful focused calls).
4. Whether the logs are sufficient to ground the final_output claims.

How to read task_result:
- "complete" means the primary loop finished normally.
- "iteration_limit" means the harness stopped the primary run at its cap.
  In that case final_output is often empty by truncation, not because the
  model refused to answer. Critique the truncation/limit honestly; do not
  treat an empty final_output on iteration_limit as a refusal to answer.

Respond with JSON only (no markdown fence required, but a single fenced JSON
object is acceptable). The JSON object must contain exactly these keys:
- task_status: one of SUCCESS, FAILED, PARTIAL_SUCCESS
- efficiency_score: a number from 0 to 1 inclusive
- critique: short evidence-grounded critique
- systemic_failure_root_cause: root cause or "none"
- workflow_adjustments: concrete adjustments or "none"

Do not include any other keys. Do not include chain-of-thought or private
reasoning outside those fields.
""".strip()


def _evaluation_error(message: str) -> dict[str, Any]:
    """Return a schema-valid result explaining why evaluation could not finish."""
    return {
        "task_status": "FAILED",
        "efficiency_score": 0.0,
        "critique": message,
        "systemic_failure_root_cause": "evaluation_error",
        "workflow_adjustments": "none",
    }


def _strip_code_fence(raw_output: str) -> str:
    """Remove an optional markdown ``` / ```json fence around JSON text."""
    text = (raw_output or "").strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if not lines:
        return text
    # Drop opening fence (``` or ```json) and a trailing fence if present.
    body = lines[1:]
    if body and body[-1].strip().startswith("```"):
        body = body[:-1]
    return "\n".join(body).strip()


def _parse_evaluation(raw_output: str) -> dict[str, Any]:
    """Validate raw evaluator text and coerce it into the required schema."""
    text = _strip_code_fence(raw_output)
    try:
        parsed = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        return _evaluation_error(f"evaluator response was not valid JSON: {exc}")

    if not isinstance(parsed, dict):
        return _evaluation_error("evaluator response must be a JSON object")

    if set(parsed.keys()) != REQUIRED_KEYS:
        return _evaluation_error(
            "evaluator response keys must be exactly "
            f"{sorted(REQUIRED_KEYS)}; got {sorted(parsed.keys())}"
        )

    task_status = parsed["task_status"]
    if task_status not in ALLOWED_TASK_STATUSES:
        return _evaluation_error(
            f"task_status must be one of {sorted(ALLOWED_TASK_STATUSES)}; "
            f"got {task_status!r}"
        )

    score = parsed["efficiency_score"]
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return _evaluation_error(
            f"efficiency_score must be a number from 0 to 1; got {score!r}"
        )
    score_value = float(score)
    if not 0.0 <= score_value <= 1.0:
        return _evaluation_error(
            f"efficiency_score must be between 0 and 1 inclusive; got {score_value}"
        )

    return {
        "task_status": task_status,
        "efficiency_score": score_value,
        "critique": parsed["critique"],
        "systemic_failure_root_cause": parsed["systemic_failure_root_cause"],
        "workflow_adjustments": parsed["workflow_adjustments"],
    }


def run_retrospective_evaluation(
    client: Any,
    deployment: str,
    original_prompt: str,
    execution_trace: list[dict[str, Any]],
    tool_run_log: list[dict[str, Any]],
    final_output: str,
    task_result: str,
) -> dict[str, Any]:
    """Return validated retrospective JSON for one finished task."""
    evidence = {
        "original_prompt": original_prompt,
        "execution_trace": execution_trace,
        "tool_run_log": tool_run_log,
        "final_output": final_output,
        "task_result": task_result,
    }
    try:
        review = client.responses.create(
            model=deployment,
            instructions=EVALUATION_INSTRUCTIONS,
            input=json.dumps(evidence, ensure_ascii=False),
        )
    except Exception as exc:  # transport / API failures must not crash the harness
        return _evaluation_error(f"retrospective evaluation API call failed: {exc}")

    return _parse_evaluation(getattr(review, "output_text", "") or "")
