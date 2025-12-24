from collections.abc import Callable
from typing import List, Sequence

from ids_peak_common import Interval, Rectangle, Point, Size
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import (
    Manager,
    Controller,
    ProcessingCallback,
    peak_afl_process_data,
    peak_afl_process_data_brightness,
    PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_HOST_GAIN,
)

from ids_peak_afl.exceptions import NotSupportedException

from ids_peak_afl.pipeline.features.ifeature import IFeature, IRangeFeature
from ids_peak_afl.pipeline.features import (
    SkipFrames,
    AutoTarget,
    AutoTolerance,
    AutoPercentile,
    Roi,
    BrightnessAlgorithm,
    BrightnessComponent,
    BrightnessComponentType,
    BrightnessAnalysisAlgorithm,
)
from ids_peak_afl.pipeline.features.brightness_limit import (
    _create_brightness_limit,
)

from ids_peak_afl.pipeline.modules.controllers import (
    ControllerMode,
    ControllerType,
)
from ids_peak_afl.pipeline.modules.controllers._internal.icontroller import (
    IController,
)
from ids_peak_afl.pipeline.modules.controllers._internal import (
    callback_manager as _callback_manager,
)

from ids_peak_afl.pipeline._internal.utils import (
    get_archive_and_reraise as _get_archive_and_reraise,
    assert_parameter_type as _assert_parameter_type,
)


class ProcessingBrightnessCallback(ProcessingCallback):
    """
    Callback handler for processing brightness data.

    This class wraps a user-provided callback function and invokes it when
    new brightness data is received from the controller, specifically
    for the host gain component.
    """

    def __init__(
        self, controller: Controller, callback: Callable[[], None]
    ) -> None:
        """
        Initializes the brightness processing callback.

        :param controller: The controller instance to monitor.
        :param callback: A callable to invoke when relevant brightness
                         data is received.
        """
        super().__init__(controller)
        self._callback = callback

    def callback(self, data: peak_afl_process_data) -> None:
        """
        Handles incoming processing data from the controller.

        Only invokes the user-provided callback if the callback data
        corresponds to the host gain component.

        :param data: Processing data received from the controller.
        """
        if not isinstance(data, peak_afl_process_data_brightness):
            return

        if (
            data.controller_component
            != PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_HOST_GAIN
        ):
            return

        self._callback()


class GenericAutoBrightness(IController):
    """
    This class provides a generic interface for automatic brightness control
    that is used as backend for BasicAutoBrightness or AdvancedAutoBrightness.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        manager: Manager,
        callback: Callable[[], None],
        component_types: List[BrightnessComponentType],
    ) -> None:
        """
        Creates a GenericAutoBrightness controller

        :param manager: Reference to the manager for device communication
        :param callback: Processing callback that will be invoked when
                         an image has been processed
        :param component_types: List of component types to create

        .. versionadded:: 2.0
        """
        self._manager = manager
        self._controller = self._manager.CreateController(
            ControllerType.BRIGHTNESS
        )

        self._brightness_components: dict[
            BrightnessComponentType, BrightnessComponent
        ] = {}
        for comp_type in component_types:
            if self._controller.IsBrightnessComponentUnitSupported(comp_type):
                self._brightness_components[comp_type] = BrightnessComponent(
                    self._controller,
                    comp_type,
                    _create_brightness_limit(self._controller, comp_type),
                )

        self._process_callback = ProcessingBrightnessCallback(
            self._controller, callback
        )
        self._finished_callback = _callback_manager.ControllerFinishedCallback(
            self._controller
        )

        self._skip_frames = SkipFrames(self._controller)
        self._auto_target = AutoTarget(self._controller)
        self._auto_tolerance = AutoTolerance(self._controller)
        self._auto_percentile = AutoPercentile(self._controller)
        self._roi = Roi(self._controller)
        self._algorithm = BrightnessAlgorithm(self._controller)

    @property
    def name(self) -> str:
        """
        Returns the name of this controller.

        .. versionadded:: 2.0
        """
        return "GenericAutoBrightness"

    @property
    def type(self) -> ControllerType:
        """
        Returns the type of this controller.

        .. versionadded:: 2.0
        """
        return ControllerType.BRIGHTNESS

    @property
    def mode(self) -> ControllerMode:
        """
        Returns the current operation mode of this controller.

        :return: Current ``ControllerMode`` depending on the current states of
                 the components in the following order:
                 - ``ControllerMode.CONTINUOUS`` if at least one component
                    is in continuous mode
                 - ``ControllerMode.ONCE`` if at least one component
                    is running in one-shot mode
                 - ``ControllerMode.OFF`` if all components are off

        .. versionadded:: 2.0
        """

        def any_component_has_mode(mode: ControllerMode) -> bool:
            return any(
                component.mode == mode
                for component in self._brightness_components.values()
            )

        # If any component is CONTINUOUS, return CONTINUOUS
        if any_component_has_mode(ControllerMode.CONTINUOUS):
            return ControllerMode.CONTINUOUS

        # If any component is ONCE, return ONCE
        if any_component_has_mode(ControllerMode.ONCE):
            return ControllerMode.ONCE

        return ControllerMode.OFF

    @mode.setter
    def mode(self, mode: ControllerMode) -> None:
        """
        Sets the operation mode to all components.

        .. versionadded:: 2.0
        """
        _assert_parameter_type(mode, ControllerMode, "mode")
        for component in self._brightness_components.values():
            component.mode = mode

    def reset_to_default(self) -> None:
        """
        Resets this controller's state to default.

        .. versionadded:: 2.0
        """
        from sys import float_info

        self.mode = ControllerMode.OFF
        self._skip_frames.value = 2
        self._auto_target.value = 150
        self._auto_tolerance.value = 3
        self._auto_percentile.value = 13.0

        self._algorithm.value = BrightnessAnalysisAlgorithm.MEDIAN

        self._roi.value = Rectangle(Point(0, 0), Size(0, 0))

        for component in self._brightness_components.values():
            component.limit = Interval(0.0, float_info.max)

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this controller to an archive.

        :param archive: The archive in which this controller's state will
                        be stored.

        .. versionadded:: 2.0
        """
        for feature in self._features:
            feature.serialize(archive)

        for component_type, component in self._brightness_components.items():
            component_archive = archive.create_archive()
            component.serialize(component_archive)

            archive.set(component_type.string_value, component_archive)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this controller's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        for feature in self._features:
            feature.deserialize(archive)

        for component_type, component in self._brightness_components.items():
            component_archive = _get_archive_and_reraise(
                archive, component_type.string_value
            )
            component.deserialize(component_archive)

    @property
    def skip_frames(self) -> IRangeFeature[int]:
        """
        Returns the skip frames feature.

        .. versionadded:: 2.0
        """
        return self._skip_frames

    @property
    def auto_target(self) -> IRangeFeature[int]:
        """
        Returns the auto target feature.

        .. versionadded:: 2.0
        """
        return self._auto_target

    @property
    def auto_tolerance(self) -> IRangeFeature[int]:
        """
        Returns the auto tolerance feature.

        .. versionadded:: 2.0
        """
        return self._auto_tolerance

    @property
    def auto_percentile(self) -> IRangeFeature[float]:
        """
        Returns the auto percentile feature.

        .. versionadded:: 2.0
        """
        return self._auto_percentile

    @property
    def roi(self) -> IFeature[Rectangle]:
        """
        Returns the roi feature.

        .. versionadded:: 2.0
        """
        return self._roi

    @property
    def analysis_algorithm(self) -> IFeature[BrightnessAnalysisAlgorithm]:
        """
        Returns the analysis algorithm feature.

        .. versionadded:: 2.0
        """
        return self._algorithm

    def component(
        self, component_type: BrightnessComponentType
    ) -> BrightnessComponent:
        """
        Returns component of the given type.

        :param component_type: The component's type.
        :raises ids_peak_afl.exceptions.NotSupportedException:
                if the component is not supported

        .. versionadded:: 2.0
        """
        component = self._brightness_components.get(component_type)
        if component is None:
            raise NotSupportedException("Component not supported")
        return component

    def has_component(self, component_type: BrightnessComponentType) -> bool:
        """
        Returns True if the controller has a component of the given type,
        False otherwise.

        .. versionadded:: 2.0
        """

        return component_type in self._brightness_components

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
            self._auto_target,
            self._auto_tolerance,
            self._auto_percentile,
            self._roi,
            self._algorithm,
        ]
