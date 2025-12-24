from ids_peak_common.datatypes import Range
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import Controller

from ids_peak_afl.pipeline.features.ifeature import IRangeFeature
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
)


class SkipFrames(IRangeFeature[int]):
    """
    This feature controls how many frames the automatic algorithms should
    skip between processing steps.

    Frame skipping is useful for performance optimization and to allow camera
    parameters to stabilize between auto adjustments. For example, setting
    skip frames to 5 means the auto algorithm will process every 6th frame
    (skip 5, process 1).

    .. versionadded:: 2.0
    """

    def __init__(self, controller: Controller) -> None:
        """
        Creates an SkipFrames feature with the specified controller

        :param controller: The auto controller that will be used to manage the
                           skip frames parameter.

        .. versionadded:: 2.0
        """
        self._controller = controller

    @property
    def value(self) -> int:
        """
        Returns the skip frames value

        .. versionadded:: 2.0
        """
        return self._controller.GetSkipFrames()

    @value.setter
    def value(self, value: int) -> None:
        """
        Sets the skip frames value

        :param value: The skip frames value to set. Use ``range`` to get the
                      valid range.

        .. versionadded:: 2.0
        """
        self._controller.SetSkipFrames(value)

    @property
    def range(self) -> Range:
        """
        Returns the valid range for skip frames

        .. versionadded:: 2.0
        """
        skip_range = self._controller.GetSkipFramesRange()
        return Range(skip_range.min, skip_range.max, skip_range.inc)

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        archive.set("SkipFrames", self.value)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        self.value = _get_and_reraise(archive, "SkipFrames", int)
