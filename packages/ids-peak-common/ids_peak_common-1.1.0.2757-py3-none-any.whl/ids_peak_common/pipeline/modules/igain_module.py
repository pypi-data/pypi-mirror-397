from abc import abstractmethod

from ids_peak_common.pipeline.modules.imodule import IModule


class IGain(IModule):
    """
    Interface for modules that provide gain control functionality.

    A gain module consists of a master gain value applied to all channels,
    along with individual gain values for the red, green, and blue channels.

    .. versionadded:: ids_peak_common 1.1
    .. ingroup:: ids_peak_common_python_pipeline_modules
    """

    @property
    @abstractmethod
    def master(self) -> float:
        """
        Retrieves the current master gain value.

        :return: The master gain value.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @master.setter
    @abstractmethod
    def master(self, value: float) -> None:
        """
        Sets the master gain value.

        This value is applied uniformly to all color channels.

        :param value: The master gain value to apply.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @property
    @abstractmethod
    def red(self) -> float:
        """
        Retrieves the gain value for the red channel.

        :return: The red channel gain value.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @red.setter
    @abstractmethod
    def red(self, value: float) -> None:
        """
        Sets the gain value for the red channel.

        :param value: The gain value for the red channel.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @property
    @abstractmethod
    def green(self) -> float:
        """
        Retrieves the gain value for the green channel.

        :return: The green channel gain value.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @green.setter
    @abstractmethod
    def green(self, value: float) -> None:
        """
        Sets the gain value for the green channel.

        :param value: The gain value for the green channel.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @property
    @abstractmethod
    def blue(self) -> float:
        """
        Retrieves the gain value for the blue channel.

        :return: The blue channel gain value.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @blue.setter
    @abstractmethod
    def blue(self, value: float) -> None:
        """
        Sets the gain value for the blue channel.

        :param value: The gain value for the blue channel.

        .. versionadded:: ids_peak_common 1.1
        """
        pass
