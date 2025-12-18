#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   nvila.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK NVILA predictor module.
"""

import sys
from collections.abc import Generator

import msgspec
from rich import print as rprint
from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.messages import create_system_message, create_user_message_with_image
from vi.inference.predictors.base_predictor import BasePredictor
from vi.inference.predictors.predictor_registry import PredictorRegistry
from vi.inference.predictors.streaming import StreamingMixin
from vi.inference.task_types import PredictionResponse, TaskAssistant, consts
from vi.inference.utils.module_import import check_imports
from vi.inference.utils.postprocessing import parse_result
from vi.utils.graceful_exit import graceful_exit

try:
    check_imports(
        packages=["torch", "xgrammar", "qwen_vl_utils"],
        dependency_group="nvila",
        auto_install=True,
    )
except ImportError as e:
    rprint(f"Error: {e}")
    sys.exit(1)

# Import after check to ensure packages are available
import torch
from qwen_vl_utils import process_vision_info
from vi.inference.config.nvila import NVILAGenerationConfig
from vi.inference.logits_processors import (
    ConditionalXGrammarLogitsProcessor,
    DebugXGrammarLogitsProcessor,
)

# Disable inductor async compile workers to prevent hanging on exit
torch._inductor.config.compile_threads = 1


@PredictorRegistry.register(
    predictor_key="nvila",
    loader_types=["NVILALoader"],
)
class NVILAPredictor(BasePredictor, StreamingMixin):
    """NVILA predictor for vision-language tasks.

    Handles NVILA-specific preprocessing, inference, and output parsing for
    vision-language tasks. Works with Datature Vi fine-tuned models that
    include structured output generation via xgrammar.

    Supported task types:
        - Visual Question Answering (VQA): User prompt is required in the form of a question
        - Phrase Grounding: User prompt is optional (uses default prompt if not provided)

    Example:
        ```python
        from vi.inference.loaders import ViLoader
        from vi.inference.predictors import NVILAPredictor

        # Load model and create predictor
        loader = ViLoader.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")
        predictor = NVILAPredictor(loader)

        # Run inference
        result = predictor(
            source="image.jpg", user_prompt="What objects are in this image?"
        )
        print(result)
        ```

    Note:
        This predictor is designed for Datature Vi fine-tuned models with
        processor and xgrammar compiler. For pretrained models without these
        components, you'll need to implement a custom predictor.

    """

    _loader: BaseLoader
    _schema: TaskAssistant
    _user_prompt: str | None

    def __init__(self, loader: BaseLoader):
        """Initialize the NVILA predictor.

        Sets up the predictor with a loaded model and configures the task-specific
        schema and prompts based on the model's training task type.

        Args:
            loader: Loaded model instance (should be NVILALoader). Must contain:
                - model: The loaded model
                - processor: Tokenizer and image processor
                - compiler: xgrammar compiler for structured outputs
                - metadata: Including task_type and system_prompt

        Raises:
            ImportError: If required dependencies (qwen_vl_utils, xgrammar) are not installed.
            AttributeError: If the loader doesn't contain processor or compiler,
                which indicates it's not a properly configured Datature Vi model.
            KeyError: If required metadata fields are missing.

        Example:
            ```python
            from vi.inference.loaders import ViLoader
            from vi.inference.predictors import NVILAPredictor

            # Load Datature model
            loader = ViLoader.from_pretrained("path/to/datature/model")
            predictor = NVILAPredictor(loader)

            # Run inference
            result = predictor(source="image.jpg")
            print(result)
            ```

        Note:
            This predictor requires a Datature Vi fine-tuned model with:
            - Processor for input preprocessing
            - xgrammar compiler for structured output generation
            - Task type metadata (VQA or phrase grounding)

            For pretrained models without these components, implement a custom
            predictor or use a different model architecture that doesn't require
            structured outputs.

        See Also:
            - `ViLoader`: Loading models with automatic detection
            - `NVILALoader`: NVILA model loader
            - [Inference Guide](../guide/inference.md): Complete inference workflow


        """
        self._loader = loader

        # Validate loader has required components
        if not hasattr(loader, "processor") or loader.processor is None:
            raise AttributeError(
                "NVILA predictor requires a loader with a processor. "
                "The provided loader may not be properly configured. "
                "Ensure you're using a Datature Vi fine-tuned model with run configuration."
            )

        if not hasattr(loader, "compiler") or loader.compiler is None:
            raise AttributeError(
                "NVILA predictor requires a loader with an xgrammar compiler. "
                "This predictor is designed for Datature Vi fine-tuned models with "
                "structured output generation. For pretrained models, please implement "
                "a custom predictor or install xgrammar: pip install xgrammar"
            )

        # Validate metadata has required fields
        if "task_type" not in self._loader.metadata:
            raise KeyError(
                "Loader metadata missing 'task_type'. This predictor requires a "
                "Datature Vi fine-tuned model with task type configuration."
            )

        # Setup task-specific schema and prompts
        self._schema = consts.TASK_TYPE_TO_ASSISTANT_MAP[
            consts.TaskType(self._loader.metadata["task_type"])
        ]
        self._user_prompt = consts.TASK_TYPE_TO_USER_PROMPT_MAP[
            consts.TaskType(self._loader.metadata["task_type"])
        ]

    def _parse_result(self, raw_output: str, user_prompt: str) -> PredictionResponse:
        """Parse generated output into appropriate response type.

        Wrapper around the shared parse_result utility function.

        Args:
            raw_output: Raw model output (may contain COT tags or code blocks).
            user_prompt: The user prompt used for inference.

        Returns:
            Parsed prediction response based on task type.

        """
        task_type = consts.TaskType(self._loader.metadata["task_type"])
        return parse_result(
            raw_output=raw_output,
            user_prompt=user_prompt,
            task_type=task_type,
            schema=self._schema,
        )

    def __call__(
        self,
        source: str,
        user_prompt: str | None = None,
        generation_config: NVILAGenerationConfig | dict | None = None,
        stream: bool = False,
        cot: bool = False,
        validate_chunks: bool = True,
        validation_verbose: bool = False,
    ) -> PredictionResponse | Generator[str, None, PredictionResponse]:
        """Perform inference on an image with optional custom prompt.

        This method processes an image and optional text prompt through the NVILA
        model, generating structured output based on the configured task type.
        It handles vision processing, text generation, and response formatting.

        Args:
            source: Path to the input image file
            user_prompt: Optional custom prompt to override the default task prompt
            generation_config: Generation configuration.
                If None, uses the generation config from the loader.
            stream: If True, returns a generator that yields tokens (as strings) as they're
                generated in real-time. The generator also returns the final PredictionResponse
                when complete. If False, waits for complete generation and returns
                the parsed PredictionResponse. Defaults to True.
            cot: If True, enables chain-of-thought mode using ConditionalXGrammarLogitsProcessor,
                which allows free-form reasoning before structured output. The model can generate
                free-form text before the <answer>...</answer> section containing structured JSON.
                If False, uses DebugXGrammarLogitsProcessor for strict schema enforcement.
                Defaults to False.
            validate_chunks: If True, validates each chunk against the schema during streaming.
                This provides early error detection but adds overhead. Only works when stream=True.
                Defaults to True.
            validation_verbose: If True, prints validation status for each chunk. Only works
                when validate_chunks=True. Defaults to False.

        Returns:
            If stream=False: Task-specific prediction results. The exact format depends
            on the model's training task:
            - VQA: VQAResponse with question-answer pairs
            - Phrase Grounding: PhraseGroundingResponse with bounding boxes

            If stream=True: A generator that yields strings (tokens) as they're generated.
            The generator returns the final PredictionResponse when complete (accessible
            via StopIteration.value or yield from).

        Raises:
            FileNotFoundError: If the image file doesn't exist.
            ValueError: If the image format is not supported.
            RuntimeError: If model inference fails.
            ImportError: If required dependencies are not installed.

        Example:
            ```python
            from vi.inference.loaders import ViLoader
            from vi.inference.predictors import NVILAPredictor

            # Load model
            loader = ViLoader.from_pretrained("path/to/datature/model")
            predictor = NVILAPredictor(loader)

            # Streaming generation (default behavior)
            # Note: For easier streaming handling, use ViModel instead
            gen = predictor(source="image.jpg")
            for token in gen:
                print(token, end="", flush=True)
            # The final result is in the generator's return value

            # Non-streaming inference - get the parsed PredictionResponse
            result = predictor(source="image.jpg", stream=False)
            print(f"Result: {result}")

            # With additional generation parameters (deterministic by default, seed=0)
            for token in predictor(
                source="image.jpg",
                user_prompt="Describe this image",
                generation_config=NVILAGenerationConfig(
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    seed=42,  # Custom seed for reproducible outputs
                ),
            ):
                print(token, end="", flush=True)

            # For random generation (non-deterministic)
            result = predictor(
                source="image.jpg",
                generation_config={"seed": -1},  # Disable seeding for randomness
                stream=False,
            )
            ```

        Note:
            - Uses NVILA-specific preprocessing via qwen_vl_utils.process_vision_info()
            - Enforces structured output via xgrammar for JSON schema compliance
            - Generation is deterministic by default (do_sample=False)
            - System prompt from training is always included in the conversation

        See Also:
            - `ViLoader`: Loading models with automatic detection
            - `ViPredictor`: Automatic predictor selection
            - [Inference Guide](../guide/inference.md): Complete workflow and examples

        """
        if user_prompt:
            self._user_prompt = user_prompt

        if isinstance(generation_config, dict):
            generation_config = NVILAGenerationConfig(**generation_config)
        elif not generation_config:
            generation_config = (
                self._loader.generation_config or NVILAGenerationConfig()
            )

        # Validate required components are present
        if self._loader.compiler is None:
            raise RuntimeError(
                "Compiler not available for structured output generation"
            )

        if self._loader.processor is None:
            raise RuntimeError("Processor not available for input preprocessing")

        # Build system prompt, adding COT format instruction if enabled
        system_prompt = self._loader.metadata["system_prompt"]
        if cot:
            system_prompt = f"{system_prompt}{consts.COT_SYSTEM_PROMPT_SUFFIX}"

        messages = [
            create_system_message(system_prompt),
            create_user_message_with_image(source, self._user_prompt),
        ]

        if self._schema:
            compiled_grammar = self._loader.compiler.compile_json_schema(self._schema)
            if cot:
                xgr_logits_processor = (
                    ConditionalXGrammarLogitsProcessor.from_compiled_grammar(
                        compiled_grammar,
                        self._loader.processor.tokenizer,
                        suffix_string="</answer>",
                    )
                )
            else:
                xgr_logits_processor = (
                    DebugXGrammarLogitsProcessor.from_compiled_grammar(
                        compiled_grammar,
                        self._loader.processor.tokenizer,
                    )
                )
            logits_processor = [xgr_logits_processor]
        else:
            logits_processor = []

        input_text = self._loader.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        image_inputs, _ = process_vision_info(messages)

        inputs = self._loader.processor(
            text=[input_text], images=image_inputs, padding=True, return_tensors="pt"
        ).to(self._loader.model.device)

        generation_config.logits_processor = logits_processor
        generation_config.pad_token_id = self._loader.processor.tokenizer.eos_token_id
        generation_config.eos_token_id = self._loader.processor.tokenizer.eos_token_id

        # Apply seed for reproducibility (unless seed=-1 for random generation)
        if generation_config.seed != -1:
            torch.manual_seed(generation_config.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(generation_config.seed)

        gen_kwargs = msgspec.structs.asdict(generation_config)
        gen_kwargs.pop("seed", None)  # Remove seed from kwargs

        # Streaming generation
        if stream:
            return self._stream_generator(
                loader=self._loader,
                inputs=inputs,
                generation_config=generation_config,
                user_prompt=self._user_prompt or "",
                parse_result_fn=self._parse_result,
                validate_chunks=validate_chunks,
                validation_verbose=validation_verbose,
                cot=cot,
            )

        # Non-streaming generation (original behavior)
        with graceful_exit("Model prediction cancelled by user"):
            with torch.no_grad():
                output_ids = self._loader.model.generate(
                    **inputs,
                    **gen_kwargs,
                )

            trimmed_output_ids = output_ids[:, inputs["input_ids"].shape[1] :]
            result_json = self._loader.processor.batch_decode(
                trimmed_output_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )[0]

            return self._parse_result(
                raw_output=result_json,
                user_prompt=self._user_prompt or "",
            )
