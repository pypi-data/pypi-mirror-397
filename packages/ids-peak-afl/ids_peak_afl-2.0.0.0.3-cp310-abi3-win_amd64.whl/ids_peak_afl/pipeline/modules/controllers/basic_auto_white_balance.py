from collections.abc import Callable

from ids_peak_common import Range, Rectangle
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import Manager

from ids_peak_afl.pipeline.modules.controllers import (
    ControllerMode,
    ControllerType,
)
from ids_peak_afl.pipeline.modules.controllers._internal.icontroller import (
    IController,
)
from ids_peak_afl.pipeline.modules.controllers._internal import (
    generic_auto_white_balance as _generic_auto_white_balance,
)
from ids_peak_afl.pipeline._internal.utils import (
    assert_parameter_type as _assert_parameter_type,
)


class BasicAutoWhiteBalance(IController):
    """
    This class provides a simplified interface for automatic white balance
    control by adjusting the color gains of camera and/or host.

    .. note:: For more granular control, consider using
              ``AdvancedWhiteBalance``

    .. versionadded:: 2.0
    """

    def __init__(self, manager: Manager, callback: Callable[[], None]) -> None:
        """
        Creates a BasicAutoWhiteBalance controller.

        :param manager: Reference to the manager for device communication
        :param callback: Processing callback that will be invoked when
                         an image has been processed

        .. versionadded:: 2.0
        """
        self._manager = manager
        self._generic_controller = (
            _generic_auto_white_balance.GenericWhiteBalance(manager, callback)
        )

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
    def name(self) -> str:
        """
        Returns the name of this controller.

        .. versionadded:: 2.0
        """
        return "BasicAutoWhiteBalance"

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
    def roi(self) -> Rectangle:
        """
        Returns the region of interest (ROI) that is used by the white balance
        algorithm to determine the current level.

        .. note:: When the ROI is set as (0, 0, 0, 0) the algorithm evaluates
                  the entire image.

        .. versionadded:: 2.0
        """
        return self._generic_controller.roi.value

    @roi.setter
    def roi(self, roi: Rectangle) -> None:
        """
        Sets the region of interest (ROI) that is used by the white balance
        algorithm to determine the current level.

        This allows for white balance on a smaller region of the image,
        providing more precise control over the results and reducing
        computational load.

        :param roi: The ROI used by the white balance algorithm

        .. versionadded:: 2.0
        """
        self._generic_controller.roi.value = roi

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
