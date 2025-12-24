import sys
from collections.abc import Callable

from ids_peak_common import Interval
from ids_peak_common.serialization import IArchive
from ids_peak_afl.exceptions import InvalidParameterException

from ids_peak_afl.ids_peak_afl import (
    peak_afl_double_limit,
    Controller as RawController,
)

from ids_peak_afl.pipeline.features.ifeature import IFeature
from ids_peak_afl.pipeline.features import BrightnessComponentType
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
)


class BrightnessLimit(IFeature[Interval]):
    """
    Brightness limit feature implementation for auto controllers

    Brightness limits define the allowable range for specific parameters that
    affect image brightness i.e. exposure and gain. These limits prevent the
    automatic algorithms from setting values outside acceptable ranges.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        setter: Callable[[Interval], None],
        getter: Callable[[], Interval],
        range_getter: Callable[[], Interval],
    ) -> None:
        """
        Creates an BrightnessLimit feature with the specified controller

        :param setter: Setter function for setting the brightness limit
        :param getter: Getter function for getting the brightness limit
        :param range_getter: Getter function for getting the brightness limit
                             range

        .. versionadded:: 2.0
        """
        self._getter = getter
        self._setter = setter
        self._range_getter = range_getter

    @property
    def value(self) -> Interval:
        """
        Returns the brightness limit

        .. versionadded:: 2.0
        """
        return self._getter()

    @value.setter
    def value(self, value: Interval) -> None:
        """
        Sets the brightness limit

        :param value: The brightness limit to set. Use ``range`` to get
                      the valid interval.

        .. versionadded:: 2.0
        """
        self._setter(value)

    @property
    def range(self) -> Interval:
        """
        Returns the valid interval for brightness limit

        .. versionadded:: 2.0
        """
        return self._range_getter()

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        interval = self.value
        archive.set("Min", interval.minimum)
        archive.set("Max", interval.maximum)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        interval_min = _get_and_reraise(archive, "Min", float)
        interval_max = _get_and_reraise(archive, "Max", float)

        self.value = Interval(interval_min, interval_max)


def _create_brightness_limit(
    controller: RawController, component_type: BrightnessComponentType
) -> BrightnessLimit:
    def to_interval(limit: peak_afl_double_limit) -> Interval:
        return Interval(limit.min, limit.max)

    def to_double_limit(interval: Interval) -> peak_afl_double_limit:
        limit = peak_afl_double_limit()
        limit.min = interval.minimum
        limit.max = interval.maximum
        return limit

    if component_type is BrightnessComponentType.EXPOSURE:
        return BrightnessLimit(
            lambda x: controller.SetExposureLimit(to_double_limit(x)),
            lambda: to_interval(controller.GetExposureLimit()),
            lambda: to_interval(controller.GetExposureLimitRange()),
        )
    if component_type is BrightnessComponentType.GAIN:
        return BrightnessLimit(
            lambda x: controller.SetGainLimit(to_double_limit(x)),
            lambda: to_interval(controller.GetGainLimit()),
            lambda: to_interval(controller.GetGainLimitRange()),
        )
    if component_type is BrightnessComponentType.ANALOG_GAIN:
        return BrightnessLimit(
            lambda x: controller.SetGainAnalogLimit(to_double_limit(x)),
            lambda: to_interval(controller.GetGainAnalogLimit()),
            lambda: to_interval(controller.GetGainAnalogLimitRange()),
        )
    if component_type is BrightnessComponentType.DIGITAL_GAIN:
        return BrightnessLimit(
            lambda x: controller.SetGainDigitalLimit(to_double_limit(x)),
            lambda: to_interval(controller.GetGainDigitalLimit()),
            lambda: to_interval(controller.GetGainDigitalLimitRange()),
        )
    if component_type is BrightnessComponentType.COMBINED_GAIN:
        return BrightnessLimit(
            lambda x: controller.SetGainCombinedLimit(to_double_limit(x)),
            lambda: to_interval(controller.GetGainCombinedLimit()),
            lambda: to_interval(controller.GetGainCombinedLimitRange()),
        )
    if component_type is BrightnessComponentType.HOST_GAIN:
        return BrightnessLimit(
            lambda x: controller.SetGainHostLimit(to_double_limit(x)),
            lambda: to_interval(controller.GetGainHostLimit()),
            lambda: to_interval(controller.GetGainHostLimitRange()),
        )

    raise InvalidParameterException("Unknown component type")
