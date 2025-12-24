from ids_peak_common.datatypes import Range
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import Controller

from ids_peak_afl.pipeline.features.ifeature import IRangeFeature
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
)


class AutoTolerance(IRangeFeature[int]):
    """
    Auto tolerance feature implementation for auto controllers

    The tolerance value defines an acceptable deviation from the target
    brightness. For example, if the target is 128 and tolerance is 10, then
    brightness values between 118 and 138 would be considered acceptable, and
    the auto algorithm would pause or finish adjustments.

    .. versionadded:: 2.0
    """

    def __init__(self, controller: Controller) -> None:
        """
        Creates an AutoTolerance feature with the specified controller

        :param controller: The auto controller that will be used to manage the
                           auto tolerance parameter.

        .. versionadded:: 2.0
        """
        self._controller = controller

    @property
    def value(self) -> int:
        """
        Returns the auto tolerance value

        .. versionadded:: 2.0
        """
        return self._controller.GetAutoTolerance()

    @value.setter
    def value(self, value: int) -> None:
        """
        Sets the tolerance value

        :param value: The tolerance value to set. Use ``range`` to get the
                      valid range.

        .. versionadded:: 2.0
        """
        self._controller.SetAutoTolerance(value)

    @property
    def range(self) -> Range:
        """
        Returns the valid range for auto tolerance values

        .. versionadded:: 2.0
        """
        value_range = self._controller.GetAutoToleranceRange()
        return Range(value_range.min, value_range.max, value_range.inc)

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        archive.set("AutoTolerance", self.value)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        self.value = _get_and_reraise(archive, "AutoTolerance", int)
