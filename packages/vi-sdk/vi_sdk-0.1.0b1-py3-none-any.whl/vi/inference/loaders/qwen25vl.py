#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   qwen25vl.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK Qwen2.5-VL loader module.
"""

import sys
from pathlib import Path

from rich import print as rprint
from rich.progress import BarColumn, SpinnerColumn, TimeElapsedColumn
from vi.api.resources.models.results import ModelDownloadResult
from vi.inference.loaders.loader_registry import LoaderRegistry
from vi.inference.utils.module_import import check_imports
from vi.utils.progress import ViProgress

try:
    check_imports(
        packages=["torch", "transformers", "xgrammar"],
        dependency_group="qwen",
        auto_install=True,
    )
except ImportError as e:
    rprint(f"Error: {e}")
    sys.exit(1)

# Import after check to ensure packages are available
import torch
import xgrammar as xgr
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig
from vi.inference.config.qwen25vl import Qwen25VLGenerationConfig
from vi.inference.loaders.hf import HuggingFaceLoader

# Constants
DEFAULT_CONFIG_FILE_NAME = "config.json"
DEFAULT_ATTN_IMPLEMENTATION = "eager"
DEFAULT_DEVICE_MAP = "auto"
MAX_THREADS = 8

# Disable inductor async compile workers to prevent hanging on exit
torch._inductor.config.compile_threads = 1


@LoaderRegistry.register(
    loader_key="qwen25vl",
    model_types=["qwen2_5_vl"],
    architectures=["Qwen2_5_VLForConditionalGeneration"],
)
@LoaderRegistry.register(
    loader_key="cosmosreason1",
    model_types=["qwen2_5_vl"],
    architectures=["Qwen2_5_VLForConditionalGeneration"],
)
@LoaderRegistry.register(
    loader_key="internvl35",
    model_types=["internvl"],
    architectures=["InternVLForConditionalGeneration"],
)
class Qwen25VLLoader(HuggingFaceLoader):
    """Loader for Qwen2.5-VL compatible vision-language models.

    Handles loading of vision-language models from HuggingFace Hub, local paths,
    or Datature Vi fine-tuned models. Supports optional PEFT adapters,
    quantization, and structured output generation via xgrammar.

    Supported model architectures:
        - Qwen2.5-VL (Qwen2_5_VLForConditionalGeneration)
        - InternVL 3.5 (InternVLForConditionalGeneration)
        - Cosmos Reason1 (Qwen2_5_VLForConditionalGeneration)

    Supported configurations:
        - Pretrained models from HuggingFace:
            - "Qwen/Qwen2.5-VL-7B-Instruct"
            - "OpenGVLab/InternVL3.5-8B"
        - Fine-tuned models from Datature Vi platform
        - Local model directories with standard HuggingFace structure
        - 4-bit and 8-bit quantization for memory efficiency
        - PEFT adapters (LoRA, QLoRA)
        - Structured output generation (requires xgrammar)

    Example:
        ```python
        from vi.inference.loaders import Qwen25VLLoader
        from vi.api.resources.models.results import ModelDownloadResult

        # Load Qwen2.5-VL from HuggingFace
        model_meta = ModelDownloadResult(
            model_path="Qwen/Qwen2.5-VL-7B-Instruct",
            adapter_path=None,
            run_config_path=None,
        )
        loader = Qwen25VLLoader(
            model_meta=model_meta,
            trust_remote_code=True,
        )

        # Load InternVL 3.5 from HuggingFace
        model_meta = ModelDownloadResult(
            model_path="OpenGVLab/InternVL3.5-8B",
            adapter_path=None,
            run_config_path=None,
        )
        loader = Qwen25VLLoader(
            model_meta=model_meta,
            trust_remote_code=True,
        )

        # Load fine-tuned Datature model
        model_meta = ModelDownloadResult(
            model_path="./models/run_123/model_full",
            adapter_path="./models/run_123/model_adapter",
            run_config_path="./models/run_123/model_full/run.json",
        )
        loader = Qwen25VLLoader(model_meta=model_meta)

        # Access components
        print(f"Model: {loader.model}")
        print(f"Processor: {loader.processor}")
        print(f"Compiler: {loader.compiler}")
        ```

    """

    _generation_config_class = Qwen25VLGenerationConfig
    _quantization_config: BitsAndBytesConfig | None = None

    def __init__(
        self,
        model_meta: ModelDownloadResult,
        attn_implementation: str = DEFAULT_ATTN_IMPLEMENTATION,
        device_map: dict | str = DEFAULT_DEVICE_MAP,
        low_cpu_mem_usage: bool = False,
        trust_remote_code: bool = False,
        max_threads: int = MAX_THREADS,
    ):
        """Initialize vision-language model loader.

        Supports Qwen2.5-VL, InternVL 3.5, and Cosmos Reason1 architectures.

        Args:
            model_meta: Downloaded model metadata containing paths to model files,
                optional adapter, and run configuration.
            attn_implementation: Attention implementation to use. Options:
                - "eager": Standard PyTorch attention (default, most compatible)
                - "flash_attention_2": Flash Attention 2 (faster, requires flash-attn)
                - "sdpa": Scaled Dot Product Attention (PyTorch 2.0+)
            device_map: Device mapping for model placement. Options:
                - "auto": Automatic placement across available devices
                - "cpu": Force CPU placement
                - "cuda": Force GPU placement
                - dict: Custom layer-to-device mapping
            low_cpu_mem_usage: Whether to use low CPU memory during loading.
                Useful for large models on memory-constrained systems.
            trust_remote_code: Whether to trust remote code in model repositories.
                Required for some custom models. Set to False for security.
            max_threads: Maximum number of threads for xgrammar compiler operations.
                Only used if xgrammar is available and model has run configuration.

        Raises:
            ImportError: If required dependencies are not installed.
            FileNotFoundError: If model files don't exist at specified paths.
            ValueError: If model format is not supported or configuration is invalid.
            RuntimeError: If model loading fails due to hardware constraints.

        Note:
            - For Datature Vi fine-tuned models (with run_config_path), the loader
              automatically loads processor and xgrammar compiler for structured outputs.
            - For pretrained models without run_config_path, only the base model
              is loaded without processor or compiler.
            - xgrammar is optional; if not installed, structured output generation
              will not be available but model loading will still succeed.

        """
        try:
            with ViProgress(
                SpinnerColumn(),
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.2f}%",
                TimeElapsedColumn(),
            ) as progress:
                main_task = progress.add_task("Loading model...", total=100)

                # Load metadata
                progress.update(
                    main_task, advance=20, description="Loading model metadata..."
                )

                if model_meta.run_config_path:
                    self._load_generation_config_from_run_json(model_meta)
                    self._load_metadata_from_run_json(model_meta)

                else:
                    try:
                        self._load_huggingface_generation_config(model_meta)
                        self._load_huggingface_model_config(model_meta)

                    except Exception as e:
                        rprint(f"Error loading model config: {e}")
                        return

                # Setup quantization if enabled
                if self._metadata.get("quantization_enabled"):
                    quant_type = self._metadata.get("quantization_type", "nf4")
                    compute_dtype = self._metadata.get(
                        "compute_precision_type", torch.bfloat16
                    )

                    self._quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_quant_type=quant_type,
                        bnb_4bit_compute_dtype=compute_dtype,
                    )

                # Load model
                progress.update(main_task, description="Loading pretrained weights...")

                model_dtype = self._metadata.get(
                    "compute_precision_type", torch.bfloat16
                )

                self._model = AutoModelForImageTextToText.from_pretrained(
                    model_meta.model_path,
                    attn_implementation=attn_implementation,
                    device_map=device_map,
                    dtype=model_dtype,
                    low_cpu_mem_usage=low_cpu_mem_usage,
                    trust_remote_code=trust_remote_code,
                    config=(
                        str(Path(model_meta.model_path) / DEFAULT_CONFIG_FILE_NAME)
                        if model_meta.run_config_path
                        else None
                    ),
                    quantization_config=self._quantization_config,
                )

                # Load adapter if present
                progress.update(main_task, advance=20, description="Loading adapter...")
                if model_meta.adapter_path:
                    self._model.load_adapter(model_meta.adapter_path)

                self._model.eval()

                # Load processor for Datature models
                progress.update(
                    main_task, advance=20, description="Loading processor..."
                )

                self._processor = AutoProcessor.from_pretrained(
                    model_meta.model_path,
                    use_fast=True,
                    trust_remote_code=trust_remote_code,
                )

                # Load compiler if xgrammar available
                progress.update(
                    main_task, advance=20, description="Loading compiler..."
                )

                self._load_xgrammar_compiler(max_threads)

                progress.update(
                    main_task, completed=100, description="Model loaded successfully"
                )
        except KeyboardInterrupt:
            rprint("\n[yellow]⚠ Model loading cancelled by user[/yellow]")
            sys.exit(0)

    def _load_xgrammar_compiler(self, max_threads: int) -> None:
        """Load xgrammar compiler for structured output generation.

        Args:
            max_threads: Maximum number of threads for compiler.

        """
        if not self._processor:
            return

        tokenizer = self._processor.tokenizer
        full_vocab_size = len(tokenizer.get_vocab())
        config_vocab_size = tokenizer.vocab_size
        actual_vocab_size = max(full_vocab_size, config_vocab_size)

        tokenizer_info = xgr.TokenizerInfo.from_huggingface(
            tokenizer, vocab_size=actual_vocab_size
        )
        self._compiler = xgr.GrammarCompiler(tokenizer_info, max_threads=max_threads)
