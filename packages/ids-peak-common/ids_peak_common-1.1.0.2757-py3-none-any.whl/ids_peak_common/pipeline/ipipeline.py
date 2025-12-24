from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence

from ids_peak_common.pipeline.modules.imodule import IModule


class IPipeline(ABC):
    """
    Interface defining the structure and behavior of a processing pipeline.

    A pipeline is composed of multiple modules chained together in a defined order.
    When an input is processed, each module's `process` function is called sequentially,
    and the final result is returned.

    .. versionadded:: ids_peak_common 1.1
    .. ingroup:: ids_peak_common_python_pipeline
    """

    @abstractmethod
    def export_settings_to_file(self, file_path: str) -> None:
        """
        Saves the current settings of the pipeline and its modules to a file.

        :param file_path: Path to the file where the settings should be saved.
        """
        pass

    @abstractmethod
    def import_settings_from_file(self, file_path: str) -> None:
        """
        Loads the settings of the pipeline and its modules from a file.

        :param file_path: Path to the file from which settings should be loaded.
        """
        pass

    @abstractmethod
    def export_settings_to_string(self) -> str:
        """
        Returns the current settings of the pipeline and its modules as a string.

        :return: A string representation of the pipeline settings.
        """
        pass

    @abstractmethod
    def import_settings_from_string(self, settings: str) -> None:
        """
        Loads settings for the pipeline and its modules from a string.

        :param settings: String containing serialized pipeline settings.
        """
        pass

    @abstractmethod
    def reset_to_default(self) -> None:
        """
        Resets the pipeline and its modules to their default state.
        """
        pass

    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        Processes the input data through all pipeline modules and returns the result.

        The input data is passed through each module in sequence.

        :param data: The input data to process.

        :return: The processed input.
        """
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """
        Returns the type identifier of the pipeline.

        This is a unique string used to identify the specific pipeline implementation.

        :return: A string representing the pipeline type.
        """
        pass

    @property
    @abstractmethod
    def _modules(self) -> Sequence[IModule]:
        """
        Retrieves the sequence of all modules in the pipeline,
        in execution order.

        :return: A sequence of modules.
        """
        pass
