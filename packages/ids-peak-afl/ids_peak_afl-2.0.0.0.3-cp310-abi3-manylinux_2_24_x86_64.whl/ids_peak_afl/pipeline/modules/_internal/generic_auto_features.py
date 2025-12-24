import warnings

from typing import cast, Any, Sequence

from ids_peak_common import IImageView
from ids_peak_common.datatypes import PixelFormat, Channel
from ids_peak_common.pipeline.modules import IAutoFeature, IGain
from ids_peak_common.serialization import IArchive
from ids_peak_common.datatypes.metadata_key import MetadataKey

from ids_peak.ids_peak import Device, NodeMap, EnumerationNode

from ids_peak_afl.ids_peak_afl import Manager

from ids_peak_afl.exceptions import (
    InvalidParameterException,
    OutOfRangeException,
    CorruptedDataException,
    InvalidCastException,
)

from ids_peak_afl.pipeline.modules.controllers import (
    ControllerType,
    BasicAutoBrightness,
    BasicAutoFocus,
    BasicAutoWhiteBalance,
    ControllerMode,
)
from ids_peak_afl.pipeline.modules.controllers._internal.icontroller import (
    IController,
)

from ids_peak_afl.pipeline._internal.utils import (
    assert_parameter_type as _assert_parameter_type,
)


class GenericAutoFeatures(IAutoFeature):
    """
    This class provides a generic interface for
    managing automatic image and camera adjustments
    that is used as backend for BasicAutoFeatures or AdvancedAutoFeatures.

    .. versionadded:: 2.0
    """

    def __init__(self, device: Device, advanced: bool = True) -> None:
        """
        Creates a GenericAutoFeatures instance.

        :param device: The device instance that will be used for camera
                       operations. Must be valid and not None.
        :param advanced: True if the instance is used as backend for
                         AdvancedAutoFeatures, False otherwise

        .. versionadded:: 2.0
        """
        super().__init__()
        if device is None:
            raise InvalidParameterException("The given device is not valid!")
        else:
            self._remote_device_nodemap = device.RemoteDevice().NodeMaps()[0]

        from ids_peak_ipl.ids_peak_ipl import Gain

        self._enabled = True
        self._manager = Manager(self._remote_device_nodemap)
        self._controllers: dict[ControllerType, IController] = {}
        self._internal_gain = Gain()
        self._gain_module: IGain | None = None
        self._device = device

        for controller_type in ControllerType:
            if (controller_type == ControllerType.WHITE_BALANCE
                    and not GenericAutoFeatures._is_color_camera(self._remote_device_nodemap)):
                continue

            if self._manager.IsControllerSupported(controller_type):
                controller = self._create_controller(
                    self._manager, controller_type, advanced
                )
                self._controllers[controller_type] = controller

        self._manager.SetGainIPL(self._internal_gain)
        self.reset_to_default()

    @property
    def version(self) -> int:
        """
        Returns the version of this module.

        .. versionadded:: 2.0
        """
        return 1

    @property
    def type(self) -> str:
        """
        Returns the type identifier of this module.

        .. versionadded:: 2.0
        """
        return "GenericAutoFeatures"

    @property
    def enabled(self) -> bool:
        """
        Checks if this module is enabled and will process data.

        .. versionadded:: 2.0
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """
        Sets whether this module is enabled and will process data.

        .. versionadded:: 2.0
        """
        self._enabled = enabled

    def get_controller(
        self, controller_type: ControllerType
    ) -> IController | None:
        """
        Returns the controller of the given type.

        .. versionadded:: 2.0
        """
        return self._controllers.get(controller_type)

    def has_controller(self, controller_type: ControllerType) -> bool:
        """
        Returns True if the module has a controller of the given type,
        False otherwise.

        .. versionadded:: 2.0
        """
        return controller_type in self._controllers

    def process(self, data: Any) -> Any:
        """
        Asynchronously evaluates the incoming data and determines
        new parameters for image brightness, white balance, and focus,
        which are then applied asynchronously.

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
        if not self._enabled:
            return data

        is_running = self._manager.Status()
        if is_running:
            return data

        from ids_peak_ipl.ids_peak_ipl import Image

        def can_be_handled_as_image(input_data: Any) -> bool:
            return (
                hasattr(input_data, "pixel_format")
                and hasattr(input_data, "to_numpy_array")
                and callable(getattr(input_data, "to_numpy_array"))
                and hasattr(input_data, "width")
                and hasattr(input_data, "height")
                and hasattr(input_data, "metadata")
            )

        if isinstance(data, Image):
            self._manager.Process(data)
        elif isinstance(data, IImageView):
            self._manager.Process(Image.from_image_view(data))
        elif can_be_handled_as_image(data):
            np_data = data.to_numpy_array().flatten()
            img = Image.CreateFromSizeAndPythonBufferWithTimestamp(
                    int(data.pixel_format.value),
                    np_data,
                    data.width,
                    data.height,
                    data.metadata.get_value_by_key(MetadataKey.DEVICE_TIMESTAMP)
                )
            self._manager.Process(img)
        else:
            raise InvalidCastException("Unsupported input type!")

        return data

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
        return self._manager.Status()

    def reset_to_default(self) -> None:
        """
        Resets this module's state to default.

        .. versionadded:: 2.0
        """
        for controller in self._controllers.values():
            controller.reset_to_default()

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this module to an archive.

        :param archive: The archive in which this controller's state will
                        be stored.

        .. versionadded:: 2.0
        """
        archive.set("Version", self.version)
        archive.set("Enabled", self._enabled)

        for controller in self._controllers.values():
            controller_archive = archive.create_archive()
            controller.serialize(controller_archive)

            archive.set(controller.name, controller_archive)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this module's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails

        .. versionadded:: 2.0
        """
        version = archive.get("Version", int)
        if version < 1:
            raise CorruptedDataException(
                f"Version {version} is invalid. Must be at least 1"
            )

        self._enabled = archive.get("Enabled", bool)
        for controller in self._controllers.values():
            controller_archive = archive.get_archive(controller.name)
            controller.deserialize(controller_archive)

    def set_gain_module(self, gain_module: IGain | None) -> None:
        """
        Sets the gain module used by this module for host-side
        gain adjustments.

        :param gain_module: The gain module implementation.
                            Pass ``None`` to disable host gain support.

        .. versionadded:: 2.0
        """
        self._gain_module = gain_module

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
        self._manager.SetCCM(matrix)

    def set_all_modes(self, mode: ControllerMode) -> None:
        """
        Sets the operating mode for all available auto feature controllers.

        This convenience method applies the specified controller mode to all
        available controllers (brightness, focus, and white balance).

        :param mode: The controller mode to apply to all controllers

        .. versionadded:: 2.0
        """
        _assert_parameter_type(mode, ControllerMode, "mode")

        for controller in self._controllers.values():
            controller.mode = mode

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
        for controller_type, controller in self._controllers.items():
            controller = cast(
                BasicAutoBrightness | BasicAutoFocus | BasicAutoWhiteBalance,
                controller,
            )

            if (value < controller.skip_frames_range.minimum
                    or value > controller.skip_frames_range.maximum):
                raise OutOfRangeException(
                    f"The value for skip frames is out of range "
                    f"for controller {controller_type.string_value}."
                )

        for controller_type, controller in self._controllers.items():
            if controller_type == ControllerType.BRIGHTNESS:
                cast(BasicAutoBrightness, controller).skip_frames = value
            elif controller_type == ControllerType.FOCUS:
                cast(BasicAutoFocus, controller).skip_frames = value
            elif controller_type == ControllerType.WHITE_BALANCE:
                cast(BasicAutoWhiteBalance, controller).skip_frames = value

    def _create_controller(
        self, manager: Manager, controller_type: ControllerType, advanced: bool
    ) -> IController:
        if controller_type is ControllerType.BRIGHTNESS:

            def callback() -> None:
                return self._brightness_gains_changed_callback()

            if advanced:
                pass
                # return AdvancedAutoBrightness(manager, callback)
            return BasicAutoBrightness(manager, callback)
        if controller_type is ControllerType.FOCUS:
            if advanced:
                pass
                # return AdvancedAutoFocus(manager)
            return BasicAutoFocus(manager)
        if controller_type is ControllerType.WHITE_BALANCE:

            def callback() -> None:
                return self._white_balance_gains_changed_callback()

            if advanced:
                pass
                # return AdvancedWhiteBalance(manager, callback)
            return BasicAutoWhiteBalance(manager, callback)

        raise InvalidParameterException(
            "Unknown controller type: {}".format(controller_type)
        )

    def _brightness_gains_changed_callback(self) -> None:
        if self._gain_module is None:
            return

        self._gain_module.master = self._internal_gain.MasterGainValue()

    def _white_balance_gains_changed_callback(self) -> None:
        if self._gain_module is None:
            return

        self._gain_module.red = self._internal_gain.RedGainValue()
        self._gain_module.green = self._internal_gain.GreenGainValue()
        self._gain_module.blue = self._internal_gain.BlueGainValue()

    @staticmethod
    def _is_color_camera(node_map: NodeMap) -> bool:
        pixel_format_node: EnumerationNode = cast(
            EnumerationNode, node_map.TryFindNode("PixelFormat")
        )
        if not pixel_format_node or not pixel_format_node.IsReadable():
            return False

        for entry in pixel_format_node.AvailableEntries():
            pixel_format = PixelFormat(entry.Value())
            if pixel_format.has_channel(
                    Channel.RED
            ) or pixel_format.has_channel(Channel.BAYER):
                return True

        return False
