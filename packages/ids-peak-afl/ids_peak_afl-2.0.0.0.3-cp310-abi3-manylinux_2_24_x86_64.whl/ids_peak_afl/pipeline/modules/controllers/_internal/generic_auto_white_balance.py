from typing import Callable, Sequence

from ids_peak_common import Rectangle, Point, Size
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import (
    Manager,
    Controller,
    ProcessingCallback,
    peak_afl_process_data,
    peak_afl_process_data_whitebalance,
    PEAK_AFL_CONTROLLER_WHITEBALANCE_COMPONENT_HOST_GAIN,
)

from ids_peak_afl.pipeline.features.ifeature import IFeature, IRangeFeature
from ids_peak_afl.pipeline.features import Roi, SkipFrames

from ids_peak_afl.pipeline.modules.controllers import (
    ControllerType,
    ControllerMode,
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


class ProcessingWhiteBalanceCallback(ProcessingCallback):
    """
    Callback handler for processing white balance data.

    This class wraps a user-provided callback function and invokes it when
    new white balance data is received from the controller, specifically
    for the host gain component.
    """

    def __init__(
        self, controller: Controller, callback: Callable[[], None]
    ) -> None:
        """
        Initializes the white balance processing callback.

        :param controller: The controller instance to monitor.
        :param callback: A callable to invoke when relevant white balance
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
        if not isinstance(data, peak_afl_process_data_whitebalance):
            return

        if (data.controller_component
                != PEAK_AFL_CONTROLLER_WHITEBALANCE_COMPONENT_HOST_GAIN):
            return

        self._callback()


class GenericWhiteBalance(IController):
    """
    This class provides a generic interface for white balance control
    that is used as backend for BasicWhiteBalance or AdvancedWhiteBalance.

    .. versionadded:: 2.0
    """

    def __init__(self, manager: Manager, callback: Callable[[], None]) -> None:
        """
        Creates a GenericWhiteBalance controller

        :param manager: Reference to the manager for device communication
        :param callback: Processing callback that will be invoked when
                        an image has been processed

        .. versionadded:: 2.0
        """
        self._manager = manager
        self._controller = self._manager.CreateController(
            ControllerType.WHITE_BALANCE
        )
        self._manager.AddController(self._controller)

        self._process_callback = ProcessingWhiteBalanceCallback(
            self._controller, callback
        )
        self._finished_callback = _callback_manager.ControllerFinishedCallback(
            self._controller
        )

        self._skip_frames = SkipFrames(self._controller)
        self._roi = Roi(self._controller)

    @property
    def name(self) -> str:
        """
        Returns the name of this controller.

        .. versionadded:: 2.0
        """
        return "GenericWhiteBalance"

    @property
    def type(self) -> ControllerType:
        """
        Returns the type of this controller.

        .. versionadded:: 2.0
        """
        return ControllerType.WHITE_BALANCE

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
        self._roi.value = Rectangle(Point(0, 0), Size(0, 0))

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
        :raises ids_peak_afl.exceptions.CorruptedDataException:
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
    def roi(self) -> IFeature[Rectangle]:
        """
        Returns the roi feature.

        .. versionadded:: 2.0
        """
        return self._roi

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
        return [self._skip_frames, self._roi]
