from __future__ import annotations

from abc import abstractmethod
from typing import Any

from ids_peak_common.serialization import ISerializable


class IModule(ISerializable):
    """
    Interface for a module used within a pipeline.

    Modules must support enabling/disabling, processing input, and serialization.

    .. versionadded:: ids_peak_common 1.1
    .. ingroup:: ids_peak_common_python_pipeline_modules
    """

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """
        Gets whether the module is currently enabled.

        :return: True if the module is enabled, False otherwise.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @enabled.setter
    @abstractmethod
    def enabled(self, value: bool) -> None:
        """
        Sets the enabled state of the module.

        :param value: True to enable the module, False to disable it.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """
        Returns the type identifier of the module.

        This should be a unique string identifying the specific implementation
        of the module.

        :return: A string identifying the module type.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        Processes input data and returns the result.

        This function is called by the pipeline to process a unit of data.

        :param data: The input data to be processed.

        :return: The processed input.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @abstractmethod
    def reset_to_default(self) -> None:
        """
        Resets the module to its default state. The enabled state is not reset.

        .. versionadded:: ids_peak_common 1.1
        """
        pass
