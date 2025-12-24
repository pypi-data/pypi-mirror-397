from typing import Sequence

from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import (
    Controller,
    PEAK_AFL_CONTROLLER_ALGORITHM_AUTO,
    PEAK_AFL_CONTROLLER_ALGORITHM_GOLDEN_RATIO_SEARCH,
    PEAK_AFL_CONTROLLER_ALGORITHM_HILL_CLIMBING_SEARCH,
    PEAK_AFL_CONTROLLER_ALGORITHM_GLOBAL_SEARCH,
    PEAK_AFL_CONTROLLER_ALGORITHM_FULL_SCAN,
)

from ids_peak_afl.pipeline.datatypes.datatypes import NamedIntEnum

from ids_peak_afl.pipeline.features.ifeature import IListFeature
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
    assert_parameter_type as _assert_parameter_type,
)


class FocusSearchAlgorithm(NamedIntEnum):
    """
    Enumeration of focus search algorithms.

    Defines the algorithms for automatic focus adjustment.
    Each algorithm offers a different balance between speed, accuracy,
    and robustness.

    .. versionadded:: 2.0
    """

    GOLDEN_RATIO = (
        PEAK_AFL_CONTROLLER_ALGORITHM_GOLDEN_RATIO_SEARCH,
        "GoldenRatio",
    )
    """
    Uses the golden section search method to efficiently locate the focus peak.
    Offers fast convergence with good accuracy and typically requires
    fewer steps than full-range scanning.
    """

    HILL_CLIMBING = (
        PEAK_AFL_CONTROLLER_ALGORITHM_HILL_CLIMBING_SEARCH,
        "HillClimbing",
    )
    """
    Iteratively adjusts focus toward higher sharpness values.
    Effective for fine-tuning around the optimal position but may
    converge to a local maximum in complex or low-contrast scenes.
    """

    GLOBAL_SEARCH = (
        PEAK_AFL_CONTROLLER_ALGORITHM_GLOBAL_SEARCH,
        "GlobalSearch",
    )
    """
    Performs a broad search across the entire focus range to find
    the global optimum. More robust against local maxima, offering
    high accuracy at the cost of slower performance.
    """

    FULL_SCAN = (PEAK_AFL_CONTROLLER_ALGORITHM_FULL_SCAN, "FullScan")
    """
    Scans the entire focus range to determine the optimal focus position.
    Provides the highest accuracy but requires the most time to complete.
    Ideal for calibration or other non-real-time applications.
    """


class SearchAlgorithm(IListFeature[FocusSearchAlgorithm]):
    """
    This feature controls which algorithm the automatic focus system uses to
    find the optimal focus position.

    Different algorithms provide different characteristics:
        - AUTO:
          Lets the controller automatically select the default algorithm
        - GOLDEN_RATIO:
          Efficient binary search, good for smooth focus curves
        - HILL_CLIMBING:
          Fast local search, good when starting near optimal focus
        - GLOBAL_SEARCH:
          Comprehensive search, more robust but slower
        - FULL_SCAN:
          Scans entire range, most accurate but slowest

    .. versionadded:: 2.0
    """

    def __init__(self, controller: Controller) -> None:
        """
        Creates an SearchAlgorithm feature with the specified controller

        :param controller: The auto controller that will be used to manage the
                           focus search algorithm parameter.

        .. versionadded:: 2.0
        """
        self._controller = controller

    @property
    def value(self) -> FocusSearchAlgorithm:
        """
        Returns the focus search algorithm

        .. versionadded:: 2.0
        """
        return FocusSearchAlgorithm.from_int(self._controller.GetAlgorithm())

    @value.setter
    def value(self, value: FocusSearchAlgorithm) -> None:
        """
        Sets the focus search algorithm

        :param value: The search algorithm to set. Use ``list`` to get a
                      list of available algorithms.

        .. versionadded:: 2.0
        """
        _assert_parameter_type(value, FocusSearchAlgorithm, "value")
        self._controller.SetAlgorithm(value)

    @property
    def list(self) -> Sequence[FocusSearchAlgorithm]:
        """
        Returns a list of available search algorithms.

        .. versionadded:: 2.0
        """
        algorithms = self._controller.GetAlgorithmList()
        supported = []
        for algorithm in algorithms:
            if algorithm == PEAK_AFL_CONTROLLER_ALGORITHM_AUTO:
                continue
            supported.append(FocusSearchAlgorithm.from_int(algorithm))

        return supported

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        archive.set("SearchAlgorithm", self.value.string_value)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        algorithm = _get_and_reraise(archive, "SearchAlgorithm", str)
        if algorithm == "Auto":
            self.value = FocusSearchAlgorithm.GOLDEN_RATIO
        else:
            self.value = FocusSearchAlgorithm.from_string(algorithm)
