from typing import Callable, Sequence

from ids_peak_common import Interval
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import (
    Manager,
    PEAK_AFL_CONTROLLER_ROI_PRESET_CENTER,
)

from ids_peak_afl.pipeline.features.ifeature import (
    IFeature,
    IRangeFeature,
    IListFeature,
)
from ids_peak_afl.pipeline.features import (
    FocusLimit,
    Hysteresis,
    SkipFrames,
    WeightedRois,
    SharpnessAlgorithm,
    FocusSharpnessAlgorithm,
    SearchAlgorithm,
    FocusSearchAlgorithm,
)

from ids_peak_afl.pipeline.modules.controllers import (
    ControllerMode,
    ControllerType,
)
from ids_peak_afl.pipeline.modules.controllers._internal import (
    callback_manager as _callback_manager,
)
from ids_peak_afl.pipeline.modules.controllers._internal.icontroller import (
    IController,
)

from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
    assert_parameter_type as _assert_parameter_type,
)


class GenericAutoFocus(IController):
    """
    This class provides a generic interface for automatic focus control
    that is used as backend for BasicAutoFocus or AdvancedAutoFocus.

    .. versionadded:: 2.0
    """

    def __init__(self, manager: Manager) -> None:
        """
        Creates a GenericAutoFocus controller

        :param manager: Reference to the manager for device communication

        .. versionadded:: 2.0
        """
        self._manager = manager
        self._controller = self._manager.CreateController(ControllerType.FOCUS)
        self._finished_callback = _callback_manager.ControllerFinishedCallback(
            self._controller
        )

        self._skip_frames = SkipFrames(self._controller)
        self._hysteresis = Hysteresis(self._controller)
        self._weighted_rois = WeightedRois(self._controller)
        self._sharpness_algorithm = SharpnessAlgorithm(self._controller)
        self._search_algorithm = SearchAlgorithm(self._controller)
        self._focus_limit = FocusLimit(self._controller)

    @property
    def name(self) -> str:
        """
        Returns the name of this controller.

        .. versionadded:: 2.0
        """
        return "GenericAutoFocus"

    @property
    def type(self) -> ControllerType:
        """
        Returns the type of this controller.

        .. versionadded:: 2.0
        """
        return ControllerType.FOCUS

    @property
    def mode(self) -> ControllerMode:
        """
        Returns the current operation mode of this controller.

        .. versionadded:: 2.0
        """
        return ControllerMode.from_int(self._controller.GetMode())

    @mode.setter
    def mode(self, mode: ControllerMode) -> None:
        """
        Sets the operation mode.

        .. versionadded:: 2.0
        """
        _assert_parameter_type(mode, ControllerMode, "mode")
        self._controller.SetMode(mode)

    def reset_to_default(self) -> None:
        """
        Resets this controller's state to default.

        .. versionadded:: 2.0
        """
        self.mode = ControllerMode.OFF
        self._skip_frames.value = 2
        self._search_algorithm.value = FocusSearchAlgorithm.GOLDEN_RATIO
        self._sharpness_algorithm.value = FocusSharpnessAlgorithm.TENENGRAD

        limit = self._controller.GetDefaultLimit()
        self._focus_limit.value = Interval(limit.min, limit.max)

        self._hysteresis.value = 8
        self.reset_weighted_rois()

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this controller to an archive.

        :param archive: The archive in which this controller's state will
                        be stored.

        .. versionadded:: 2.0
        """
        for feature in self._features:
            feature.serialize(archive)
        archive.set("Mode", self.mode.string_value)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this controller's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises: ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        for feature in self._features:
            feature.deserialize(archive)
        self.mode = ControllerMode.from_string(
            _get_and_reraise(archive, "Mode", str)
        )

    @property
    def skip_frames(self) -> IRangeFeature[int]:
        """
        Returns the skip frames feature.

        .. versionadded:: 2.0
        """
        return self._skip_frames

    @property
    def weighted_rois(self) -> WeightedRois:
        """
        Returns the weighted ROIs feature.

        .. versionadded:: 2.0
        """
        return self._weighted_rois

    @property
    def hysteresis(self) -> IRangeFeature[int]:
        """
        Returns the hysteresis feature.

        .. versionadded:: 2.0
        """
        return self._hysteresis

    @property
    def sharpness_algorithm(self) -> IListFeature[FocusSharpnessAlgorithm]:
        """
        Returns the sharpness algorithm feature.

        .. versionadded:: 2.0
        """
        return self._sharpness_algorithm

    @property
    def search_algorithm(self) -> IListFeature[FocusSearchAlgorithm]:
        """
        Returns the search algorithm feature.

        .. versionadded:: 2.0
        """
        return self._search_algorithm

    @property
    def focus_limit(self) -> FocusLimit:
        """
        Returns the focus limit feature.

        .. versionadded:: 2.0
        """
        return self._focus_limit

    def reset_weighted_rois(self) -> None:
        """
        Resets the weighted ROIs to the default value.

        .. versionadded:: 2.0
        """
        self._controller.SetROIPreset(
            PEAK_AFL_CONTROLLER_ROI_PRESET_CENTER
        )

    def register_finished_callback(self, callback: Callable[[], None]) -> str:
        """
        Register a callback to be executed when the controller
        finishes executing in the ``ONCE`` mode.

        :param callback: function to be executed.
        :return: callback identifier to unregister for the call
                 to ``unregister_finished_callback``

        .. versionadded:: 2.0
        """
        return self._finished_callback.register(callback)

    def unregister_finished_callback(self, callback_id: str) -> bool:
        """
        Unregisters a callback previously registered with the call to
        ``register_finished_callback``.

        :param callback_id: a string identifier to unregister the callback
                            previously registered with
                            ``register_finished_callback``.
        :return: True if the callback was unregistered, False otherwise

        .. versionadded:: 2.0
        """
        return self._finished_callback.unregister(callback_id)

    @property
    def _features(self) -> Sequence[IFeature]:
        return [
            self._skip_frames,
            self._weighted_rois,
            self._hysteresis,
            self.sharpness_algorithm,
            self.search_algorithm,
            self.focus_limit,
        ]
