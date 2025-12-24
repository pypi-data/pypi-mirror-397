from abc import abstractmethod

from ids_peak_common.serialization.iserializable import ISerializable

from ids_peak_afl.pipeline.modules.controllers import (
    ControllerType,
    ControllerMode,
)


class IController(ISerializable):
    """
    Abstract base interface for all automatic controllers

    The ``IController`` class defines the interface that all automatic
    controllers must implement.

    .. versionadded:: 2.0
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of this controller.

        .. versionadded:: 2.0
        """

    @property
    @abstractmethod
    def type(self) -> ControllerType:
        """
        Returns the type of this controller.

        .. versionadded:: 2.0
        """

    @property
    @abstractmethod
    def mode(self) -> ControllerMode:
        """
        Gets the current operation mode of this controller.

        .. versionadded:: 2.0
        """

    @mode.setter
    @abstractmethod
    def mode(self, mode: ControllerMode) -> None:
        """
        Sets the operation mode for this controller

        .. versionadded:: 2.0
        """

    @abstractmethod
    def reset_to_default(self) -> None:
        """
        Resets this controller's state to default.

        .. versionadded:: 2.0
        """
