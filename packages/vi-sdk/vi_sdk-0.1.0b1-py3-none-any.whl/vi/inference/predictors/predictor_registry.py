#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   predictor_registry.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK predictor registry module.
"""

from collections.abc import Callable

from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.predictors.base_predictor import BasePredictor


class PredictorRegistry:
    """Registry for model predictors with plugin-style architecture.

    Maps loader types to appropriate predictor classes. New predictors can be
    added by decorating classes with @PredictorRegistry.register().

    Example:
        ```python
        from vi.inference.predictors import BasePredictor, PredictorRegistry


        @PredictorRegistry.register(
            predictor_key="my_model", loader_types=["MyModelLoader"]
        )
        class MyModelPredictor(BasePredictor):
            def __call__(self, image_path, **kwargs):
                # Model-specific inference logic
                pass
        ```

    """

    _registry: dict[str, type[BasePredictor]] = {}
    _loader_mapping: dict[str, str] = {}

    @classmethod
    def register(
        cls,
        predictor_key: str,
        loader_types: list[str] | None = None,
    ) -> Callable[[type[BasePredictor]], type[BasePredictor]]:
        """Register a model predictor.

        Registers a predictor class with the registry, associating it with
        specific loader types for automatic selection.

        Args:
            predictor_key: Unique identifier for this predictor (e.g., "qwen25vl").
            loader_types: List of loader class names that this predictor handles
                (e.g., ["Qwen25VLLoader"]).

        Returns:
            Decorator function that registers the class and returns it unchanged.

        Example:
            ```python
            @PredictorRegistry.register(
                predictor_key="qwen25vl", loader_types=["Qwen25VLLoader"]
            )
            class Qwen25VLPredictor(BasePredictor):
                pass
            ```

        """

        def decorator(predictor_class: type[BasePredictor]) -> type[BasePredictor]:
            # Register the predictor
            cls._registry[predictor_key] = predictor_class

            # Map loader types to predictor key
            if loader_types:
                for loader_type in loader_types:
                    cls._loader_mapping[loader_type] = predictor_key

            return predictor_class

        return decorator

    @classmethod
    def get_predictor(
        cls,
        predictor_key: str | None = None,
        loader: BaseLoader | None = None,
    ) -> type[BasePredictor]:
        """Get predictor class by key or from loader instance.

        Retrieves the appropriate predictor class based on the provided identifier
        or by detecting the loader type.

        Args:
            predictor_key: Direct predictor key (e.g., "qwen25vl").
            loader: Loader instance to find matching predictor for.

        Returns:
            Predictor class that can be instantiated with a loader.

        Raises:
            ValueError: If no arguments provided, both arguments provided,
                or if the specified predictor/loader is not found.

        Example:
            ```python
            # Get by predictor key
            predictor_class = PredictorRegistry.get_predictor(predictor_key="qwen25vl")

            # Get by loader instance
            loader = Qwen25VLLoader(model_meta)
            predictor_class = PredictorRegistry.get_predictor(loader=loader)
            ```

        """
        # Count how many arguments were provided
        args_provided = sum(x is not None for x in [predictor_key, loader])

        if args_provided == 0:
            raise ValueError("Must provide either predictor_key or loader")

        if args_provided > 1:
            raise ValueError("Provide either predictor_key or loader, not both")

        # Get by predictor key
        if predictor_key:
            if predictor_key not in cls._registry:
                raise ValueError(
                    f"Unknown predictor: '{predictor_key}'. "
                    f"Available predictors: {cls.list_predictors()}"
                )
            return cls._registry[predictor_key]

        # Get by loader instance
        if loader:
            loader_type = type(loader).__name__
            if loader_type not in cls._loader_mapping:
                raise ValueError(
                    f"No predictor registered for loader type '{loader_type}'. "
                    f"Supported loader types: {cls.list_loader_types()}"
                )
            predictor_key = cls._loader_mapping[loader_type]
            return cls._registry[predictor_key]

        # Should never reach here due to args_provided check
        raise ValueError("Unexpected error in predictor lookup")

    @classmethod
    def list_predictors(cls) -> list[str]:
        """List all registered predictor keys.

        Returns:
            List of predictor keys that can be used with get_predictor().

        Example:
            ```python
            available = PredictorRegistry.list_predictors()
            print(f"Available predictors: {available}")
            # Output: Available predictors: ['qwen25vl', 'llava', ...]
            ```

        """
        return sorted(cls._registry.keys())

    @classmethod
    def list_loader_types(cls) -> list[str]:
        """List all loader types that have registered predictors.

        Returns:
            List of loader class names that have associated predictors.

        Example:
            ```python
            types = PredictorRegistry.list_loader_types()
            print(f"Supported loader types: {types}")
            # Output: ['Qwen25VLLoader', 'LLaVALoader', ...]
            ```

        """
        return sorted(cls._loader_mapping.keys())

    @classmethod
    def is_registered(
        cls,
        predictor_key: str | None = None,
        loader: BaseLoader | None = None,
    ) -> bool:
        """Check if a predictor is registered for the given identifier.

        Args:
            predictor_key: Predictor key to check.
            loader: Loader instance to check.

        Returns:
            True if a predictor is registered, False otherwise.

        Example:
            ```python
            if PredictorRegistry.is_registered(predictor_key="qwen25vl"):
                print("Qwen2.5-VL predictor is available")
            ```

        """
        try:
            cls.get_predictor(predictor_key=predictor_key, loader=loader)
            return True
        except ValueError:
            return False
