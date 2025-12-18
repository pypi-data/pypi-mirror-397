#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   conditional_processor.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Conditional XGrammar logits processor for structured output generation.
"""

from typing import Any

import torch
import xgrammar as xgr
from vi.inference.utils.compiler import compile_grammar_str


class ConditionalXGrammarLogitsProcessor:
    """A logits processor that conditionally applies xgrammar constraints during generation.

    This processor remains inactive (i.e., does not constrain logits) until it detects an
    <answer> tag in the input token IDs, at which point it activates xgrammar processing for
    constrained output generation. Once an </answer> tag is detected, the processor deactivates
    and will no longer apply grammar constraints, allowing free-form (unconstrained) generation.
    This is particularly useful for generation scenarios that require alternating between
    chain-of-thought and structured output, e.g.:
        ...<thoughts>...</thoughts><answer>STRICT_JSON</answer><thoughts>...</thoughts><answer>...</answer>

    Attributes:
        xgr_processor: The underlying xgrammar logits processor (applies grammar constraints).
        tokenizer: The tokenizer used for tag detection and text decoding.
        is_active: Whether xgrammar constraints are currently active (inside an <answer> section).
        answer_start_tag: The tag which triggers activation of grammar processing (default "<answer>").
        answer_end_tag: The tag which deactivates grammar processing (default "</answer>").
        start_tag_ids: Pre-encoded token IDs for answer_start_tag (for fast matching).
        end_tag_ids: Pre-encoded token IDs for answer_end_tag (for fast matching).

    """

    @classmethod
    def from_compiled_grammar(
        cls,
        compiled_grammar: "xgr.CompiledGrammar",
        tokenizer: Any,
        suffix_string: str | None = None,
    ) -> "ConditionalXGrammarLogitsProcessor":
        """Construct a ConditionalXGrammarLogitsProcessor from an xgrammar CompiledGrammar.

        Args:
            compiled_grammar: An xgrammar CompiledGrammar object, usually compiled from a schema.
            tokenizer: The tokenizer instance (must provide .encode() and .decode()).
            suffix_string: Optionally, a string that is required after the answer section;
                if provided, additional rules are added to enforce suffix appearance.

        Returns:
            ConditionalXGrammarLogitsProcessor: Configured processor ready for use.

        """
        # Create the base xgrammar processor, optionally augmenting grammar rules
        if suffix_string is not None:
            schema_rules = str(compiled_grammar.grammar)
            updated_schema_rules = schema_rules.replace("root ::=", "schema_rules ::=")
            new_rules = f"""
                root ::= schema_rules ws answer_suffix
                ws ::= [ \\n\\t]*
                answer_suffix ::= "{suffix_string}"
                {updated_schema_rules}
            """
            new_compiled = compile_grammar_str(tokenizer, new_rules)
            base_xgr_processor = xgr.contrib.hf.LogitsProcessor(new_compiled)
        else:
            base_xgr_processor = xgr.contrib.hf.LogitsProcessor(compiled_grammar)

        return cls(base_xgr_processor, tokenizer)

    def __init__(
        self,
        xgr_processor: Any,
        tokenizer: Any,
    ):
        """Initialize the conditional logits processor.

        Args:
            xgr_processor: The base xgrammar logits processor to delegate to when active.
            tokenizer: Tokenizer used for tag encoding/decoding.

        """
        self.xgr_processor: Any = xgr_processor
        self.tokenizer: Any = tokenizer
        self.is_active: bool = False
        self.answer_start_tag: str = "<answer>"
        self.answer_end_tag: str = "</answer>"

        # Pre-encode tags for efficient matching in token streams
        self.start_tag_ids: list[int] = self.tokenizer.encode(
            self.answer_start_tag, add_special_tokens=False
        )
        self.end_tag_ids: list[int] = self.tokenizer.encode(
            self.answer_end_tag, add_special_tokens=False
        )

    def _check_for_tag(self, input_ids: "torch.LongTensor", tag_ids: list[int]) -> bool:
        """Return True if the given tag (represented by tag_ids) matches the last tokens.

        Args:
            input_ids: Tensor of input token IDs of shape (batch, seq_len).
            tag_ids: List of token IDs representing the tag to match.

        Returns:
            bool: True if tag_ids appears at the end of input_ids[0], otherwise False.

        """
        if input_ids.shape[1] < len(tag_ids):
            return False
        sequence = input_ids[0, -len(tag_ids) :].tolist()
        return sequence == tag_ids

    def _check_tag_in_recent_tokens(
        self,
        input_ids: "torch.LongTensor",
        tag_ids: list[int],
        tag_string: str,
        lookback: int = 50,
    ) -> bool:
        """Check if the tag appears anywhere in the last `lookback` tokens.

        This is robust to edge conditions, as tags may be split across token boundaries or not
        perfectly aligned with chunked generation. Also decodes recent tokens to check for tag
        presence in the text if token-based matching fails.

        Args:
            input_ids: Tensor of input token IDs (shape [batch, seq_len]).
            tag_ids: List of token IDs comprising the target tag.
            tag_string: The original tag string (for text-based fallback).
            lookback: Number of most recent tokens to examine.

        Returns:
            bool: True if the tag is detected, otherwise False.

        """
        if input_ids.shape[1] < len(tag_ids):
            return False

        # Token-based check in the lookback window
        start_idx = max(0, input_ids.shape[1] - lookback)
        recent_tokens = input_ids[0, start_idx:].tolist()
        for i in range(len(recent_tokens) - len(tag_ids) + 1):
            if recent_tokens[i : i + len(tag_ids)] == tag_ids:
                return True

        # Fallback: Decode and check if tag_string is in recent generated text
        try:
            decoded_text = self.tokenizer.decode(
                input_ids[0, start_idx:], skip_special_tokens=False
            )
            if tag_string in decoded_text:
                return True
        except Exception:
            pass
        return False

    def __call__(
        self,
        input_ids: "torch.LongTensor",
        scores: "torch.FloatTensor",
    ) -> "torch.FloatTensor":
        """Conditionally apply xgrammar constraints depending on tag detection.

        Args:
            input_ids: Input token IDs to the generation step (shape [1, seq_len]).
            scores: Scores/logits to be modified (shape [1, vocab_size]).

        Returns:
            torch.FloatTensor: The possibly constrained scores. If inside an <answer> section,
            returns scores modified by the xgrammar processor; otherwise, returns unchanged.

        """
        # Activate if entering <answer> section (i.e., tag has just appeared)
        if not self.is_active:
            if self._check_tag_in_recent_tokens(
                input_ids, self.start_tag_ids, self.answer_start_tag
            ):
                self.is_active = True

        # Deactivate if exiting </answer> section
        if self.is_active:
            if self._check_tag_in_recent_tokens(
                input_ids, self.end_tag_ids, self.answer_end_tag
            ):
                self.is_active = False

        # Apply xgrammar only if active; otherwise, let freeform tokens through
        if self.is_active:
            try:
                # Move to CPU if necessary
                input_ids_cpu = input_ids.cpu()
                scores_cpu = scores.cpu()

                modified_scores_cpu = self.xgr_processor(input_ids_cpu, scores_cpu)
                modified_scores = modified_scores_cpu.to(scores.device)
                return modified_scores
            except Exception:
                # If xgrammar fails, deactivate and allow generation to pass through
                self.is_active = False
                return scores
        else:
            return scores
