from typing import Type, Any

from ids_peak_common.serialization import IArchive

from ids_peak_afl.exceptions import (
    CorruptedDataException,
    InvalidParameterException,
)


def get_and_reraise(
    archive: IArchive, key: str, datatype: Type[IArchive.T]
) -> IArchive.T:
    """
    Returns the key from the archive or raises ``CorruptedDataException``.
    """
    try:
        return archive.get(key, datatype)
    except KeyError as e:
        raise CorruptedDataException(
            f"The given archive is corrupted. The key '{key}' is missing."
        ) from e
    except Exception as e:
        raise CorruptedDataException(
            f"There was an error while getting key '{key}' from the archive."
        ) from e


def get_archive_and_reraise(archive: IArchive, key: str) -> IArchive:
    """
    Returns the sub-archive from the archive or
    raises ``CorruptedDataException``.
    """
    try:
        return archive.get_archive(key)
    except KeyError as e:
        raise CorruptedDataException(
            f"The given archive is corrupted. The key '{key}' is missing."
        ) from e
    except Exception as e:
        raise CorruptedDataException(
            f"There was an error while getting key '{key}' from the archive."
        ) from e


def assert_parameter_type(obj: Any, _type: type, parameter: str) -> None:
    """
    Checks if the given object is of the expected type and
    raises ``InvalidParameterException`` if not.
    """
    if not isinstance(obj, _type):
        raise InvalidParameterException(
            f"Invalid type for parameter `{parameter}`, "
            f"expected `{str(_type)}`, got `{type(obj)}`"
        )
