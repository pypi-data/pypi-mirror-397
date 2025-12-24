from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import Controller
from ids_peak_afl.ids_peak_afl import (
    PEAK_AFL_CONTROLLER_BRIGHTNESS_ALGORITHM_MEDIAN,
    PEAK_AFL_CONTROLLER_BRIGHTNESS_ALGORITHM_MEAN,
)

from ids_peak_afl.pipeline.datatypes import NamedIntEnum
from ids_peak_afl.pipeline.features.ifeature import IFeature
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
    assert_parameter_type as _assert_parameter_type,
)


class BrightnessAnalysisAlgorithm(NamedIntEnum):
    """
    Enumeration of brightness analysis algorithms.

    Defines the available algorithms used to analyze image brightness.
    Each algorithm provides a distinct approach for calculating a
    representative brightness value from pixel intensities.

    .. versionadded:: 2.0
    """

    MEDIAN = (PEAK_AFL_CONTROLLER_BRIGHTNESS_ALGORITHM_MEDIAN, "Median")
    """
    Calculates brightness using the median of pixel intensities.
    This method is more robust against outliers and extreme values,
    providing stable brightness measurements in scenes with high contrast
    or image noise.
    """

    MEAN = (PEAK_AFL_CONTROLLER_BRIGHTNESS_ALGORITHM_MEAN, "Mean")
    """
    Calculates brightness using the arithmetic mean (average) of pixel
    intensities.
    This method offers faster computation and smooth brightness transitions
    but can be influenced by outliers and extreme pixel values.
    """


class BrightnessAlgorithm(IFeature[BrightnessAnalysisAlgorithm]):
    """
    Brightness algorithm feature implementation for auto controllers

    This feature controls how the automatic exposure and brightness systems
    calculate the representative brightness value from the image data.

    Different algorithms provide different characteristics:
        - MEDIAN:
          More robust to outliers and extreme values, provides stable
          results in scenes with high contrast or bright/dark spots
        - MEAN:
          Faster computation, considers all pixel values equally, may be
          influenced by extreme brightness values

    .. versionadded:: 2.0
    """

    def __init__(self, controller: Controller) -> None:
        """
        Creates an BrightnessAlgorithm feature with the specified controller

        :param controller: The auto controller that will be used to manage the
                           auto algorithm parameter.

        .. versionadded:: 2.0
        """
        self._controller = controller

    @property
    def value(self) -> BrightnessAnalysisAlgorithm:
        """
        Returns the brightness algorithm value

        .. versionadded:: 2.0
        """
        return BrightnessAnalysisAlgorithm.from_int(
            self._controller.GetBrightnessAlgorithm()
        )

    @value.setter
    def value(self, value: BrightnessAnalysisAlgorithm) -> None:
        """
        Sets the brightness algorithm value

        :param value: The brightness algorithm value to set. Use ``range`` to
                      get the valid range.

        .. versionadded:: 2.0
        """
        _assert_parameter_type(value, BrightnessAnalysisAlgorithm, "value")
        self._controller.SetBrightnessAlgorithm(value)

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        archive.set("BrightnessAlgorithm", self.value.string_value)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                 if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        self.value = BrightnessAnalysisAlgorithm.from_string(
            _get_and_reraise(archive, "BrightnessAlgorithm", str)
        )
