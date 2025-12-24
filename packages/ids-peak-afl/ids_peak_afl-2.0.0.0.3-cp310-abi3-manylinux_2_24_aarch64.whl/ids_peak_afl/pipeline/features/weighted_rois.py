from dataclasses import dataclass

from ids_peak_common import Rectangle, Point, Size
from ids_peak_common.serialization import IArchive

from ids_peak_afl.ids_peak_afl import (
    Controller,
    WeightedRectangleList,
    peak_afl_weighted_rectangle,
    PEAK_AFL_CONTROLLER_ROI_WEIGHT_WEAK,
    PEAK_AFL_CONTROLLER_ROI_WEIGHT_MEDIUM,
    PEAK_AFL_CONTROLLER_ROI_WEIGHT_STRONG,
    PEAK_AFL_CONTROLLER_ROI_PRESET_CENTER,
)

from ids_peak_afl.exceptions import InvalidParameterException

from ids_peak_afl.pipeline.features.ifeature import IFeature
from ids_peak_afl.pipeline.datatypes.datatypes import NamedIntEnum
from ids_peak_afl.pipeline._internal.utils import (
    get_and_reraise as _get_and_reraise,
)


class RoiWeight(NamedIntEnum):
    """
    Enumeration of ROI weight levels.

    Defines the influence of a region of interest (ROI) on focus calculations.
    Regions with higher weights are more important during autofocus evaluation.

    .. versionadded:: 2.0
    """

    WEAK = (PEAK_AFL_CONTROLLER_ROI_WEIGHT_WEAK, "Weak")
    """
    Assigns minimal influence to the region in focus calculations.
    Suitable for background or less important areas.
    """

    MEDIUM = (PEAK_AFL_CONTROLLER_ROI_WEIGHT_MEDIUM, "Medium")
    """
    Assigns moderate influence to the region in focus calculations.
    Suitable for areas of average importance within the scene.
    """

    STRONG = (PEAK_AFL_CONTROLLER_ROI_WEIGHT_STRONG, "Strong")
    """
    Assigns strong influence to the region in focus calculations.
    Suitable for critical areas that must remain sharply focused.
    """


class RoiPreset(NamedIntEnum):
    """
    Preset enumeration for the region of interest

    ROI configurations that can be applied
    without manually specifying coordinates. These presets
    automatically adapt to the current image size.

    .. versionadded:: 2.0
    """

    CENTER = (PEAK_AFL_CONTROLLER_ROI_PRESET_CENTER, "Center")
    """    
    Defines a centered region of interest.
    The size determined by the preset scales with the image dimensions,
    covering approximately 1/15th of the image area.
    """


@dataclass
class WeightedRoi:
    rect: Rectangle
    weight: RoiWeight


class WeightedRois(IFeature[list[WeightedRoi]]):
    """
    This feature allows defining multiple region of interests (ROIs) within the
    image, each with different importance weights that influence automatic
    algorithms.

    Weighted ROIs are useful for prioritizing important subjects in the scene.

    Each weighted ROI consists of a rectangular region and a weight
    (Weak, Medium, Strong) that determines how much influence that region
    has on the automatic calculations.

    .. versionadded:: 2.0
    """

    def __init__(self, controller: Controller) -> None:
        """
        Creates an WeightedRois feature with the specified controller

        :param controller: The auto controller that will be used to manage the
                           weighted rois parameter.

        .. versionadded:: 2.0
        """
        self._controller = controller

    @property
    def value(self) -> list[WeightedRoi]:
        """
        Returns a list of weighted rois

        .. versionadded:: 2.0
        """
        weighted = self._controller.GetWeightedROIs()
        out = list()
        for wroi in weighted:
            out.append(
                WeightedRoi(
                    Rectangle(
                        Point(wroi.roi.x, wroi.roi.y),
                        Size(wroi.roi.width, wroi.roi.height),
                    ),
                    RoiWeight.from_int(wroi.weight),
                )
            )
        return out

    @value.setter
    def value(self, value: list[WeightedRoi]) -> None:
        """
        Sets a list of weighted rois

        :param value: A list of weighted rois to set. Use ``set_single`` to
                      for setting only a single roi.

        .. versionadded:: 2.0
        """
        weighted_list = list()
        for wroi in value:
            self._check_rectangle_size(wroi.rect)
            weighted = peak_afl_weighted_rectangle()
            weighted.roi.x = int(wroi.rect.x)
            weighted.roi.y = int(wroi.rect.y)
            weighted.roi.width = int(wroi.rect.width)
            weighted.roi.height = int(wroi.rect.height)
            weighted.weight = wroi.weight
            weighted_list.append(weighted)

        self._controller.SetWeightedROIs(WeightedRectangleList(weighted_list))

    def set_single(self, wroi: WeightedRoi) -> None:
        """
        Sets a single weighted roi

        :param wroi: A weighted roi to set. Use ``value`` to set a list of
                     multiple weighted rois.

        .. versionadded:: 2.0
        """
        self._check_rectangle_size(wroi.rect)

        weighted = peak_afl_weighted_rectangle()
        weighted.roi.x = int(wroi.rect.x)
        weighted.roi.y = int(wroi.rect.y)
        weighted.roi.width = int(wroi.rect.width)
        weighted.roi.height = int(wroi.rect.height)
        weighted.weight = wroi.weight
        self._controller.SetWeightedROI(weighted)

    def set_preset(self, preset: RoiPreset) -> None:
        """
        Sets the region of interest (ROI) to a predefined preset.

        Presets provide convenient configurations for positioning and sizing the ROI.

        :param preset: The predefined ROI preset to apply.

        .. versionadded:: 2.0
        """

        self._controller.SetROIPreset(preset)

    def serialize(self, archive: IArchive) -> None:
        """
        Stores the current state of this feature to an archive.

        :param archive: The archive in which this feature's state will
                        be stored.

        .. versionadded:: 2.0
        """
        archives: list[IArchive] = []
        for roi in self.value:
            sub_archive = archive.create_archive()
            sub_archive.set("X", roi.rect.x)
            sub_archive.set("Y", roi.rect.y)
            sub_archive.set("Width", roi.rect.width)
            sub_archive.set("Height", roi.rect.height)
            sub_archive.set("Weight", roi.weight.string_value)

            archives.append(sub_archive)

        archive.set("WeightedRois", archives)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores this feature's state from an archive.

        :param archive: The archive from which the state will be restored.
        :raises ids_peak_afl.exceptions.CorruptedDataException:
                if deserialization fails because of a corrupted file

        .. versionadded:: 2.0
        """
        rois: list[WeightedRoi] = []
        archives = _get_and_reraise(archive, "WeightedRois", list)
        for arch in archives:
            x = _get_and_reraise(arch, "X", int)
            y = _get_and_reraise(arch, "Y", int)
            width = _get_and_reraise(arch, "Width", int)
            height = _get_and_reraise(arch, "Height", int)
            weight = RoiWeight.from_string(
                _get_and_reraise(arch, "Weight", str)
            )

            rect = Rectangle(Point(x, y), Size(width, height))
            rois.append(WeightedRoi(rect, weight))

        self.value = rois

    def _check_rectangle_size(self, rect: Rectangle) -> None:
        if rect.width < 20 or rect.height < 20:
            raise InvalidParameterException(
                "Rectangle is too small. The `Size` must be at least 20 x 20."
            )
