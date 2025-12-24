from ids_peak_common import Interval
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import (
    Controller,
    peak_afl_controller_limit,
)

from ids_peak_afl.pipeline.features.ifeature import IFeature
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
)


class FocusLimit(IFeature[Interval]):
    """
    Focus limit feature implementation for auto controllers

    Focus limits are useful for:
    - Restricting focus search to a specific distance range
      (e.g., macro, infinity)
    - Preventing the lens from moving to mechanically unsafe positions
    - Optimizing focus speed by limiting the search range
    - Avoiding focus on unwanted objects at certain distances

    .. versionadded:: 2.0
    """

    def __init__(self, controller: Controller) -> None:
        """
        Creates an FocusLimit feature with the specified controller

        :param controller: The auto controller that will be used to manage the
                           focus limit parameter.

        .. versionadded:: 2.0
        """
        self._controller = controller

    @property
    def value(self) -> Interval:
        """
        Returns the focus limit

        .. versionadded:: 2.0
        """
        limit = self._controller.GetLimit()
        return Interval(limit.min, limit.max)

    @value.setter
    def value(self, interval: Interval) -> None:
        """
        Sets the focus limit

        :param interval: The focus limit to set. Use ``range`` to get the
                      valid range.

        .. versionadded:: 2.0
        """
        limit = peak_afl_controller_limit()
        limit.min = int(interval.minimum)
        limit.max = int(interval.maximum)
        self._controller.SetLimit(limit)

    @property
    def range(self) -> Interval:
        """
        Returns the valid interval for focus limit

        .. versionadded:: 2.0
        """
        limit = self._controller.GetDefaultLimit()
        return Interval(limit.min, limit.max)

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        interval = self.value
        archive.set("Min", interval.minimum)
        archive.set("Max", interval.maximum)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        interval_min = _get_and_reraise(archive, "Min", int)
        interval_max = _get_and_reraise(archive, "Max", int)

        self.value = Interval(interval_min, interval_max)
