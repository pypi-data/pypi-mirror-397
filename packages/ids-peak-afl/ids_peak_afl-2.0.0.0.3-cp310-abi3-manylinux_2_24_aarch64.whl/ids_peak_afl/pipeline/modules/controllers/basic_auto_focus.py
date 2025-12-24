from typing import Callable, Sequence

from ids_peak_common import Range, Interval
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import Manager

from ids_peak_afl.exceptions import InvalidParameterException

from ids_peak_afl.pipeline.features import (
    WeightedRoi,
    FocusSharpnessAlgorithm,
    FocusSearchAlgorithm,
)
from ids_peak_afl.pipeline.modules.controllers import (
    ControllerMode,
    ControllerType,
)
from ids_peak_afl.pipeline.features.weighted_rois import RoiPreset

from ids_peak_afl.pipeline.modules.controllers._internal import (
    generic_auto_focus as _generic_auto_focus,
)
from ids_peak_afl.pipeline.modules.controllers._internal.icontroller import (
    IController,
)
from ids_peak_afl.pipeline._internal.utils import (
    assert_parameter_type as _assert_parameter_type,
)


class BasicAutoFocus(IController):
    """
    This class provides a simplified interface for automatic focus
    control by adjusting the camera’s focus stepper parameter.

    .. note:: For more granular control, consider using
              ``AdvancedAutoFocus``

    .. versionadded:: 2.0
    """

    def __init__(self, manager: Manager) -> None:
        """
        Creates a BasicAutoFocus controller.

        :param manager: Reference to the manager for device communication
        :param callback: Processing callback that will be invoked when
                         an image has been processed

        .. versionadded:: 2.0
        """
        self._manager = manager
        self._generic_controller = _generic_auto_focus.GenericAutoFocus(
            manager
        )

    @property
    def name(self) -> str:
        """
        Returns the name of this controller.

        .. versionadded:: 2.0
        """
        return "BasicAutoFocus"

    @property
    def type(self) -> ControllerType:
        """
        Returns the type of this controller.

        .. versionadded:: 2.0
        """
        return ControllerType.FOCUS

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this controller to an archive.

        :param archive: The archive in which this controller's state will
                        be stored.

        .. versionadded:: 2.0
        """
        self._generic_controller.serialize(archive)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this controller's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        self._generic_controller.deserialize(archive)

    @property
    def mode(self) -> ControllerMode:
        """
        Gets the current operation mode of this controller.

        .. versionadded:: 2.0
        """
        return self._generic_controller.mode

    @mode.setter
    def mode(self, mode: ControllerMode) -> None:
        """
        Sets the operation mode of this controller.

        .. versionadded:: 2.0
        """
        _assert_parameter_type(mode, ControllerMode, "mode")
        self._generic_controller.mode = mode

    def reset_to_default(self) -> None:
        """
        Resets this controller's state to default.

        This sets all properties to their default values.

        .. versionadded:: 2.0
        """
        self._generic_controller.reset_to_default()

    @property
    def skip_frames_range(self) -> Range:
        """
        Returns the valid range for ``skip_frames``.

        .. versionadded:: 2.0
        """
        return self._generic_controller.skip_frames.range

    @property
    def skip_frames(self) -> int:
        """
        Returns the number of frames to skip between processed steps.

        Skip frames controls how many images are skipped between processing
        steps. Processing every N-th frame reduces computational load but
        may decrease responsiveness.

        .. versionadded:: 2.0
        """
        return self._generic_controller.skip_frames.value

    @skip_frames.setter
    def skip_frames(self, skip_frames: int) -> None:
        """
        Sets the skip frames value.

        :param skip_frames: The number of frames to skip between processing
                            steps

        .. note:: Check ``skip_frames_range`` before calling this method to
                 ensure the value is valid.

        .. versionadded:: 2.0
        """
        self._generic_controller.skip_frames.value = skip_frames

    @property
    def weighted_rois(self) -> list[WeightedRoi]:
        """
        Returns the weighted regions of interest (ROIs) that are used by the
        focus algorithm to determine the current image sharpness.

        Weighted ROIs are useful for prioritizing important subjects
        in the scene.

        .. versionadded:: 2.0
        """

        return self._generic_controller.weighted_rois.value

    @weighted_rois.setter
    def weighted_rois(
        self, weighted_rois: list[WeightedRoi] | WeightedRoi
    ) -> None:
        """
        Sets the weighted regions of interest (ROIs) that are used by the focus
        algorithm to determine the current image sharpness.

        :param weighted_rois: List of weighted ROIs or single weighted roi.
        """

        if isinstance(weighted_rois, WeightedRoi):
            self._generic_controller.weighted_rois.set_single(weighted_rois)
            return
        elif isinstance(weighted_rois, list):
            self._generic_controller.weighted_rois.value = weighted_rois
        else:
            raise InvalidParameterException(
                f"Invalid type for parameter `weighted_rois`, "
                f"expected `list[WeightedRoi]` or `WeightedRoi`, got `{type(weighted_rois)}`"
            )

    def reset_weighted_rois(self) -> None:
        """
        Resets the weighted roi to a single ``RoiPreset.CENTER``.
        """

        self._generic_controller.weighted_rois.set_preset(RoiPreset.CENTER)

    @property
    def hysteresis_range(self) -> Range:
        """
        Returns the valid range for ``hysteresis``.

        .. versionadded:: 2.0
        """
        return self._generic_controller.hysteresis.range

    @property
    def hysteresis(self) -> int:
        """
        Gets the current hysteresis value.

        :return: The currently configured hysteresis value

        .. versionadded:: 2.0
        """
        return self._generic_controller.hysteresis.value

    @hysteresis.setter
    def hysteresis(self, value: int) -> None:
        """
        Sets the hysteresis value.

        :param value: The hysteresis value

        .. note:: Check ``hysteresis_range`` before calling this method to
                  ensure the value is valid.

        .. versionadded:: 2.0
        """
        self._generic_controller.hysteresis.value = value

    @property
    def sharpness_algorithm_list(self) -> Sequence[FocusSharpnessAlgorithm]:
        """
        Returns a list of valid values for ``sharpness_algorithm``.

        .. versionadded:: 2.0
        """
        return self._generic_controller.sharpness_algorithm.list

    @property
    def sharpness_algorithm(self) -> FocusSharpnessAlgorithm:
        """
        Gets the current sharpness algorithm.

        :return: The currently configured sharpness algorithm

        .. versionadded:: 2.0
        """
        return self._generic_controller.sharpness_algorithm.value

    @sharpness_algorithm.setter
    def sharpness_algorithm(self, value: FocusSharpnessAlgorithm) -> None:
        """
        Sets the sharpness algorithm.

        :param value: The sharpness algorithm

        .. note:: Check ``sharpness_algorithm_list`` before calling this
                  method to ensure the value is valid.

        .. versionadded:: 2.0
        """
        _assert_parameter_type(value, FocusSharpnessAlgorithm, "value")
        self._generic_controller.sharpness_algorithm.value = value

    @property
    def search_algorithm_list(self) -> Sequence[FocusSearchAlgorithm]:
        """
        Returns a list of valid values for ``search_algorithm``.

        .. versionadded:: 2.0
        """
        return self._generic_controller.search_algorithm.list

    @property
    def search_algorithm(self) -> FocusSearchAlgorithm:
        """
        Gets the current search algorithm.

        :return: The currently configured search algorithm

        .. versionadded:: 2.0
        """
        return self._generic_controller.search_algorithm.value

    @search_algorithm.setter
    def search_algorithm(self, value: FocusSearchAlgorithm) -> None:
        """
        Sets the search algorithm.

        :param value: The search algorithm

        .. note:: Check ``search_algorithm_list`` before calling this
                  method to ensure the value is valid.

        .. versionadded:: 2.0
        """
        _assert_parameter_type(value, FocusSearchAlgorithm, "value")
        self._generic_controller.search_algorithm.value = value

    @property
    def focus_limit_range(self) -> Interval:
        """
        Returns the valid range for ``focus_limit``.

        .. versionadded:: 2.0
        """
        return self._generic_controller.focus_limit.range

    @property
    def focus_limit(self) -> Interval:
        """
        Returns the focus limit interval.

        The focus limit defines an interval specifying the minimum and
        maximum focus values within which the focus can be adjusted.

        .. versionadded:: 2.0
        """
        return self._generic_controller.focus_limit.value

    @focus_limit.setter
    def focus_limit(self, value: Interval) -> None:
        """
        Sets the focus limit.

        :param value: The interval defining the minimum and maximum
               focus limits

        .. versionadded:: 2.0
        """
        self._generic_controller.focus_limit.value = value

    def register_finished_callback(self, callback: Callable[[], None]) -> str:
        """
        Registers a callback function to be invoked when white balance
        adjustment completes in the "Once" mode.

        :param callback: The callback to register
        :return: Unique string identifying the callback function to unregister
                 the callback later.

        .. versionadded:: 2.0
        """
        return self._generic_controller.register_finished_callback(callback)

    def unregister_finished_callback(self, callback_id: str) -> bool:
        """
        Unregisters a previously registered finished callback so that
        it is no longer invoked.

        :param callback_id: return value of ``register_finished_callback``
                            which identifies the registered callback

        :return: True if the callback was found and successfully unregistered,
                 False otherwise.

        .. note:: Unregistering a callback that's currently executing is safe.

        .. versionadded:: 2.0
        """
        return self._generic_controller.unregister_finished_callback(
            callback_id
        )
