#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   streaming.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference streaming module.
"""

import threading
from collections.abc import Callable, Generator
from typing import Any

import msgspec
import torch
from transformers import TextIteratorStreamer
from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.logits_processors import StreamingXGrammarValidator
from vi.inference.task_types.assistant import PredictionResponse

# Disable inductor async compile workers to prevent hanging on exit
torch._inductor.config.compile_threads = 1


class StreamingMixin:
    """Mixin class providing streaming generation capabilities for predictors.

    This mixin provides common streaming functionality that can be added to
    any predictor class through multiple inheritance. It handles:
    - Threaded model generation for non-blocking streaming
    - Token-by-token output with buffering
    - Optional chunk validation against schemas
    - JSON-aware formatting that preserves indentation

    Example:
        ```python
        class MyPredictor(BasePredictor, StreamingMixin):
            def __call__(self, source: str, stream: bool = False):
                # ... setup code ...
                if stream:
                    return self._stream_generator(...)
                # ... non-streaming code ...
        ```

    Note:
        This is designed as a mixin and should be used alongside BasePredictor
        or similar base classes that define the core prediction interface.

    """

    def _run_generation(
        self,
        model: Any,
        inputs: dict,
        gen_kwargs: dict,
        streamer: TextIteratorStreamer,
        exception_holder: list,
    ) -> None:
        """Run model generation in a thread.

        Args:
            model: The model to run generation on
            inputs: Model inputs
            gen_kwargs: Generation keyword arguments
            streamer: The streamer to signal end on exception
            exception_holder: List to store exception for propagation to main thread

        """
        try:
            with torch.no_grad():
                model.generate(**inputs, **gen_kwargs)
        except KeyboardInterrupt:
            # Silently handle interruption in background thread
            streamer.end()
        except Exception as e:
            # Store exception and signal streamer to end
            exception_holder.append(e)
            streamer.end()

    def _setup_streaming_validator(
        self,
        loader: BaseLoader,
        validate_chunks: bool,
        validation_verbose: bool,
        cot: bool = False,
    ) -> StreamingXGrammarValidator | None:
        """Set up validator for streaming chunk validation.

        Args:
            loader: Model loader with compiler and tokenizer
            validate_chunks: Whether to enable chunk validation
            validation_verbose: Whether to enable verbose validation logging
            cot: Whether Chain-of-Thought mode is enabled. If True, only validates
                content inside <answer> tags.

        Returns:
            Validator instance if enabled, None otherwise

        """
        if not validate_chunks:
            return None

        schema = getattr(self, "_schema", None)
        compiler = getattr(loader, "compiler", None)
        tokenizer = getattr(loader.processor, "tokenizer", None)

        return StreamingXGrammarValidator(
            schema=schema,
            compiler=compiler,
            tokenizer=tokenizer,
            verbose=validation_verbose,
            cot=cot,
        )

    def _validate_streaming_chunk(
        self,
        validator: StreamingXGrammarValidator | None,
        text: str,
    ) -> None:
        """Validate a streaming chunk against the schema.

        Args:
            validator: Validator instance or None if validation disabled.
            text: Text chunk to validate

        Raises:
            ValueError: If validation fails

        """
        if validator:
            is_valid, error_msg = validator.validate_chunk(text)
            if not is_valid:
                raise ValueError(
                    f"Chunk validation failed: {error_msg}\n"
                    f"Accumulated output: {validator.get_accumulated()}"
                )

    def _process_and_yield_token(
        self,
        text: str,
        buffer: list[str],
    ) -> Generator[str, None, None]:
        """Process a token with whitespace-aware buffering and yield output.

        Preserves JSON indentation while providing clean streaming output.

        Args:
            text: Token text to process
            buffer: Buffer list for accumulating whitespace

        Yields:
            Processed text when ready to output

        """
        is_whitespace = text.strip() == ""

        if is_whitespace:
            # Preserve all whitespace to maintain JSON formatting
            buffer.append(text)
        else:
            # Meaningful content - flush buffer first
            if buffer:
                yield "".join(buffer)
                buffer.clear()
            yield text

    def _finalize_streaming_output(
        self,
        thread: threading.Thread,
        full_output: list[str],
        validator: StreamingXGrammarValidator | None,
        parse_result_fn: Callable[[str, str], PredictionResponse],
        user_prompt: str,
    ) -> PredictionResponse:
        """Finalize streaming output and perform final validation.

        Args:
            thread: Generation thread to join
            full_output: List of all generated tokens
            validator: Validator instance or None.
            parse_result_fn: Function to parse final JSON result
            user_prompt: User prompt for parsing

        Returns:
            Final parsed prediction response

        Raises:
            ValueError: If final validation fails

        """
        # Wait for generation to complete
        thread.join()

        # Combine all output
        result_json = "".join(full_output)

        # Final validation if enabled
        if validator:
            is_valid, error_msg, _ = validator.validate_final()
            if not is_valid:
                raise ValueError(f"Final validation failed: {error_msg}")

        return parse_result_fn(result_json, user_prompt)

    def _stream_generator(
        self,
        loader: BaseLoader,
        inputs: dict,
        generation_config: Any,
        user_prompt: str,
        parse_result_fn: Callable[[str, str], PredictionResponse],
        validate_chunks: bool = False,
        validation_verbose: bool = False,
        cot: bool = False,
    ) -> Generator[str, None, PredictionResponse]:
        """Generate streaming output with buffering and optional chunk validation.

        Common streaming implementation used by all predictors.

        Args:
            loader: Model loader with processor and model
            inputs: Model inputs
            generation_config: Generation configuration
            user_prompt: User prompt for parsing
            parse_result_fn: Function to parse final JSON result
            validate_chunks: If True, validates each chunk against schema during streaming.
                For COT mode, only validates content inside <answer> tags.
            validation_verbose: If True, prints validation status for each chunk
            cot: If True, enables Chain-of-Thought streaming mode. The validator
                will track <think> and <answer> sections and only validate JSON
                inside <answer> tags.

        Yields:
            Tokens as strings during generation

        Returns:
            Final PredictionResponse when complete

        Raises:
            ValueError: If chunk validation is enabled and a chunk fails validation

        """
        # Set up streamer and start generation in separate thread
        streamer = TextIteratorStreamer(
            loader.processor.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
            timeout=None,  # Avoid timeout errors during interruption
        )
        gen_kwargs = msgspec.structs.asdict(generation_config)
        gen_kwargs.pop("seed", None)  # Remove seed from kwargs
        gen_kwargs["streamer"] = streamer

        # Exception holder to propagate thread exceptions to main thread
        exception_holder: list[Exception] = []

        thread = threading.Thread(
            target=self._run_generation,
            args=(loader.model, inputs, gen_kwargs, streamer, exception_holder),
            daemon=True,
        )
        thread.start()

        # Set up validator if chunk validation is enabled
        validator = self._setup_streaming_validator(
            loader, validate_chunks, validation_verbose, cot=cot
        )

        # Initialize output collection and buffer
        full_output: list[str] = []
        buffer: list[str] = []

        try:
            # Stream tokens as they're generated
            for text in streamer:
                if text is None or text == "":
                    continue

                full_output.append(text)
                self._validate_streaming_chunk(validator, text)

                # Process token with buffering and yield output
                yield from self._process_and_yield_token(text, buffer)

            # Check if generation thread raised an exception
            if exception_holder:
                raise exception_holder[0]

            # Flush any remaining buffered content
            if buffer:
                yield "".join(buffer)

            # Finalize and return parsed result
            return self._finalize_streaming_output(
                thread, full_output, validator, parse_result_fn, user_prompt
            )

        except (KeyboardInterrupt, SystemExit):
            # Clean up gracefully on user interrupt
            # Mark the streamer as stopped to prevent deadlocks
            try:
                # Try to stop the streamer gracefully
                streamer.end()
            except Exception:
                pass

            # Don't wait for thread - it may be stuck in CUDA operations
            # The daemon flag will handle cleanup when main thread exits
            raise  # Re-raise to propagate to outer handler
        except Exception:
            # For other exceptions, try to clean up thread
            if thread.is_alive():
                thread.join(timeout=1.0)
            raise
