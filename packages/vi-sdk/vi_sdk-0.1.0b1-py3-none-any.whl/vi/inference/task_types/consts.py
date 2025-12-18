#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   consts.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference task types consts module.
"""

from enum import Enum

from vi.inference.task_types import PredictionResponse, TaskAssistant
from vi.inference.task_types.phrase_grounding import (
    PhraseGroundingAssistant,
    PhraseGroundingResponse,
)
from vi.inference.task_types.vqa import VQAAssistant, VQAResponse


class TaskType(Enum):
    """Task type enum."""

    PHRASE_GROUNDING = "phrase-grounding"
    VQA = "vqa"
    GENERIC = "generic"


TASK_TYPE_TO_ASSISTANT_MAP: dict[TaskType, type[TaskAssistant] | None] = {
    TaskType.PHRASE_GROUNDING: PhraseGroundingAssistant,
    TaskType.VQA: VQAAssistant,
    TaskType.GENERIC: None,
}

TASK_TYPE_TO_RESPONSE_MAP: dict[TaskType, type[PredictionResponse] | None] = {
    TaskType.PHRASE_GROUNDING: PhraseGroundingResponse,
    TaskType.VQA: VQAResponse,
    TaskType.GENERIC: None,
}


PHRASE_GROUNDING_USER_PROMPT = """
Analyze this image and provide comprehensive object grounding:

- Examine all regions of the image to identify distinct objects
- Generate a detailed caption describing what you observe
- Decompose your caption into:
  * Grounded phrases: noun phrases referring to visible objects (with bounding boxes)
  * Ungrounded phrases: connecting words without visual referents
- Ensure the phrase sequence reconstructs your complete caption

Requirements:

- Include objects from across the entire image
- Each grounded phrase MUST have accurate bounding box(es)
- Maintain the exact order and spacing to reconstruct the caption
- Avoid detecting the same object instance multiple times
- All coordinates must be within [0, 1024]

Return the results in the specified JSON format with the 'phrase_grounding' structure.
"""

VQA_USER_PROMPT = "What is in this image?"

TASK_TYPE_TO_USER_PROMPT_MAP: dict[TaskType, str | None] = {
    TaskType.PHRASE_GROUNDING: PHRASE_GROUNDING_USER_PROMPT,
    TaskType.VQA: VQA_USER_PROMPT,
    TaskType.GENERIC: None,
}

COT_SYSTEM_PROMPT_SUFFIX = (
    " Answer the question in the following format: <think>"
    "\nyour reasoning\n</think>\n\n"
    "<answer>\nyour answer\n</answer>"
)
