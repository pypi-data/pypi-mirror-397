#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   postprocessing.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference postprocessing utilities.
"""

import re

from vi.inference.task_types import (
    GenericResponse,
    PredictionResponse,
    TaskAssistant,
    consts,
)
from vi.inference.task_types.phrase_grounding import PhraseGroundingResponse
from vi.inference.task_types.vqa import VQAResponse


def extract_content(result: str) -> tuple[str, str | None]:
    """Extract JSON content and thinking from model output.

    Handles various output formats:
    - <think>...</think> tags (COT reasoning)
    - <answer>...</answer> tags (COT structured output)
    - Markdown code blocks (```json...``` or ```...```)
    - Raw JSON

    Args:
        result: Raw model output potentially containing tags or code blocks.

    Returns:
        Tuple of (json_content, thinking_content).
        thinking_content is None if no <think> tags found.

    """
    thinking: str | None = None

    # Extract thinking content from <think> tags
    think_pattern = r"<think>(.*?)</think>"
    think_match = re.search(think_pattern, result, re.DOTALL)
    if think_match:
        thinking = think_match.group(1).strip()

    # Extract JSON from <answer> tags
    json_content = result
    answer_pattern = r"<answer>(.*?)</answer>"
    answer_match = re.search(answer_pattern, result, re.DOTALL)
    if answer_match:
        json_content = answer_match.group(1).strip()
    elif think_match:
        # If no <answer> tags but <think> tags exist, extract content outside <think> tags
        json_content = re.sub(think_pattern, "", result, flags=re.DOTALL).strip()

    # Strip markdown code blocks if present
    code_block_pattern = r"^```(?:json)?\s*\n?(.*?)\n?```$"
    code_match = re.search(code_block_pattern, json_content.strip(), re.DOTALL)
    if code_match:
        json_content = code_match.group(1).strip()

    return json_content, thinking


def parse_result(
    raw_output: str,
    user_prompt: str,
    task_type: consts.TaskType,
    schema: type[TaskAssistant] | None,
) -> PredictionResponse:
    """Parse generated output into appropriate response type.

    Automatically extracts JSON from COT tags (<answer>...</answer>)
    and markdown code blocks if present. Also extracts thinking content
    from <think>...</think> tags.

    Args:
        raw_output: Raw model output (may contain COT tags or code blocks).
        user_prompt: The user prompt used for inference.
        task_type: The task type (VQA, PHRASE_GROUNDING, GENERIC).
        schema: The schema class for parsing (TaskAssistant subclass).

    Returns:
        Parsed prediction response based on task type. Includes raw_output
        and thinking fields. If parsing fails, returns GenericResponse
        with the full raw output.

    """
    # Extract JSON and thinking content
    json_content, thinking = extract_content(raw_output)

    # For generic task type, return raw output directly
    if task_type == consts.TaskType.GENERIC:
        return GenericResponse(
            prompt=user_prompt,
            result=raw_output,
            raw_output=raw_output,
            thinking=thinking,
        )

    # Try to parse JSON for structured task types
    try:
        if schema is None:
            raise ValueError("Schema is required for structured task types")

        assistant = schema.model_validate_json(json_content)

        if task_type == consts.TaskType.VQA:
            return VQAResponse(
                prompt=user_prompt,
                result=assistant.vqa,
                raw_output=raw_output,
                thinking=thinking,
            )

        if task_type == consts.TaskType.PHRASE_GROUNDING:
            return PhraseGroundingResponse(
                prompt=user_prompt,
                result=assistant.phrase_grounding,
                raw_output=raw_output,
                thinking=thinking,
            )

    except Exception:
        # If parsing fails, return GenericResponse with full raw output
        return GenericResponse(
            prompt=user_prompt,
            result=raw_output,
            raw_output=raw_output,
            thinking=thinking,
        )

    raise ValueError(f"Unknown task type: {task_type}")
