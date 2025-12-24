from __future__ import annotations

from enum import IntEnum
from typing import TypeVar, Type, cast
from ids_peak_afl.exceptions import InvalidParameterException

E = TypeVar("E", bound="NamedIntEnum")


class NamedIntEnum(IntEnum):
    """
    Enumeration class that associates each integer value with a
    corresponding string value.

    .. versionadded:: 2.0
    """

    int_value: int
    string_value: str

    def __new__(cls: Type[E], int_value: int, string_value: str) -> E:
        """
        Create a new enum member with the given integer and string values.

        .. versionadded:: 2.0
        """
        obj = cast(E, int.__new__(cls, int_value))
        obj._value_ = int_value
        obj.int_value = int_value
        obj.string_value = string_value
        return obj

    @classmethod
    def from_int(cls: Type[E], value: int) -> E:
        """
        Returns the enum member matching the given ``int_value``.

        .. versionadded:: 2.0
        """
        for member in cls:
            if member.int_value == value:
                return member
        raise InvalidParameterException(
            f"Value '{value}' is not a valid {cls.__name__} entry"
        )

    @classmethod
    def from_string(cls: Type[E], name: str) -> E:
        """
        Returns the enum member matching the given ``string_value``
        (case-sensitive).

        .. versionadded:: 2.0
        """
        for member in cls:
            if member.string_value == name:
                return member
        raise InvalidParameterException(
            f"{name!r} is not a valid {cls.__name__} entry"
        )
