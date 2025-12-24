from typing import Sequence

from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import (
    Controller,
    PEAK_AFL_CONTROLLER_SHARPNESS_ALGORITHM_AUTO,
    PEAK_AFL_CONTROLLER_SHARPNESS_ALGORITHM_TENENGRAD,
    PEAK_AFL_CONTROLLER_SHARPNESS_ALGORITHM_SOBEL,
    PEAK_AFL_CONTROLLER_SHARPNESS_ALGORITHM_MEAN_SCORE,
    PEAK_AFL_CONTROLLER_SHARPNESS_ALGORITHM_HISTOGRAM_VARIANCE,
)

from ids_peak_afl.pipeline.datatypes.datatypes import NamedIntEnum
from ids_peak_afl.pipeline.features.ifeature import IListFeature
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
    assert_parameter_type as _assert_parameter_type,
)


class FocusSharpnessAlgorithm(NamedIntEnum):
    """
    Enumeration of focus sharpness algorithms.

    Defines the available methods used to measure image sharpness
    during autofocus operations.

    .. versionadded:: 2.0
    """

    TENENGRAD = (
        PEAK_AFL_CONTROLLER_SHARPNESS_ALGORITHM_TENENGRAD,
        "Tenengrad",
    )
    """
    Measures sharpness using gradient magnitude calculations.
    Effective for images with clear edges and strong contrast, and
    offers good overall performance with low computational cost.
    """

    SOBEL = (PEAK_AFL_CONTROLLER_SHARPNESS_ALGORITHM_SOBEL, "Sobel")
    """
    Evaluates sharpness using Sobel edge detection operators.
    Provides high sensitivity to fine details and textures but
    can be more susceptible to image noise.
    """

    MEAN_SCORE = (
        PEAK_AFL_CONTROLLER_SHARPNESS_ALGORITHM_MEAN_SCORE,
        "MeanScore",
    )
    """
    Computes sharpness using statistical measures of image content.
    Delivers stable results across diverse scenes but may be less
    responsive to fine detail variations.
    """

    HISTOGRAM_VARIANCE = (
        PEAK_AFL_CONTROLLER_SHARPNESS_ALGORITHM_HISTOGRAM_VARIANCE,
        "HistogramVariance",
    )
    """
    Determines sharpness from intensity variance within the image histogram.
    Performs well in evenly illuminated scenes with good contrast.
    """


class SharpnessAlgorithm(IListFeature[FocusSharpnessAlgorithm]):
    """
    This feature controls how the automatic focus system measures image
    sharpness to determine the optimal focus position.

    Different algorithms provide different characteristics:
        - AUTO:
          Lets the controller automatically select the best algorithm
        - TENENGRAD:
          Gradient-based, good for high-contrast edges
        - SOBEL:
          Edge detection based, robust for various scene types
        - MEAN_SCORE:
          Statistical approach, good for textured surfaces
        - HISTOGRAM_VARIANCE:
          Variance-based, effective for uniform lighting

    .. versionadded:: 2.0
    """

    def __init__(self, controller: Controller) -> None:
        """
        Creates an SharpnessAlgorithm feature with the specified controller

        :param controller: The auto controller that will be used to manage the
                           sharpness algorithm parameter.

        .. versionadded:: 2.0
        """
        self._controller = controller

    @property
    def value(self) -> FocusSharpnessAlgorithm:
        """
        Returns the sharpness algorithm

        .. versionadded:: 2.0
        """
        return FocusSharpnessAlgorithm.from_int(
            self._controller.GetSharpnessAlgorithm()
        )

    @value.setter
    def value(self, value: FocusSharpnessAlgorithm) -> None:
        """
        Sets the sharpness algorithm

        :param value: The percentile value to set. Use ``list`` to get a
                      list of available algorithms.

        .. versionadded:: 2.0
        """
        _assert_parameter_type(value, FocusSharpnessAlgorithm, "value")
        self._controller.SetSharpnessAlgorithm(value)

    @property
    def list(self) -> Sequence[FocusSharpnessAlgorithm]:
        """
        Returns a list of available sharpness algorithms.

        .. versionadded:: 2.0
        """
        algorithms = self._controller.GetSharpnessAlgorithmList()
        supported = []
        for algorithm in algorithms:
            if algorithm == PEAK_AFL_CONTROLLER_SHARPNESS_ALGORITHM_AUTO:
                continue

            supported.append(FocusSharpnessAlgorithm.from_int(algorithm))

        return supported

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        archive.set("SharpnessAlgorithm", self.value.string_value)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        algorithm = _get_and_reraise(archive, "SharpnessAlgorithm", str)
        if algorithm == "Auto":
            self.value = FocusSharpnessAlgorithm.TENENGRAD
        else:
            self.value = FocusSharpnessAlgorithm.from_string(algorithm)
