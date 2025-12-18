#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   debug_processor.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Debug wrapper for XGrammar logits processor.
"""

import torch
import xgrammar as xgr
from rich import print as rprint
from transformers import PreTrainedTokenizer


class DebugXGrammarLogitsProcessor:
    """Debug wrapper for XGrammar logits processor with detailed error diagnostics.

    Wraps the XGrammar LogitsProcessor to provide comprehensive debugging information
    when grammar constraints fail during structured output generation. Displays recent
    tokens, candidate tokens, and decoding context to help diagnose schema violations.

    This is particularly useful for debugging models that generate structured outputs
    (JSON, XML, etc.) where grammar constraints must be satisfied at each generation step.

    """

    @classmethod
    def from_compiled_grammar(cls, compiled_grammar, tokenizer):
        """Create a LogitsProcessor from a compiled grammar and tokenizer."""
        base_xgr_processor = xgr.contrib.hf.LogitsProcessor(compiled_grammar)
        return cls(base_xgr_processor, tokenizer)

    def __init__(
        self,
        xgr_processor: xgr.contrib.hf.LogitsProcessor,
        tokenizer: PreTrainedTokenizer,
    ):
        """Initialize the debug wrapper with base processor and tokenizer.

        Args:
            xgr_processor: Base XGrammar logits processor that enforces grammar constraints.
            tokenizer: Tokenizer for decoding token IDs to text for error reporting.

        """
        self._xgr_processor = xgr_processor
        self._tokenizer = tokenizer
        self._call_count = 0

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> torch.FloatTensor:
        """Process logits with grammar constraints and detailed error reporting.

        Applies XGrammar processing to constrain model outputs to valid grammar
        productions. If grammar validation fails, displays comprehensive debugging
        information including recent tokens, top candidates, and generation context.

        The processing is performed on CPU for compatibility, then moved back to
        the original device.

        Args:
            input_ids: Token IDs generated so far (batch_size, sequence_length).
            scores: Unnormalized logits for next token prediction (batch_size, vocab_size).

        Returns:
            Modified logits with invalid grammar productions masked out. Same shape
            as input scores, on the same device.

        Raises:
            AssertionError: If XGrammar internal assertion fails due to grammar
                violation or unexpected state. Includes detailed diagnostic output.

        """
        self._call_count += 1

        try:
            # Apply xgrammar processing
            input_ids_cpu = input_ids.cpu()
            scores_cpu = scores.cpu()

            # Apply xgrammar processing on CPU
            modified_scores_cpu = self._xgr_processor(input_ids_cpu, scores_cpu)

            # Move back to original device
            modified_scores = modified_scores_cpu.to(scores.device)
            return modified_scores

        except AssertionError as e:
            rprint(f"\n=== XGRAMMAR ASSERTION ERROR (Call #{self._call_count}) ===")
            rprint(f"Error: {e}")
            rprint(f"Input IDs shape: {input_ids.shape}")
            rprint(f"Scores shape: {scores.shape}")

            # Show the last few tokens that were generated
            if input_ids.shape[1] > 0:
                recent_tokens = input_ids[0, -10:].tolist()  # Last 10 tokens
                rprint(f"Recent tokens: {recent_tokens}")
                recent_text = self._tokenizer.decode(
                    recent_tokens, skip_special_tokens=False
                )
                rprint(f"Recent text: {repr(recent_text)}")

            # Show which token would be selected based on current scores
            top_token_id = torch.argmax(scores[0]).item()
            top_token_text = self._tokenizer.decode(
                [top_token_id], skip_special_tokens=False
            )
            rprint(f"Top scoring token ID: {top_token_id}")
            rprint(f"Top scoring token text: {repr(top_token_text)}")

            # Show some alternative high-scoring tokens
            top_5_ids = torch.topk(scores[0], 5).indices.tolist()
            rprint("Top 5 token candidates:")
            for i, token_id in enumerate(top_5_ids):
                token_text = self._tokenizer.decode(
                    [token_id], skip_special_tokens=False
                )
                rprint(f"  {i + 1}. ID {token_id}: {repr(token_text)}")

            rprint("=== END XGRAMMAR ERROR INFO ===\n")

            # Re-raise the error
            raise
