from abc import abstractmethod
from typing import TypeVar, Generic, Sequence

from ids_peak_common import Range
from ids_peak_common.serialization import ISerializable

T = TypeVar("T")


class IFeature(ISerializable, Generic[T]):
    """
    Base interface for auto feature implementations

    The ``IFeature`` generic class provides the interface for all auto feature
    implementations. It defines the basic operations that all features must
    support: getting and setting values, serialization and deserialization.

    :type T: The type of value that this feature manages (e.g., ``int``,
             ``BrightnessAnalysisAlgorithm``, ``Rectangle``)

    .. versionadded:: 2.0
    """

    @property
    @abstractmethod
    def value(self) -> T:
        """
        Returns the value of this feature.

        .. versionadded:: 2.0
        """

    @value.setter
    @abstractmethod
    def value(self, value: T) -> None:
        """
        Sets the value of this feature.

        .. versionadded:: 2.0
        """


class IRangeFeature(IFeature[T]):
    """
    Interface for features that have a valid range of values.

    :type T: The numeric type that this range feature manages

    .. versionadded:: 2.0
    """

    @property
    @abstractmethod
    def range(self) -> Range:
        """
        Returns the valid range for this feature

        .. versionadded:: 2.0
        """


class IListFeature(IFeature[T]):
    """
    Interface for features that have a list of valid values.

    :type T: The enumerated type that this list feature manages

    .. versionadded:: 2.0
    """

    @property
    @abstractmethod
    def list(self) -> Sequence[T]:
        """
         Returns a list of valid values for this feature

        .. versionadded:: 2.0
        """
