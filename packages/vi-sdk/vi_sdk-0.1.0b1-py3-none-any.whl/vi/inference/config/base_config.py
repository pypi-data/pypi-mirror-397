#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   base_config.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference base generation config module.
"""

from msgspec import Struct, field
from xgrammar.contrib.hf import LogitsProcessor


class ViGenerationConfig(
    Struct, kw_only=True, rename="camel", forbid_unknown_fields=False
):
    """Generation configuration.

    Attributes:
        temperature: Sampling temperature.
        top_k: Top-k sampling.
        top_p: Nucleus sampling probability.
        repetition_penalty: Repetition penalty.
        max_new_tokens: Maximum number of tokens to generate.
        do_sample: Whether to use sampling.
        seed: Random seed for reproducibility. Defaults to 0 for deterministic output.
            Set to -1 to disable seeding and use random generation.
        logits_processor: Logits processor.

    """

    temperature: float = 1.0
    top_k: int = 50
    top_p: float = 1.0
    repetition_penalty: float = 1.05
    max_new_tokens: int = 1024
    do_sample: bool = False
    seed: int = 0
    logits_processor: list[LogitsProcessor] = field(default_factory=list)
