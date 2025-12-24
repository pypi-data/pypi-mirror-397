from typing import Callable

from ids_peak_common import Range, Rectangle, Interval
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import Manager

from ids_peak_afl.exceptions import NotSupportedException
from ids_peak_afl.pipeline.datatypes import NamedIntEnum
from ids_peak_afl.pipeline.modules.controllers import (
    ControllerMode,
    ControllerType,
)
from ids_peak_afl.pipeline.features import (
    BrightnessComponentType,
    BrightnessAnalysisAlgorithm,
)

from ids_peak_afl.pipeline.modules.controllers._internal import (
    generic_auto_brightness as _generic_auto_brightness,
)
from ids_peak_afl.pipeline.modules.controllers._internal.icontroller import (
    IController,
)
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
    assert_parameter_type as _assert_parameter_type,
)


class AutoBrightnessPolicy(NamedIntEnum):
    """
    Enumeration for auto brightness policy.

    Defines the various strategies for automatic brightness control, specifying
    how the controller adjusts parameters to reach the target brightness level.

    .. versionadded:: 2.0
    """

    EXPOSURE_AND_GAIN = (0, "ExposureAndGain")
    """Use both exposure time and gain adjustments"""

    EXPOSURE_ONLY = (1, "ExposureOnly")
    """Use only exposure time adjustments, keeping gain constant"""

    GAIN_ONLY = (2, "GainOnly")
    """Use only gain adjustments, keeping exposure time constant"""


class BasicAutoBrightness(IController):
    """
    This class provides a simplified interface for automatic brightness
    control by adjusting the camera’s exposure and the gain of the
    camera and/or host, depending on the current ``AutoBrightnessPolicy``.

    .. note:: For more granular control, consider using
              ``AdvancedAutoBrightness``

    .. versionadded:: 2.0
    """

    def __init__(self, manager: Manager, callback: Callable[[], None]) -> None:
        """
        Creates a BasicAutoBrightness controller.

        :param manager: Reference to the manager for device communication
        :param callback: Processing callback that will be invoked when
                         an image has been processed

        .. versionadded:: 2.0
        """
        self._cached_mode = ControllerMode.OFF
        self._policy = AutoBrightnessPolicy.EXPOSURE_AND_GAIN
        self._exposure_component = BrightnessComponentType.EXPOSURE
        self._gain_component = BrightnessComponentType.GAIN
        self._generic_controller = (
            _generic_auto_brightness.GenericAutoBrightness(
                manager,
                callback,
                [self._exposure_component, self._gain_component],
            )
        )
        self._mode: ControllerMode = ControllerMode.OFF

    @property
    def name(self) -> str:
        """
        Returns the name of this controller.

        .. versionadded:: 2.0
        """
        return "BasicAutoBrightness"

    @property
    def type(self) -> ControllerType:
        """
        Returns the type of this controller.

        .. versionadded:: 2.0
        """
        return ControllerType.BRIGHTNESS

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this controller to an archive.

        .. note:: BasicAutoBrightness serialization data is not compatible to
                  AdvancedAutoBrightness

        :param archive: The archive in which this controller's state will
                        be stored.

        .. versionadded:: 2.0
        """
        archive.set("Policy", self._policy.string_value)
        self._generic_controller.serialize(archive)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this controller's state from an archive.

        .. note:: BasicAutoBrightness serialization data is not compatible to
                  AdvancedAutoBrightness

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        self._generic_controller.deserialize(archive)
        self._cached_mode = self.mode
        self.policy = AutoBrightnessPolicy.from_string(
            _get_and_reraise(archive, "Policy", str)
        )

    @property
    def mode(self) -> ControllerMode:
        """
        Returns the current operation mode of this controller.

        :return: Current ``ControllerMode`` depending on the current states of
                 the components (exposure, gain) in the following order:
                 - ``ControllerMode.CONTINUOUS`` if at least one component
                    is in continuous mode
                 - ``ControllerMode.ONCE`` if at least one component
                    is running in one-shot mode
                 - ``ControllerMode.OFF`` if all components are off

        .. versionadded:: 2.0
        """
        return self._generic_controller.mode

    @mode.setter
    def mode(self, mode: ControllerMode) -> None:
        """
        Sets the operation mode to all components, depending on the
        current policy:
            - ``AutoBrightnessPolicy.EXPOSURE_ONLY``:
              Mode is applied to exposure component only, gain component is
              set to ``ControllerMode.OFF``
            - ``AutoBrightnessPolicy.GAIN_ONLY``:
              Mode is applied to gain component only, exposure component is
              set to ``ControllerMode.OFF``
            - ``AutoBrightnessPolicy.EXPOSURE_AND_GAIN``:
              Mode is applied to both components

        :param mode: The controller mode to set

        .. versionadded:: 2.0
        """
        _assert_parameter_type(mode, ControllerMode, "mode")

        exposure_component = self._generic_controller.component(
            self._exposure_component
        )
        if exposure_component is not None:
            if self._policy in [
                AutoBrightnessPolicy.EXPOSURE_ONLY,
                AutoBrightnessPolicy.EXPOSURE_AND_GAIN,
            ]:
                controller_mode = mode
            else:
                controller_mode = ControllerMode.OFF

            exposure_component.mode = controller_mode

        gain_component = self._generic_controller.component(
            self._gain_component
        )
        if gain_component is not None:
            if self._policy in [
                AutoBrightnessPolicy.GAIN_ONLY,
                AutoBrightnessPolicy.EXPOSURE_AND_GAIN,
            ]:
                controller_mode = mode
            else:
                controller_mode = ControllerMode.OFF

            gain_component.mode = controller_mode

        self._cached_mode = mode

    def reset_to_default(self) -> None:
        """
        Resets this controller's state to default.

        This sets ``policy`` to ``AutoBrightnessPolicy.EXPOSURE_AND_GAIN``,
        ``mode`` to ``ControllerMode.OFF`` and all other properties to
        their default values.

        .. versionadded:: 2.0
        """
        self._policy = AutoBrightnessPolicy.EXPOSURE_AND_GAIN
        self._cached_mode = ControllerMode.OFF
        self._generic_controller.reset_to_default()

    @property
    def analysis_algorithm(self) -> BrightnessAnalysisAlgorithm:
        """
        Gets the current brightness analysis algorithm.

        .. versionadded:: 2.0
        """
        return self._generic_controller.analysis_algorithm.value

    @analysis_algorithm.setter
    def analysis_algorithm(
        self, algorithm: BrightnessAnalysisAlgorithm
    ) -> None:
        """
        Sets the brightness analysis algorithm.

        :param algorithm: The brightness analysis algorithm to use

        .. versionadded:: 2.0
        """
        _assert_parameter_type(
            algorithm, BrightnessAnalysisAlgorithm, "algorithm"
        )
        self._generic_controller.analysis_algorithm.value = algorithm

    @property
    def auto_percentile_range(self) -> Range:
        """
        Returns the valid range for ``auto_percentile``.

        .. versionadded:: 2.0
        """
        return self._generic_controller.auto_percentile.range

    @property
    def auto_percentile(self) -> float:
        """
        Gets the current percentile value for brightness calculation.

        The percentile determines which part of the histogram is used
        for brightness analysis. Higher percentiles focus on brighter areas,
        lower percentiles on darker areas.

        :return: The currently configured percentile value

        .. versionadded:: 2.0
        """
        return self._generic_controller.auto_percentile.value

    @auto_percentile.setter
    def auto_percentile(self, percentile: float) -> None:
        """
        Sets the percentile value for brightness calculation.

        :param percentile: The percentile value to use

        .. note:: Check ``auto_percentile_range`` before calling this method to
                  ensure the value is valid.

        .. versionadded:: 2.0
        """
        self._generic_controller.auto_percentile.value = percentile

    @property
    def auto_target_range(self) -> Range:
        """
        Returns the valid range for ``auto_target``.

        .. versionadded:: 2.0
        """
        return self._generic_controller.auto_target.range

    @property
    def auto_target(self) -> int:
        """
        Gets the current target brightness value.

        :return: The currently configured target brightness value

        .. versionadded:: 2.0
        """
        return self._generic_controller.auto_target.value

    @auto_target.setter
    def auto_target(self, target: int) -> None:
        """
        Sets the target brightness value.

        :param target: The target brightness value in device-specific units

        .. note:: Check ``auto_target_range`` before calling this method to
                  ensure the value is valid.

        .. versionadded:: 2.0
        """
        self._generic_controller.auto_target.value = target

    @property
    def auto_tolerance_range(self) -> Range:
        """
        Returns the valid range for ``auto_tolerance``.

        .. versionadded:: 2.0
        """
        return self._generic_controller.auto_tolerance.range

    @property
    def auto_tolerance(self) -> int:
        """
        Returns the brightness tolerance within which the algorithm
        will pause or finish adjustments.

        Smaller tolerance values provide more stable brightness but may
        cause oscillations while larger tolerance values reduce adjustment
        frequency but may allow more brightness variation.

        :return: The current tolerance value

        .. versionadded:: 2.0
        """
        return self._generic_controller.auto_tolerance.value

    @auto_tolerance.setter
    def auto_tolerance(self, tolerance: int) -> None:
        """
        Sets the brightness tolerance within which the algorithm
        will pause or finish adjustments.

        :param tolerance: The tolerance value to set

        .. note:: Check ``auto_tolerance_range`` before calling this method to
                  ensure the value is valid.

        .. versionadded:: 2.0
        """
        self._generic_controller.auto_tolerance.value = tolerance

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

        ..  note:: Check ``skip_frames_range`` before calling this method to
                ensure the value is valid.

        .. versionadded:: 2.0
        """
        self._generic_controller.skip_frames.value = skip_frames

    @property
    def roi(self) -> Rectangle:
        """
        Returns the region of interest (ROI) that is used by the brightness
        algorithm to determine the current brightness level.

        .. note:: When the ROI is set as (0, 0, 0, 0) the algorithm evaluates
                  the entire image.

        .. versionadded:: 2.0
        """
        return self._generic_controller.roi.value

    @roi.setter
    def roi(self, roi: Rectangle) -> None:
        """
        Sets the region of interest (ROI) that is used by the brightness
        algorithm to determine the current brightness level.

        This allows for brightness analysis on a smaller region of the image,
        providing more precise control over the results and reducing
        computational load.

        :param roi: The ROI used by the brightness algorithm

        .. versionadded:: 2.0
        """
        self._generic_controller.roi.value = roi

    @property
    def policy(self) -> AutoBrightnessPolicy:
        """
        Returns the control policy.

        The policy specifies which parameters (gain, exposure) are adjusted
        to achieve the ``auto_target`` brightness level.

        .. versionadded:: 2.0
        """
        return self._policy

    @policy.setter
    def policy(self, policy: AutoBrightnessPolicy) -> None:
        """
        Sets the control policy.

        :param policy: The auto brightness policy

        .. versionadded:: 2.0
        """
        _assert_parameter_type(policy, AutoBrightnessPolicy, "policy")

        self._policy = policy
        # NOTE: so the mode is updated for the new policy
        self.mode = self._cached_mode

    @property
    def exposure_limit_range(self) -> Interval:
        """
        Returns the valid range for ``exposure_limit``.

        .. versionadded:: 2.0
        """
        return self._generic_controller.component(
            BrightnessComponentType.EXPOSURE
        ).limit_range

    @property
    def has_exposure_limit(self) -> bool:
        """
        Returns True if ``exposure_limit`` is supported, False otherwise.

        .. versionadded:: 2.0
        """
        return self._generic_controller.has_component(self._exposure_component)

    @property
    def exposure_limit(self) -> Interval:
        """
        Returns the exposure limit interval.

        The exposure limit defines an interval specifying the minimum and
        maximum exposure times within which the exposure can be adjusted.

        :raises ids_peak_afl.exceptions.NotSupportedException:
                if exposure component is not available

        .. versionadded:: 2.0
        """
        if not self.has_exposure_limit:
            raise NotSupportedException("Exposure component not supported")
        return self._generic_controller.component(
            self._exposure_component
        ).limit

    @exposure_limit.setter
    def exposure_limit(self, interval: Interval) -> None:
        """
        Sets the exposure limit.

        :param interval: The interval defining the minimum and maximum
               exposure limits

        :raises ids_peak_afl.exceptions.NotSupportedException:
                if exposure component is not available

        .. versionadded:: 2.0
        """
        if not self.has_exposure_limit:
            raise NotSupportedException("Exposure component not supported")
        self._generic_controller.component(
            self._exposure_component
        ).limit = interval

    @property
    def gain_limit_range(self) -> Interval:
        """
        Returns the valid range for ``gain_limit``.

        .. versionadded:: 2.0
        """
        return self._generic_controller.component(
            BrightnessComponentType.GAIN
        ).limit_range

    @property
    def has_gain_limit(self) -> bool:
        """
        Returns True if ``gain_limit`` is supported, False otherwise.

        .. versionadded:: 2.0
        """
        return self._generic_controller.has_component(self._gain_component)

    @property
    def gain_limit(self) -> Interval:
        """
        Returns the gain limit interval.

        The gain limit defines an interval specifying the minimum and
        maximum gain factors within which the gain can be adjusted.

        :raises ids_peak_afl.exceptions.NotSupportedException:
                if gain component is not available

        .. versionadded:: 2.0
        """
        if not self.has_gain_limit:
            raise NotSupportedException("Gain component not supported")
        return self._generic_controller.component(self._gain_component).limit

    @gain_limit.setter
    def gain_limit(self, interval: Interval) -> None:
        """
        Sets the gain limit.

        :param interval: The interval defining the minimum and maximum
               gain limits

        :raises ids_peak_afl.exceptions.NotSupportedException:
                if gain component is not available

        .. versionadded:: 2.0
        """
        if not self.has_gain_limit:
            raise NotSupportedException("Gain component not supported")

        self._generic_controller.component(
            self._gain_component
        ).limit = interval

    def register_finished_callback(self, callback: Callable[[], None]) -> str:
        """
        Registers a callback function to be invoked when brightness
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
