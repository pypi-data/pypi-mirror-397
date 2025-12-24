from ids_peak_afl.ids_peak_afl import (
    PEAK_AFL_CONTROLLER_AUTOMODE_OFF,
    PEAK_AFL_CONTROLLER_AUTOMODE_CONTINUOUS,
    PEAK_AFL_CONTROLLER_AUTOMODE_ONCE,
    PEAK_AFL_CONTROLLER_TYPE_BRIGHTNESS,
    PEAK_AFL_CONTROLLER_TYPE_WHITE_BALANCE,
    PEAK_AFL_CONTROLLER_TYPE_AUTOFOCUS,
)

from ids_peak_afl.pipeline.datatypes import NamedIntEnum


class ControllerMode(NamedIntEnum):
    """
    Enumeration of controller operation modes.

    Defines the modes in which an automatic controller can operate. Each mode
    specifies how and when the automatic algorithms are executed.

    .. versionadded:: 2.0
    """

    OFF = (PEAK_AFL_CONTROLLER_AUTOMODE_OFF, "Off")
    """
    The controller is disabled; image processing is bypassed,
    and parameters are not adjusted.
    """

    CONTINUOUS = (PEAK_AFL_CONTROLLER_AUTOMODE_CONTINUOUS, "Continuous")
    """
    The controller continuously processes images and
    adjusts parameters as needed.

    When the setpoint is reached, the parameter adjustment is suspended until
    changes in the scene require further correction.
    """

    ONCE = (PEAK_AFL_CONTROLLER_AUTOMODE_ONCE, "Once")
    """
    The controller processes images and adjusts parameters as needed
    until the setpoint is reached.

    Once the setpoint is reached, parameter adjustment stops and
    the controller switches to ``OFF`` mode.
    """


class ControllerType(NamedIntEnum):
    """
    Enumeration of controller types.

    Defines the automatic controller type. Each type is
    specialized to manage a specific aspect of automatic camera control.

    .. versionadded:: 2.0
    """

    FOCUS = (PEAK_AFL_CONTROLLER_TYPE_AUTOFOCUS, "Focus")
    """
    Adjusts the focal length automatically to achieve maximum image sharpness.
    """

    BRIGHTNESS = (PEAK_AFL_CONTROLLER_TYPE_BRIGHTNESS, "Brightness")
    """
    Manages exposure time and gain settings to maintain optimal
    image brightness.
    """

    WHITE_BALANCE = (
        PEAK_AFL_CONTROLLER_TYPE_WHITE_BALANCE,
        "WhiteBalance",
    )
    """
    Adjusts color gains to compensate for varying lighting conditions
    and maintain accurate colors.
    """
