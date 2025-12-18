#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   hf.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK HuggingFace loader module.
"""

import sys

import msgspec
from rich import print as rprint
from vi.api.resources.models.results import ModelDownloadResult
from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.utils.module_import import check_imports

try:
    check_imports(
        packages=[
            "transformers",
        ],
        dependency_group="inference",
        auto_install=False,
    )
except ImportError as e:
    rprint(f"Error: {e}")
    sys.exit(1)

from transformers import AutoConfig, GenerationConfig
from vi.inference.config.base_config import ViGenerationConfig


class HuggingFaceLoader(BaseLoader):
    """Base loader for HuggingFace models.

    Provides common functionality for loading HuggingFace models by extracting
    configuration from the model's config.json file. This class serves as a
    base for specific model loaders that need HuggingFace compatibility.

    The loader automatically detects model architecture, type, and other
    configuration parameters from the HuggingFace model configuration.

    Attributes:
        Inherits all attributes from BaseLoader:
            model: The loaded model instance.
            processor: The processor for input preprocessing (optional).
            compiler: The compiler for structured outputs (optional).
            generation_config: Generation config.
            metadata: Dictionary containing model metadata.

    Note:
        This is an abstract base class. Use specific model loaders like
        Qwen25VLLoader for actual model loading.

    """

    _generation_config_class: type[ViGenerationConfig] = ViGenerationConfig

    def _load_huggingface_generation_config(
        self, model_meta: ModelDownloadResult
    ) -> None:
        """Load generation config from HuggingFace config.json."""
        generation_config = GenerationConfig.from_pretrained(model_meta.model_path)
        self._generation_config = msgspec.convert(
            generation_config.to_dict(), type=self._generation_config_class
        )

    def _load_huggingface_model_config(self, model_meta: ModelDownloadResult) -> None:
        """Load model configuration from HuggingFace config.json.

        Extracts model configuration from the HuggingFace model's config.json file
        and populates the metadata dictionary with model type, architectures,
        compute precision, and other relevant information.

        Args:
            model_meta: Model metadata containing the model path where config.json
                is located. The model_path should point to a directory containing
                the HuggingFace model files.

        Raises:
            FileNotFoundError: If config.json is not found in the model directory.
            ValueError: If the config.json file is malformed or missing required fields.
            ImportError: If transformers library is not available.

        Note:
            This method sets default values for task_type, system_prompt, and
            quantization_enabled if they are not present in the configuration.

        """
        config = AutoConfig.from_pretrained(model_meta.model_path)
        self._metadata["model_type"] = config.model_type
        self._metadata["architectures"] = config.architectures
        self._metadata["compute_precision_type"] = config.dtype

        # Set defaults for pretrained models
        self._metadata.setdefault("task_type", "generic")
        self._metadata.setdefault("system_prompt", "")
        self._metadata.setdefault("quantization_enabled", False)
