#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   streaming_validator.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Streaming XGrammar validator for streaming output validation.
"""

import json
import re
from typing import Any

import xgrammar as xgr
from pydantic import BaseModel
from rich import print as rprint
from transformers import PreTrainedTokenizer


class StreamingXGrammarValidator:
    """Validates accumulated output chunks against xgrammar constraints during streaming.

    While the DebugXGrammarLogitsProcessor validates token-by-token during generation,
    this validator checks the accumulated output after each chunk to ensure it forms
    valid JSON that matches the expected schema.

    This provides:
    - Early error detection during streaming
    - Progressive JSON validation
    - Better debugging information about where violations occur

    For Chain-of-Thought (COT) mode, the validator tracks `<think>` and `<answer>`
    sections and only validates JSON content inside `<answer>` tags.

    """

    def __init__(
        self,
        schema: type[BaseModel] | None,
        compiler: xgr.GrammarCompiler | None = None,
        tokenizer: PreTrainedTokenizer | None = None,
        verbose: bool = False,
        cot: bool = False,
    ):
        """Initialize the streaming validator.

        Args:
            schema: Pydantic model defining the expected output schema
            compiler: xgrammar compiler for creating grammar matchers
            tokenizer: Tokenizer for converting text to token IDs. Required for
                accurate token-based validation. If None, falls back to character-based validation.
            verbose: If True, prints validation status for each chunk
            cot: If True, enables Chain-of-Thought mode where only content inside
                `<answer>` tags is validated against the schema.

        """
        self._schema = schema
        self._compiler = compiler
        self._tokenizer = tokenizer
        self._verbose = verbose
        self._cot = cot
        self._accumulated = ""
        self._accumulated_token_ids: list[int] = []
        self._last_valid_length = 0
        self._last_valid_token_length = 0
        self._validation_count = 0
        self._matcher_position = 0  # Track how many tokens we've validated so far

        # COT-specific state
        self._in_think = False
        self._in_answer = False
        self._answer_content = ""  # Content inside <answer> tags only
        self._answer_token_ids: list[int] = []  # Token IDs for answer content
        self._json_complete = False  # True once JSON is fully parsed in COT mode

        # Create grammar matcher if we have both schema and compiler
        if schema and compiler:
            self._compiled_grammar = compiler.compile_json_schema(schema)
            # Create a matcher for progressive validation
            self._matcher = xgr.GrammarMatcher(self._compiled_grammar)
        else:
            self._compiled_grammar = None
            self._matcher = None

    def validate_chunk(self, chunk: str) -> tuple[bool, str | None]:
        """Validate a new chunk of output.

        Args:
            chunk: New text chunk to add and validate

        Returns:
            Tuple of (is_valid, error_message). If is_valid is True, error_message is None.
            If is_valid is False, error_message contains details about the validation failure.

        """
        self._validation_count += 1
        self._accumulated += chunk

        # Tokenize the new chunk if we have a tokenizer
        if self._tokenizer:
            chunk_token_ids = self._tokenizer.encode(chunk, add_special_tokens=False)
            self._accumulated_token_ids.extend(chunk_token_ids)
        else:
            chunk_token_ids = []

        # COT mode: track sections and only validate <answer> content
        if self._cot:
            return self._validate_cot_chunk()

        # Non-COT mode: validate entire output
        # If no schema/matcher, just do basic JSON validation
        if self._matcher is None:
            return self._validate_json_only()

        # Try xgrammar validation with token IDs
        if self._tokenizer and chunk_token_ids:
            return self._validate_with_xgrammar_tokens()
        else:
            # Fallback to character-based validation if no tokenizer
            return self._validate_with_xgrammar()

    def _validate_json_only(self) -> tuple[bool, str | None]:
        """Validate that accumulated text is valid JSON (or could be when complete).

        Returns:
            Tuple of (is_valid, error_message)

        """
        # Try parsing as complete JSON
        try:
            json.loads(self._accumulated)
            self._last_valid_length = len(self._accumulated)
            if self._verbose:
                rprint(
                    f"[green]✓[/green] Chunk #{self._validation_count}: Valid complete JSON"
                )
            return True, None
        except json.JSONDecodeError as e:
            # Could be partial JSON (still being generated)
            # During streaming, we need to be lenient about incomplete content
            stripped = self._accumulated.strip()

            # Check if we're in the middle of generating a string value
            # Count quotes to see if we have an unclosed string
            def is_inside_string(text: str) -> bool:
                """Check if we're currently inside an unclosed string."""
                # Simple heuristic: count unescaped quotes
                # If odd number, we're inside a string
                quote_count = 0
                i = 0
                while i < len(text):
                    if text[i] == '"' and (i == 0 or text[i - 1] != "\\"):
                        quote_count += 1
                    i += 1
                return quote_count % 2 == 1

            # Check for common partial JSON patterns that are valid during streaming
            is_partial_valid = (
                # Empty or whitespace only
                stripped == ""
                # Ends with structural characters (definitely partial)
                or stripped.endswith(("{", "[", ":", ","))
                # Inside an unclosed string (being generated)
                or is_inside_string(stripped)
                # Just opened a string
                or stripped.endswith('"')
            )

            if is_partial_valid:
                if self._verbose:
                    rprint(
                        f"[yellow]⋯[/yellow] Chunk #{self._validation_count}: Partial JSON (still streaming)"
                    )
                return True, None

            # Check the specific error to determine if it's recoverable
            error_msg_lower = str(e).lower()
            recoverable_errors = [
                "unterminated string",  # String still being generated
                "expecting property name",  # Object key being generated
                "expecting value",  # Value being generated
                "expecting ',' delimiter",  # Next element being generated
            ]

            if any(err in error_msg_lower for err in recoverable_errors):
                if self._verbose:
                    rprint(
                        f"[yellow]⋯[/yellow] Chunk #{self._validation_count}: "
                        f"Recoverable partial state ({e})"
                    )
                return True, None

            # If we've accumulated very little, it's likely just starting
            if len(self._accumulated) < 50:
                if self._verbose:
                    rprint(
                        f"[yellow]⋯[/yellow] Chunk #{self._validation_count}: "
                        f"Early streaming stage"
                    )
                return True, None

            # If we've accumulated a lot since last valid state, that's suspicious
            chars_since_valid = len(self._accumulated) - self._last_valid_length
            if chars_since_valid > 500:
                error_msg = (
                    f"JSON validation failed after {self._validation_count} chunks: {e}. "
                    f"Generated {chars_since_valid} chars since last valid state."
                )
                if self._verbose:
                    rprint(f"[red]✗[/red] {error_msg}")
                    rprint(f"Accumulated so far: {self._accumulated[:200]}...")
                return False, error_msg

            # Otherwise, likely still partial - allow it
            if self._verbose:
                rprint(
                    f"[yellow]⋯[/yellow] Chunk #{self._validation_count}: "
                    f"Assuming partial (accumulated {len(self._accumulated)} chars)"
                )
            return True, None

    def _validate_with_xgrammar_tokens(self) -> tuple[bool, str | None]:
        """Validate accumulated text using xgrammar matcher with actual token IDs.

        This is the preferred method that uses actual token IDs from the tokenizer,
        providing more accurate grammar matching and better integration with xgrammar
        internals.

        Uses incremental validation: only validates new tokens since last validation,
        leveraging xgrammar's internal state management for efficiency.

        Returns:
            Tuple of (is_valid, error_message)

        """
        if self._matcher is None or not self._tokenizer:
            return True, None

        try:
            # Only validate new tokens (incremental validation)
            # The matcher maintains state between calls, so we don't need to reset
            new_tokens = self._accumulated_token_ids[self._matcher_position :]

            # Validate each new token incrementally
            for relative_idx, token_id in enumerate(new_tokens):
                if not self._matcher.accept_token(token_id):
                    token_idx = self._matcher_position + relative_idx

                    # Decode the problematic token for better error messages
                    try:
                        token_text = self._tokenizer.decode(
                            [token_id], skip_special_tokens=False
                        )
                    except Exception:
                        token_text = f"token_id_{token_id}"

                    # Get context around the error
                    context_start = max(0, token_idx - 5)
                    context_end = min(len(self._accumulated_token_ids), token_idx + 5)
                    context_tokens = self._accumulated_token_ids[
                        context_start:context_end
                    ]

                    try:
                        context_text = self._tokenizer.decode(
                            context_tokens, skip_special_tokens=False
                        )
                    except Exception:
                        context_text = f"[{len(context_tokens)} tokens]"

                    error_msg = (
                        f"Grammar violation at token {token_idx}: {repr(token_text)} "
                        f"(token_id={token_id}). Context: {repr(context_text)}"
                    )

                    if self._verbose:
                        rprint(
                            f"[red]✗[/red] Chunk #{self._validation_count}: {error_msg}"
                        )
                        # Show accumulated text around the error position
                        try:
                            text_pos = len(
                                self._tokenizer.decode(
                                    self._accumulated_token_ids[:token_idx],
                                    skip_special_tokens=False,
                                )
                            )
                            context_start_text = max(0, text_pos - 50)
                            context_end_text = min(
                                len(self._accumulated), text_pos + 50
                            )
                            rprint(
                                f"Text position: {text_pos}, "
                                f"context: {repr(self._accumulated[context_start_text:context_end_text])}"
                            )
                        except Exception:
                            pass

                    return False, error_msg

            # Update position after successfully validating all new tokens
            self._matcher_position = len(self._accumulated_token_ids)

            # Also try JSON validation for syntax correctness
            is_valid, json_error = self._validate_json_only()
            if not is_valid:
                return False, json_error

            # Check if the grammar matcher is in a terminated state
            # This indicates the output matches the expected structure
            is_terminated = self._matcher.is_terminated()

            if is_terminated:
                self._last_valid_length = len(self._accumulated)
                self._last_valid_token_length = len(self._accumulated_token_ids)
                if self._verbose:
                    rprint(
                        f"[green]✓[/green] Chunk #{self._validation_count}: "
                        f"Complete and valid ({len(self._accumulated_token_ids)} tokens)"
                    )
            else:
                # Grammar is not terminated yet, but tokens are valid so far
                # This is normal for partial/incomplete output
                if self._verbose:
                    rprint(
                        f"[yellow]⋯[/yellow] Chunk #{self._validation_count}: "
                        f"Partial but valid ({len(self._accumulated_token_ids)} tokens)"
                    )

            return True, None

        except Exception as e:
            error_msg = f"xgrammar validation error: {e}"
            if self._verbose:
                rprint(f"[red]✗[/red] Chunk #{self._validation_count}: {error_msg}")
                import traceback

                rprint(traceback.format_exc())
            return False, error_msg

    def _validate_with_xgrammar(self) -> tuple[bool, str | None]:
        """Validate accumulated text using xgrammar matcher (character-based fallback).

        This is a fallback method used when no tokenizer is available.
        It uses character codes instead of actual token IDs, which is less accurate
        but still provides basic validation.

        Returns:
            Tuple of (is_valid, error_message)

        """
        if self._matcher is None:
            return True, None

        try:
            # Reset matcher and try to accept the full accumulated string
            self._matcher.reset()

            # Feed the accumulated text to the matcher character by character
            # This is less accurate than token-based validation
            for char_pos, char in enumerate(self._accumulated):
                char_code = ord(char)
                # Note: This is a simplified approach using character codes
                # It's less accurate than token-based validation
                if not self._matcher.accept_token(char_code):
                    error_msg = (
                        f"Grammar violation at character position {char_pos}: "
                        f"'{char}' (char_code={char_code})"
                    )
                    if self._verbose:
                        rprint(
                            f"[red]✗[/red] Chunk #{self._validation_count}: {error_msg}"
                        )
                        context_start = max(0, char_pos - 20)
                        context_end = min(len(self._accumulated), char_pos + 20)
                        rprint(
                            f"Context: {repr(self._accumulated[context_start:context_end])}"
                        )
                    return False, error_msg

            # Also try JSON validation
            is_valid, json_error = self._validate_json_only()
            if not is_valid:
                return False, json_error

            # Check if we can terminate (complete JSON)
            if self._matcher.is_terminated():
                if self._verbose:
                    rprint(
                        f"[green]✓[/green] Chunk #{self._validation_count}: Complete and valid"
                    )
            else:
                if self._verbose:
                    rprint(
                        f"[yellow]⋯[/yellow] Chunk #{self._validation_count}: Partial but valid"
                    )

            self._last_valid_length = len(self._accumulated)
            return True, None

        except Exception as e:
            error_msg = f"xgrammar validation error: {e}"
            if self._verbose:
                rprint(f"[red]✗[/red] Chunk #{self._validation_count}: {error_msg}")
            return False, error_msg

    def _validate_cot_chunk(self) -> tuple[bool, str | None]:
        """Validate a chunk in COT mode, only validating <answer> content.

        This method is lenient and handles multiple output formats:
        1. Proper COT output with `<answer>` tags - validates content inside <answer>
        2. `<think>` tags but no `<answer>` tags - validates content OUTSIDE <think> tags
        3. No COT tags at all - validates entire output as JSON

        Returns:
            Tuple of (is_valid, error_message)

        """
        # Update section tracking based on accumulated content
        self._update_cot_section_state()

        # Check for fallback modes when no <answer> tags are present
        has_think_tags = "<think>" in self._accumulated
        has_answer_tags = "<answer>" in self._accumulated

        # Fallback mode 1: <think> tags but no <answer> tags
        # In this case, validate content OUTSIDE the <think> tags as JSON
        if has_think_tags and not has_answer_tags and not self._in_think:
            # Extract content outside <think> tags
            non_think_content = self._extract_content_outside_think_tags(
                self._accumulated
            )
            non_think_stripped = non_think_content.strip()

            # Only validate if we have actual JSON content
            if non_think_stripped and non_think_stripped[0] in "{[":
                self._non_think_content = non_think_content
                # Temporarily swap accumulated for JSON validation
                original_accumulated = self._accumulated
                self._accumulated = non_think_stripped
                result = self._validate_json_only()
                self._accumulated = original_accumulated
                return result

            # Inside <think> or no JSON content yet - skip validation
            return True, None

        # Fallback mode 2: no COT tags at all, plain JSON output
        accumulated_stripped = self._accumulated.strip()
        no_cot_tags_seen = not has_think_tags and not has_answer_tags
        looks_like_json = accumulated_stripped and accumulated_stripped[0] in "{["

        if no_cot_tags_seen and looks_like_json:
            # Fallback mode: validate as plain JSON
            return self._validate_json_only()

        # If we're in the answer section, extract and validate the answer content
        if self._in_answer:
            # If JSON is already complete, skip validation for trailing content
            # (whitespace before </answer>)
            if self._json_complete:
                return True, None

            answer_start_idx = self._accumulated.rfind("<answer>")
            if answer_start_idx != -1:
                new_answer_content = self._accumulated[
                    answer_start_idx + len("<answer>") :
                ]
                # Remove </answer> if present
                if "</answer>" in new_answer_content:
                    new_answer_content = new_answer_content[
                        : new_answer_content.find("</answer>")
                    ]

                # Strip BOTH leading and trailing whitespace for validation
                # Models often output newlines around JSON like: <answer>\n{...}\n</answer>
                new_answer_stripped = new_answer_content.strip()

                # Only validate if we have actual JSON content (starts with { or [)
                if not new_answer_stripped:
                    # Only whitespace so far, nothing to validate
                    self._answer_content = new_answer_content
                elif new_answer_stripped[0] not in "{[":
                    # Content doesn't look like JSON yet, skip validation
                    self._answer_content = new_answer_content
                elif len(new_answer_stripped) > len(self._answer_content.strip()):
                    # We have new JSON content to validate
                    old_stripped = self._answer_content.strip()
                    new_chunk = new_answer_stripped[len(old_stripped) :]
                    self._answer_content = new_answer_content

                    # Also strip trailing whitespace from the new chunk
                    # This handles tokens like '}\n' - we only want to validate '}'
                    new_chunk = new_chunk.rstrip()

                    if new_chunk:
                        # Tokenize the new answer chunk
                        if self._tokenizer:
                            new_chunk_tokens = self._tokenizer.encode(
                                new_chunk, add_special_tokens=False
                            )
                            self._answer_token_ids.extend(new_chunk_tokens)

                        # Validate using the matcher if available
                        if self._matcher is not None and self._tokenizer:
                            # Validate new tokens incrementally
                            start_pos = len(self._answer_token_ids) - len(
                                new_chunk_tokens
                            )
                            for i, token_id in enumerate(new_chunk_tokens):
                                # Check if JSON is already complete before this token
                                if self._matcher.is_terminated():
                                    self._json_complete = True
                                    break

                                if not self._matcher.accept_token(token_id):
                                    token_idx = start_pos + i
                                    try:
                                        token_text = self._tokenizer.decode(
                                            [token_id], skip_special_tokens=False
                                        )
                                    except Exception:
                                        token_text = f"token_id_{token_id}"
                                    error_msg = (
                                        f"Grammar violation in <answer> at token "
                                        f"{token_idx}: {repr(token_text)}"
                                    )
                                    if self._verbose:
                                        rprint(
                                            f"[red]✗[/red] COT Chunk "
                                            f"#{self._validation_count}: {error_msg}"
                                        )
                                    return False, error_msg

                            # Check if JSON completed after processing all tokens
                            if self._matcher.is_terminated():
                                self._json_complete = True
                else:
                    # No new content
                    self._answer_content = new_answer_content

        if self._verbose:
            section = (
                "answer"
                if self._in_answer
                else "think"
                if self._in_think
                else "preamble"
            )
            rprint(
                f"[blue]⋯[/blue] COT Chunk #{self._validation_count}: "
                f"Section={section}, accumulated={len(self._accumulated)} chars"
            )

        return True, None

    def _update_cot_section_state(self) -> None:
        """Update the current COT section state based on accumulated content."""
        # Check for think tags
        think_start = self._accumulated.rfind("<think>")
        think_end = self._accumulated.rfind("</think>")

        # Check for answer tags
        answer_start = self._accumulated.rfind("<answer>")
        answer_end = self._accumulated.rfind("</answer>")

        # Determine current state based on tag positions
        if answer_start != -1 and (answer_end == -1 or answer_start > answer_end):
            # Inside <answer> section
            self._in_answer = True
            self._in_think = False
        elif think_start != -1 and (think_end == -1 or think_start > think_end):
            # Inside <think> section
            self._in_think = True
            self._in_answer = False
        else:
            # Outside both sections (or after closing tags)
            if answer_end != -1 and answer_end > answer_start:
                self._in_answer = False
            if think_end != -1 and think_end > think_start:
                self._in_think = False

    def _extract_content_outside_think_tags(self, text: str) -> str:
        """Extract content that is outside all <think>...</think> sections.

        This handles the case where the model outputs <think> tags but no <answer>
        tags, and the JSON is everything outside the think sections.

        Also strips markdown code fences (```json ... ```) if present.

        Args:
            text: The full text to process

        Returns:
            Content outside all <think> sections, concatenated together,
            with markdown code fences stripped if present.

        """
        result_parts: list[str] = []
        current_pos = 0

        while current_pos < len(text):
            # Find the next <think> tag
            think_start = text.find("<think>", current_pos)

            if think_start == -1:
                # No more <think> tags, add the rest of the text
                result_parts.append(text[current_pos:])
                break

            # Add content before <think> tag
            if think_start > current_pos:
                result_parts.append(text[current_pos:think_start])

            # Find the closing </think> tag
            think_end = text.find("</think>", think_start)

            if think_end == -1:
                # Unclosed <think> tag - we're inside a think section
                # Don't include anything after the <think> tag
                break

            # Move past the </think> tag
            current_pos = think_end + len("</think>")

        result = "".join(result_parts)

        # Strip markdown code fences if present (e.g., ```json ... ```)
        result = self._strip_markdown_code_fences(result)

        return result

    def _strip_markdown_code_fences(self, text: str) -> str:
        r"""Strip markdown code fences from text.

        Handles formats like:
        - ```json\\n{...}\\n```
        - ```\\n{...}\\n```

        Args:
            text: Text that may contain markdown code fences

        Returns:
            Text with code fences stripped, or original text if no fences found.

        """
        stripped = text.strip()

        # Pattern to match ```json or ``` at the start, and ``` at the end
        # Allow for optional language identifier after opening ```
        pattern = r"^```(?:\w+)?\s*\n?(.*?)\n?```\s*$"
        match = re.match(pattern, stripped, re.DOTALL)

        if match:
            return match.group(1).strip()

        return text

    def validate_final(self) -> tuple[bool, str | None, Any | None]:
        """Validate the final accumulated output and parse it.

        Returns:
            Tuple of (is_valid, error_message, parsed_result). If validation succeeds,
            returns (True, None, parsed_model). If validation fails, returns
            (False, error_message, None).

        """
        # COT mode: validate the answer content
        if self._cot:
            return self._validate_cot_final()

        # Non-COT mode: validate entire output as JSON
        # First check if it's valid JSON
        try:
            parsed_json = json.loads(self._accumulated)
        except json.JSONDecodeError as e:
            return False, f"Final output is not valid JSON: {e}", None

        # If we have a schema, validate against it
        if self._schema:
            try:
                parsed_model = self._schema.model_validate(parsed_json)
                if self._verbose:
                    rprint("[green]✓[/green] Final output validated against schema")
                return True, None, parsed_model
            except Exception as e:
                return False, f"Final output doesn't match schema: {e}", None

        # No schema, just return the parsed JSON
        return True, None, parsed_json

    def _validate_cot_final(self) -> tuple[bool, str | None, Any | None]:
        """Validate the final COT output.

        This method is lenient and handles multiple output formats:
        1. Proper COT output with `<think>` and `<answer>` tags - validates <answer> content
        2. `<think>` tags but no `<answer>` tags - validates content OUTSIDE <think> tags
        3. No COT tags at all - validates entire output as JSON

        Returns:
            Tuple of (is_valid, error_message, parsed_result).

        """
        has_think_tags = "<think>" in self._accumulated
        has_answer_start = "<answer>" in self._accumulated
        has_answer_end = "</answer>" in self._accumulated

        # Case 1: <think> tags but no <answer> tags
        # Validate content OUTSIDE the <think> tags as JSON
        if has_think_tags and not has_answer_start and not has_answer_end:
            if self._verbose:
                rprint(
                    "[yellow]⚠[/yellow] Found <think> tags but no <answer> tags, "
                    "validating content outside <think> sections"
                )
            # Extract content outside <think> tags
            non_think_content = self._extract_content_outside_think_tags(
                self._accumulated
            ).strip()

            if not non_think_content:
                return False, "No content found outside <think> tags", None

            try:
                parsed_json = json.loads(non_think_content)
            except json.JSONDecodeError as e:
                return (
                    False,
                    f"Content outside <think> tags is not valid JSON: {e}",
                    None,
                )

            # If we have a schema, validate against it
            if self._schema:
                try:
                    parsed_model = self._schema.model_validate(parsed_json)
                    if self._verbose:
                        rprint(
                            "[green]✓[/green] Content outside <think> validated against schema"
                        )
                    return True, None, parsed_model
                except Exception as e:
                    return (
                        False,
                        f"Content outside <think> doesn't match schema: {e}",
                        None,
                    )

            return True, None, parsed_json

        # Case 2: No COT structure at all - fall back to treating entire output as JSON
        if not has_think_tags and not has_answer_start and not has_answer_end:
            if self._verbose:
                rprint(
                    "[yellow]⚠[/yellow] No COT tags found, "
                    "falling back to plain JSON validation"
                )
            try:
                parsed_json = json.loads(self._accumulated.strip())
            except json.JSONDecodeError as e:
                return False, f"Output is not valid JSON: {e}", None

            # If we have a schema, validate against it
            if self._schema:
                try:
                    parsed_model = self._schema.model_validate(parsed_json)
                    if self._verbose:
                        rprint(
                            "[green]✓[/green] Output validated against schema "
                            "(fallback mode)"
                        )
                    return True, None, parsed_model
                except Exception as e:
                    return False, f"Output doesn't match schema: {e}", None

            return True, None, parsed_json

        # Case 3: Has <answer> tags - validate the answer content
        if has_answer_start and not has_answer_end:
            return False, "Missing closing </answer> tag", None

        # Validate the answer content as JSON (strip whitespace)
        answer_json = self._answer_content.strip()
        if answer_json:
            try:
                parsed_json = json.loads(answer_json)
            except json.JSONDecodeError as e:
                return False, f"Answer content is not valid JSON: {e}", None

            # If we have a schema, validate against it
            if self._schema:
                try:
                    parsed_model = self._schema.model_validate(parsed_json)
                    if self._verbose:
                        rprint(
                            "[green]✓[/green] COT answer content validated against schema"
                        )
                    return True, None, parsed_model
                except Exception as e:
                    return False, f"Answer content doesn't match schema: {e}", None

            return True, None, parsed_json

        return True, None, None

    def get_accumulated(self) -> str:
        """Get the accumulated output so far.

        Returns:
            The full accumulated text

        """
        return self._accumulated

    def get_answer_content(self) -> str:
        """Get the content inside <answer> tags (COT mode only).

        Returns:
            The content inside <answer> tags, or empty string if not in COT mode.

        """
        return self._answer_content

    def reset(self) -> None:
        """Reset the validator to start fresh."""
        self._accumulated = ""
        self._accumulated_token_ids = []
        self._last_valid_length = 0
        self._last_valid_token_length = 0
        self._validation_count = 0
        self._matcher_position = 0
        # Reset COT state
        self._in_think = False
        self._in_answer = False
        self._answer_content = ""
        self._answer_token_ids = []
        self._json_complete = False
        self._non_think_content = ""
        if self._matcher:
            self._matcher.reset()
