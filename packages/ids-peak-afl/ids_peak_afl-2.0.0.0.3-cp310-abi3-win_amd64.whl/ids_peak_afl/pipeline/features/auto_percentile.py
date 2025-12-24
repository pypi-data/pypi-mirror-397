from ids_peak_common.datatypes import Range
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import Controller

from ids_peak_afl.pipeline.features.ifeature import IRangeFeature
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
)


class AutoPercentile(IRangeFeature[float]):
    """
    Auto percentile feature implementation for auto controllers

    This class represents the percentile value used in automatic exposure and
    brightness calculations, specifying which portion of the image histogram is
    considered for adjustments.

    The percentile value typically ranges from 0.0 to 100.0:
        - Lower values (e.g., 10.0) emphasize darker regions of the image.
        - Higher values (e.g., 90.0) emphasize brighter regions of the image.
        - Median values (e.g., 50.0) correspond to the middle brightness of
          the image, treating darker and brighter areas equally.

    .. versionadded:: 2.0
    """

    def __init__(self, controller: Controller) -> None:
        """
        Creates an AutoPercentile feature with the specified controller

        :param controller: The auto controller that will be used to manage the
                           auto percentile parameter.

        .. versionadded:: 2.0
        """
        self._controller = controller

    @property
    def value(self) -> float:
        """
        Returns the auto percentile value

        .. versionadded:: 2.0
        """
        return self._controller.GetAutoPercentile()

    @value.setter
    def value(self, value: float) -> None:
        """
        Sets the percentile value

        :param value: The percentile value to set. Use ``range`` to get the
                      valid range.

        .. versionadded:: 2.0
        """
        self._controller.SetAutoPercentile(value)

    @property
    def range(self) -> Range:
        """
        Returns the valid range for auto percentile values

        .. versionadded:: 2.0
        """
        value_range = self._controller.GetAutoPercentileRange()
        return Range(value_range.min, value_range.max, value_range.inc)

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        archive.set("AutoPercentile", self.value)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        self.value = _get_and_reraise(archive, "AutoPercentile", float)
