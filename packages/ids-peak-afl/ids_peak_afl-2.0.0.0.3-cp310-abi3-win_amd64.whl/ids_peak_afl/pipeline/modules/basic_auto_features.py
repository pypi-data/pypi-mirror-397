from typing import Any, Sequence
from typing import cast as type_cast

from ids_peak_common.pipeline.modules import IAutoFeature, IGain
from ids_peak_common.serialization import IArchive

from ids_peak.ids_peak import Device

from ids_peak_afl.exceptions import NotSupportedException

from ids_peak_afl.pipeline.modules.controllers import (
    ControllerMode,
    ControllerType,
    BasicAutoFocus,
    BasicAutoBrightness,
    BasicAutoWhiteBalance,
)
from ids_peak_afl.pipeline.modules._internal.generic_auto_features import (
    GenericAutoFeatures,
)
from ids_peak_afl.pipeline._internal.utils import (
    assert_parameter_type as _assert_parameter_type,
)


class BasicAutoFeatures(IAutoFeature):
    """
    This class provides a simplified interface for
    managing automatic image and camera adjustments.

    This module integrates basic controllers for brightness, focus, and
    white balance with simplified configuration options.
    It offers a single point of access for all auto features.

    .. note:: For more granular control, consider using
              ``AdvancedAutoFeatures``

    .. versionadded:: 2.0
    """

    def __init__(self, device: Device) -> None:
        """
        Creates a BasicAutoFeatures instance.

        The module will automatically detect which controllers
        (``auto_brightness``, ``auto_white_balance``, ``auto_focus``) are
        supported by the device.

        :param device: The device instance that will be used for camera
                       operations. Must be valid and not None.

        :raises ids_peak_afl.exceptions.InvalidParameterException:
                if device is invalid
        :raises ids_peak_afl.exceptions.InternalErrorException:
                if an internal error occurs

        .. versionadded:: 2.0
        """
        super().__init__()
        self._generic_module = GenericAutoFeatures(device, False)

    @property
    def type(self) -> str:
        """
        Returns the type identifier of this module.

        .. versionadded:: 2.0
        """
        return "BasicAutoFeatures"

    @property
    def enabled(self) -> bool:
        """
        Checks if this module is enabled and will process data.

        Returns the overall state of this module. To check specific controller
        modes, use the ``mode`` property of the individual controllers
        (``auto_brightness``, ``auto_white_balance``, and ``auto_focus``).

        :return: True if this module is enabled, False otherwise.

        .. versionadded:: 2.0
        """
        return self._generic_module.enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """
        Sets whether this module is enabled and will process data.

        .. note::
            Enabling the module does not automatically set controller modes to
            ``ControllerMode.CONTINUOUS``. Ensure the controllers are
            configured appropriately; otherwise, the module may not process
            data as expected.

        :param enabled: True to enable this module, False to disable it.

        .. versionadded:: 2.0
        """
        self._generic_module.enabled = enabled

    def process(self, data: Any) -> Any:
        """
        Asynchronously evaluates the incoming data and determines new
        parameters for image brightness, white balance, and focus, which are
        then applied asynchronously.

        .. note::
            - Auto features are processed and applied asynchronously.
            - New images received during processing are skipped. See also
              ``is_processing``.
            - Processing order: brightness → white balance → focus

        :param data: The input data to be processed by this module.
        :return: The input data
        :raises ids_peak_afl.exceptions.InvalidCastException:
                if input type is incompatible

        .. versionadded:: 2.0
        """
        return self._generic_module.process(data)

    @property
    def is_processing(self) -> bool:
        """
        Returns whether this module is currently processing data.

        While this function returns True, any calls to ``process`` will cause
        the data to be skipped for processing.

        :return: True if this module is currently processing data, False
                 otherwise.

        .. versionadded:: 2.0
        """
        return self._generic_module.is_processing

    def reset_to_default(self) -> None:
        """
        Resets this module's state to default.

        .. versionadded:: 2.0
        """
        self._generic_module.reset_to_default()

    @property
    def auto_brightness(self) -> BasicAutoBrightness:
        """
        Returns the brightness controller for automatic brightness adjustment.

        Use this controller to manage and configure automatic brightness
        behavior like exposure and master gain.

        :return: The brightness controller instance.

        :raises peak::common.exceptions.NotSupportedException:
                If automatic brightness control is not supported.

        .. note:: Check ``has_auto_brightness`` before calling this method to
                ensure the feature is available.

        .. versionadded:: 2.0
        """
        controller = self._generic_module.get_controller(
            ControllerType.BRIGHTNESS
        )
        if not controller:
            raise NotSupportedException(
                "Brightness controller is not supported "
                "for the current device!"
            )
        return type_cast(BasicAutoBrightness, controller)

    @property
    def has_auto_brightness(self) -> bool:
        """
        Checks if brightness control is available.

        :return: True if the brightness control is supported,
                 False otherwise

        .. versionadded:: 2.0
        """
        return self._generic_module.has_controller(ControllerType.BRIGHTNESS)

    @property
    def auto_focus(self) -> BasicAutoFocus:
        """
        Returns the focus controller for automatic focusing.

        Use this controller to manage and configure automatic focus
        behavior.

        :return: The focus controller instance.

        :raises peak::common.exceptions.NotSupportedException:
                If automatic focus control is not supported.

        .. note:: Check ``has_auto_focus`` before calling this method to
                ensure the feature is available.

        .. versionadded:: 2.0
        """
        controller = self._generic_module.get_controller(ControllerType.FOCUS)
        if not controller:
            raise NotSupportedException(
                "Focus controller is not supported for the current device!"
            )
        return type_cast(BasicAutoFocus, controller)

    @property
    def has_auto_focus(self) -> bool:
        """
        Checks if focus control is available.

        Focus control can be used only with cameras that support hardware-based
        focal length adjustment.

        :return: True if the focus control is supported, False otherwise

        .. versionadded:: 2.0
        """
        return self._generic_module.has_controller(ControllerType.FOCUS)

    @property
    def auto_white_balance(self) -> BasicAutoWhiteBalance:
        """
        Returns the white balance controller for automatic white balance.

        Use this controller to manage and configure automatic white balance
        behavior like color gains.

        :return: The white balance controller instance.

        :raises peak::common.exceptions.NotSupportedException:
                If automatic white balance control is not supported.

        .. note:: Check ``has_auto_white_balance`` before calling this method
                to ensure the feature is available.

        .. versionadded:: 2.0
        """
        controller = self._generic_module.get_controller(
            ControllerType.WHITE_BALANCE
        )
        if not controller:
            raise NotSupportedException(
                "White balance controller is not supported "
                "for the current device!"
            )
        return type_cast(BasicAutoWhiteBalance, controller)

    @property
    def has_auto_white_balance(self) -> bool:
        """
        Checks if white balance control is available.

        White balance control is only supported for color cameras.

        :return: True if the white balance control is supported,
                 False otherwise

        .. versionadded:: 2.0
        """
        return self._generic_module.has_controller(
            ControllerType.WHITE_BALANCE
        )

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this module to an archive.

        .. note:: BasicAutoFeatures serialization data is not compatible to
                  AdvancedAutoFeatures

        :param archive: The archive in which this module's state
                        will be stored.

        .. versionadded:: 2.0
        """
        self._generic_module.serialize(archive)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this module's state from an archive.

        .. note:: BasicAutoFeatures serialization data is not compatible to
                  AdvancedAutoFeatures

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        self._generic_module.deserialize(archive)

    def set_gain_module(self, gain_module: IGain | None) -> None:
        """
        Sets the gain module used by this module for host-side
        gain adjustments.

        .. note:: The gain module is used only as a fallback for cameras that
                  do not provide hardware gain control.

        :param gain_module: The gain module implementation.
                            Pass ``None`` to disable host gain support.

        .. versionadded:: 2.0
        """
        self._generic_module.set_gain_module(gain_module)

    def set_color_correction_matrix(self, matrix: Sequence[float]) -> None:
        """
        Sets the color correction matrix for this module.

        Set this matrix to inform the white balance controller of a
        color correction matrix applied between color gain adjustment and
        input image analysis. The controller incorporates this matrix in
        its calculations.

        .. note:: If no matrix is set, the white balance control may become
                  unstable.

        :param matrix: Sequence of 9 float values representing the 3x3 color
                       correction matrix in row-wise order [row, column]:
                       [0,0] [0,1] [0,2] [1,0] [1,1] [1,2] [2,0] [2,1] [2,2]

        :raises ids_peak_afl.exceptions.InvalidParameterException:
                if matrix values are invalid

        .. versionadded:: 2.0
        """
        self._generic_module.set_color_correction_matrix(matrix)

    def set_all_modes(self, mode: ControllerMode) -> None:
        """
        Sets the operating mode for all available auto feature controllers.

        This convenience method applies the specified controller mode to all
        available controllers (brightness, focus, and white balance).

        :param mode: The controller mode to apply to all controllers

        .. versionadded:: 2.0
        """
        _assert_parameter_type(mode, ControllerMode, "mode")
        self._generic_module.set_all_modes(mode)

    def set_all_skip_frames(self, value: int) -> None:
        """
        Sets the skip frames value for all available auto feature controllers.

        This convenience method sets the skip_frames parameter for all
        available controllers (brightness, focus, and white balance).

        Skip frames controls how many images are skipped between processing
        steps. Processing every N-th frame reduces computational load but
        may decrease responsiveness.

        :param value: Number of frames to skip between processing steps

        .. versionadded:: 2.0
        """
        self._generic_module.set_all_skip_frames(value)
