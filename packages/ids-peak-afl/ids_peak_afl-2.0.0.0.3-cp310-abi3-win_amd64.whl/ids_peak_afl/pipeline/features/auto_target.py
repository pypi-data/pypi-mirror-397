from ids_peak_common.datatypes import Range
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import Controller

from ids_peak_afl.pipeline.features.ifeature import IRangeFeature
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
)


class AutoTarget(IRangeFeature[int]):
    """
    Auto target feature implementation for auto controllers

    This class represents the target value that the algorithm attempts to
    achieve when adjusting the brightness.

    The target value represents the desired brightness level in the image,
    expressed as a value in the range of 0-255. The auto algorithms will
    adjust exposure, gain, and other parameters to achieve this target
    brightness in the specified region of interest.

    .. versionadded:: 2.0
    """

    def __init__(self, controller: Controller) -> None:
        """
        Creates an AutoTarget feature with the specified controller

        :param controller: The auto controller that will be used to manage the
                           auto target parameter.

        .. versionadded:: 2.0
        """
        self._controller = controller

    @property
    def value(self) -> int:
        """
        Returns the auto target value

        .. versionadded:: 2.0
        """
        return self._controller.GetAutoTarget()

    @value.setter
    def value(self, value: int) -> None:
        """
        Sets the auto target value

        :param value: The target value to set. Use ``range`` to get the
                      valid range.

        .. versionadded:: 2.0
        """
        self._controller.SetAutoTarget(value)

    @property
    def range(self) -> Range:
        """
        Returns the valid range for auto target values

        .. versionadded:: 2.0
        """
        value_range = self._controller.GetAutoTargetRange()
        return Range(value_range.min, value_range.max, value_range.inc)

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        archive.set("AutoTarget", self.value)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        self.value = _get_and_reraise(archive, "AutoTarget", int)
