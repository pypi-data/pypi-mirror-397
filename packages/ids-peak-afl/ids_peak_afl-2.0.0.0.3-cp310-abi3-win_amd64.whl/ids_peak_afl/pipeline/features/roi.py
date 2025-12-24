from ids_peak_common.datatypes import Rectangle, Point, Size
from ids_peak_common.serialization import IArchive
from ids_peak_afl.exceptions import InvalidParameterException

from ids_peak_afl.ids_peak_afl import Controller, peak_afl_rectangle

from ids_peak_afl.pipeline.features.ifeature import IFeature
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
    get_archive_and_reraise as _get_archive_and_reraise,
)


class Roi(IFeature[Rectangle]):
    """
    This feature defines a rectangular region of interest (ROI) within the
    image, allowing auto feature algorithms to restrict their analysis to a
    specific area.

    .. versionadded:: 2.0
    """

    def __init__(self, controller: Controller) -> None:
        """
        Creates an Roi feature with the specified controller

        :param controller: The auto controller that will be used to manage the
                           roi parameter.

        .. versionadded:: 2.0
        """
        self._controller = controller

    @property
    def value(self) -> Rectangle:
        """
        Returns the roi

        .. versionadded:: 2.0
        """
        roi = self._controller.GetROI()
        return Rectangle(Point(roi.x, roi.y), Size(roi.width, roi.height))

    @value.setter
    def value(self, value: Rectangle) -> None:
        """
        Sets the roi

        :param value: The region of interest (ROI) to set. The rectangle must
                      be fully contained within the image being processed.

        :raises ids_peak_afl.exceptions.InvalidParameterException: if x or y are negative

        .. versionadded:: 2.0
        """
        if value.x < 0 or value.y < 0:
            raise InvalidParameterException(
                "Negative x or y is not supported!"
            )

        rect = peak_afl_rectangle()
        rect.x = int(value.x)
        rect.y = int(value.y)
        rect.width = int(value.width)
        rect.height = int(value.height)
        self._controller.SetROI(rect)

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        sub_archive = archive.create_archive()
        rect = self.value

        sub_archive.set("X", rect.x)
        sub_archive.set("Y", rect.y)
        sub_archive.set("Width", rect.width)
        sub_archive.set("Height", rect.height)

        archive.set("Roi", sub_archive)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        sub_archive = _get_archive_and_reraise(archive, "Roi")

        x = _get_and_reraise(sub_archive, "X", int)
        y = _get_and_reraise(sub_archive, "Y", int)
        width = _get_and_reraise(sub_archive, "Width", int)
        height = _get_and_reraise(sub_archive, "Height", int)

        self.value = Rectangle(Point(x, y), Size(width, height))
