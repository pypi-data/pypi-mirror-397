from __future__ import annotations

from abc import ABC, abstractmethod


class IFeature(ABC):
    """
    Abstract base class for all image processing pipeline features.

    IFeature defines the common interface that all pipeline features must implement.
    Features represent configurable image processing operations that can be enabled
    or disabled within an image processing pipeline.

    Each feature provides:
    - Enable/disable functionality through the `enabled` property
    - Reset capability to restore default settings via `reset_to_default()`
    - Feature-specific configuration methods (implemented in derived classes)

    Features are typically used within a pipeline context where they can be
    selectively enabled or disabled to customize the image processing workflow.
    When a feature is disabled, it has no effect on the processed image.

    Notes:
        - All derived classes must implement the three abstract methods:
          `enabled` (getter/setter) and `reset_to_default`.
        - The enabled state is independent of the feature's configuration.
          Calling `reset_to_default()` will reset the feature's parameters
          to their default values but will not change the enabled/disabled state.

    ```python
        # Assuming we have a concrete feature implementation
        feature = SomeConcreteFeature()
        # Enable the feature
        feature.enabled = True
        # Check if enabled
        if feature.enabled:
            # Feature will be applied during processing
            pass
        # Reset to default configuration (but keep enabled state)
        feature.reset_to_default()
    ```

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """
        Indicates whether the feature is currently enabled.

        :return: True if enabled; otherwise False.

        .. versionadded:: ids_peak_icv 1.0
        """
        pass

    @enabled.setter
    @abstractmethod
    def enabled(self, value: bool) -> None:
        """
        Enables or disables the feature.
        :param value: Set to True to enable the feature, or False to disable it.

        .. versionadded:: ids_peak_icv 1.0
        """
        pass

    @abstractmethod
    def reset_to_default(self) -> None:
        """
        Restores the feature's default values.
        The enabled state does not change when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        pass
