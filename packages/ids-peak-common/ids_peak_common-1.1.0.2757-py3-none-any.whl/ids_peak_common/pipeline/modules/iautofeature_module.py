from abc import abstractmethod
from typing import Sequence

from ids_peak_common.pipeline.modules.igain_module import IGain
from ids_peak_common.pipeline.modules.imodule import IModule


class IAutoFeature(IModule):
    """
    Interface for modules that provide auto feature functionality.
    Defines the necessary functions that any auto feature module must implement.

    .. versionadded:: ids_peak_common 1.1
    .. ingroup:: ids_peak_common_python_pipeline_modules
    """

    @abstractmethod
    def set_gain_module(self, gain_module: IGain | None) -> None:
        """
        Called by the pipeline to set the gain module for the auto feature module.

        This function provides the gain module that the auto feature module can use
        to apply gain adjustments as needed.

        :param gain_module: The gain module to be controlled by the auto feature module
                            or ``None`` if no gain module should be set.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @abstractmethod
    def set_color_correction_matrix(self, matrix: Sequence[float]) -> None:
        """
        Notifies the auto feature module of the currently used color correction matrix.

        Allows the auto feature module to adjust its algorithms and gain values based on
        the provided color correction matrix.

        :param matrix: The 3x3 color correction matrix currently in use.

        .. versionadded:: ids_peak_common 1.1
        """

        pass
