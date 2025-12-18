#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   loader_registry.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK loader registry module.
"""

from collections.abc import Callable

from vi.inference.loaders.base_loader import BaseLoader


class LoaderRegistry:
    """Registry for model loaders with plugin-style architecture.

    Allows registration and retrieval of model-specific loaders without tight
    coupling to specific implementations. New model loaders can be added by
    decorating classes with @LoaderRegistry.register().

    Example:
        ```python
        from vi.inference.loaders import BaseLoader, LoaderRegistry


        @LoaderRegistry.register(
            loader_key="my_model",
            model_types=["my_model_type"],
            architectures=["MyModelForVision"],
        )
        class MyModelLoader(BaseLoader):
            def __init__(self, model_meta, **kwargs):
                # Model-specific loading logic
                pass
        ```

    """

    _registry: dict[str, type[BaseLoader]] = {}
    _model_type_mapping: dict[str, str] = {}
    _architecture_mapping: dict[str, str] = {}

    @classmethod
    def register(
        cls,
        loader_key: str,
        model_types: list[str] | None = None,
        architectures: list[str] | None = None,
    ) -> Callable[[type[BaseLoader]], type[BaseLoader]]:
        """Register a model loader.

        Registers a loader class with the registry, associating it with specific
        model types and architectures for automatic detection.

        Args:
            loader_key: Unique identifier for this loader (e.g., "qwen25vl").
            model_types: List of model_type values from config.json that this
                loader handles (e.g., ["qwen2_5_vl"]).
            architectures: List of architecture names from config.json that this
                loader handles (e.g., ["Qwen2_5_VLForConditionalGeneration"]).

        Returns:
            Decorator function that registers the class and returns it unchanged.

        Example:
            ```python
            @LoaderRegistry.register(
                loader_key="qwen25vl",
                model_types=["qwen2_5_vl"],
                architectures=["Qwen2_5_VLForConditionalGeneration"],
            )
            class Qwen25VLLoader(BaseLoader):
                pass
            ```

        """

        def decorator(loader_class: type[BaseLoader]) -> type[BaseLoader]:
            # Register the loader
            cls._registry[loader_key] = loader_class

            # Map model types to loader key
            if model_types:
                for model_type in model_types:
                    cls._model_type_mapping[model_type] = loader_key

            # Map architectures to loader key
            if architectures:
                for arch in architectures:
                    cls._architecture_mapping[arch] = loader_key

            return loader_class

        return decorator

    @classmethod
    def get_loader(
        cls,
        loader_key: str | None = None,
        model_type: str | None = None,
        architecture: str | None = None,
    ) -> type[BaseLoader]:
        """Get a loader class by key, model type, or architecture.

        Retrieves the appropriate loader class based on the provided identifier.
        Useful for both explicit loader selection and automatic detection.

        Args:
            loader_key: Direct loader key (e.g., "qwen25vl").
            model_type: Model type from config.json (e.g., "qwen2_5_vl").
            architecture: Architecture name from config.json (e.g.,
                "Qwen2_5_VLForConditionalGeneration").

        Returns:
            Loader class that can be instantiated with model metadata.

        Raises:
            ValueError: If no arguments provided, multiple arguments provided,
                or if the specified loader/model/architecture is not found.

        Example:
            ```python
            # Get by loader key
            loader_class = LoaderRegistry.get_loader(loader_key="qwen25vl")

            # Get by model type
            loader_class = LoaderRegistry.get_loader(model_type="qwen2_5_vl")

            # Get by architecture
            loader_class = LoaderRegistry.get_loader(
                architecture="Qwen2_5_VLForConditionalGeneration"
            )
            ```

        """
        # Count how many arguments were provided
        args_provided = sum(
            x is not None for x in [loader_key, model_type, architecture]
        )

        if args_provided == 0:
            raise ValueError(
                "Must provide one of: loader_key, model_type, or architecture"
            )

        if args_provided > 1:
            raise ValueError(
                "Provide only one of: loader_key, model_type, or architecture"
            )

        # Get by loader key
        if loader_key:
            if loader_key not in cls._registry:
                raise ValueError(
                    f"Unknown loader: '{loader_key}'. "
                    f"Available loaders: {cls.list_loaders()}"
                )
            return cls._registry[loader_key]

        # Get by model type
        if model_type:
            if model_type not in cls._model_type_mapping:
                raise ValueError(
                    f"No loader registered for model_type '{model_type}'. "
                    f"Supported model types: {cls.list_model_types()}"
                )
            loader_key = cls._model_type_mapping[model_type]
            return cls._registry[loader_key]

        # Get by architecture
        if architecture:
            if architecture not in cls._architecture_mapping:
                raise ValueError(
                    f"No loader registered for architecture '{architecture}'. "
                    f"Supported architectures: {cls.list_architectures()}"
                )
            loader_key = cls._architecture_mapping[architecture]
            return cls._registry[loader_key]

        # Should never reach here due to args_provided check
        raise ValueError("Unexpected error in loader lookup")

    @classmethod
    def list_loaders(cls) -> list[str]:
        """List all registered loader keys.

        Returns:
            List of loader keys that can be used with get_loader().

        Example:
            ```python
            available = LoaderRegistry.list_loaders()
            print(f"Available loaders: {available}")
            # Output: Available loaders: ['qwen25vl', 'llava', ...]
            ```

        """
        return sorted(cls._registry.keys())

    @classmethod
    def list_model_types(cls) -> list[str]:
        """List all supported model types from config.json.

        Returns:
            List of model_type values that can be automatically detected.

        Example:
            ```python
            types = LoaderRegistry.list_model_types()
            print(f"Supported model types: {types}")
            # Output: Supported model types: ['qwen2_5_vl', 'llava', ...]
            ```

        """
        return sorted(cls._model_type_mapping.keys())

    @classmethod
    def list_architectures(cls) -> list[str]:
        """List all supported architecture names from config.json.

        Returns:
            List of architecture names that can be automatically detected.

        Example:
            ```python
            archs = LoaderRegistry.list_architectures()
            print(f"Supported architectures: {archs}")
            # Output: ['Qwen2_5_VLForConditionalGeneration', ...]
            ```

        """
        return sorted(cls._architecture_mapping.keys())

    @classmethod
    def is_registered(
        cls,
        loader_key: str | None = None,
        model_type: str | None = None,
        architecture: str | None = None,
    ) -> bool:
        """Check if a loader is registered for the given identifier.

        Args:
            loader_key: Loader key to check.
            model_type: Model type to check.
            architecture: Architecture name to check.

        Returns:
            True if a loader is registered, False otherwise.

        Example:
            ```python
            if LoaderRegistry.is_registered(model_type="qwen2_5_vl"):
                print("Qwen2.5-VL is supported")
            ```

        """
        try:
            cls.get_loader(
                loader_key=loader_key,
                model_type=model_type,
                architecture=architecture,
            )
            return True
        except ValueError:
            return False
