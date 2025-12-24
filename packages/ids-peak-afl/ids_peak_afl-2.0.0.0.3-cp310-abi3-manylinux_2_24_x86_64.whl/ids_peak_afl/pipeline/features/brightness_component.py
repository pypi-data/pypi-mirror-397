from __future__ import annotations
from typing import TYPE_CHECKING

from ids_peak_common import Interval
from ids_peak_common.serialization import ISerializable, IArchive

from ids_peak_afl.ids_peak_afl import Controller as RawController
from ids_peak_afl.ids_peak_afl import (
    PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_INVALID,
    PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_EXPOSURE,
    PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_ANALOG_GAIN,
    PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_DIGITAL_GAIN,
    PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_COMBINED_GAIN,
    PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_HOST_GAIN,
    PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_GAIN,
)

from ids_peak_afl.pipeline.datatypes import NamedIntEnum
from ids_peak_afl.pipeline.features.ifeature import IFeature
from ids_peak_afl.pipeline.modules.controllers import ControllerMode
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
    get_archive_and_reraise as _get_archive_and_reraise,
    assert_parameter_type as _assert_parameter_type,
)

if TYPE_CHECKING:
    from ids_peak_afl.pipeline.features.brightness_limit import (
        BrightnessLimit,
    )


class BrightnessComponentType(NamedIntEnum):
    """
    Enumeration of brightness component types.

    Defines the different component types used to adjust image brightness.

    .. versionadded:: 2.0
    """

    INVALID = (PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_INVALID, "Invalid")
    """
    This value serves as a placeholder type and should not be used
    for any operations.
    """

    EXPOSURE = (
        PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_EXPOSURE,
        "ComponentExposure",
    )
    """
    Adjusts the camera’s exposure time to control brightness.
    Longer exposure increases brightness but can introduce motion blur.
    """

    ANALOG_GAIN = (
        PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_ANALOG_GAIN,
        "ComponentAnalogGain",
    )
    """
    Adjusts the sensor’s analog gain before digitization. Provides a good
    signal-to-noise ratio but may have a limited adjustment range.
    This method is preferred over digital gain when available.
    """

    DIGITAL_GAIN = (
        PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_DIGITAL_GAIN,
        "ComponentDigitalGain",
    )
    """
    Adjusts the digital camera gain after sensor readout.
    Offers a wider adjustment range than analog gain but amplifies
    image noise.
    """

    COMBINED_GAIN = (
        PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_COMBINED_GAIN,
        "ComponentCombinedGain",
    )
    """
    Controls both analog and digital gain for optimal signal-to-noise ratio.
    Typically increases analog gain first, then applies digital gain to
    extend the range.
    """

    HOST_GAIN = (
        PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_HOST_GAIN,
        "ComponentHostGain",
    )
    """
    Applies host gain in software after image acquisition.
    This amplifies noise and increases CPU usage.
    """

    GAIN = (PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_GAIN, "ComponentGain")
    """
    Automatically selects the type of gain to adjust
    (analog, digital, combined, or host) based on the camera’s supported
    features.
    """


class BrightnessComponent(ISerializable):
    def __init__(
        self,
        parent: RawController,
        component_type: BrightnessComponentType,
        brightness_limit: BrightnessLimit,
    ) -> None:
        self._parent = parent
        self._component_type = component_type
        self._brightness_limit = brightness_limit

    @property
    def component_type(self) -> BrightnessComponentType:
        return self._component_type

    def serialize(self, archive: IArchive) -> None:
        archive.set("Mode", self.mode.string_value)

        limit_archive = archive.create_archive()
        self._brightness_limit.serialize(limit_archive)

        archive.set("Limit", limit_archive)

    def deserialize(self, archive: IArchive) -> None:
        limit_archive = _get_archive_and_reraise(archive, "Limit")
        self._brightness_limit.deserialize(limit_archive)

        self.mode = ControllerMode.from_string(
            _get_and_reraise(archive, "Mode", str)
        )

    @property
    def mode(self) -> ControllerMode:
        return ControllerMode.from_int(
            self._parent.BrightnessComponentGetMode(self._component_type)
        )

    @mode.setter
    def mode(self, mode: ControllerMode) -> None:
        _assert_parameter_type(mode, ControllerMode, "mode")
        self._parent.BrightnessComponentSetMode(self._component_type, mode)

    @property
    def limit_range(self) -> Interval:
        return self._brightness_limit.range

    @property
    def limit(self) -> Interval:
        return self._brightness_limit.value

    @limit.setter
    def limit(self, interval: Interval) -> None:
        self._brightness_limit.value = interval

    @property
    def limit_feature(self) -> IFeature[Interval]:
        return self._brightness_limit
