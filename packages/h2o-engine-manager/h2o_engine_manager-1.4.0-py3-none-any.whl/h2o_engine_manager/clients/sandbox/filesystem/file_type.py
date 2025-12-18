from enum import Enum

from h2o_engine_manager.gen.model.v1_file_type import V1FileType


class FileType(Enum):
    """FileType indicates the type of filesystem entry."""

    FILE_TYPE_UNSPECIFIED = "FILE_TYPE_UNSPECIFIED"
    FILE_TYPE_REGULAR = "FILE_TYPE_REGULAR"
    FILE_TYPE_DIRECTORY = "FILE_TYPE_DIRECTORY"
    FILE_TYPE_SYMLINK = "FILE_TYPE_SYMLINK"

    def to_api_object(self) -> V1FileType:
        return V1FileType(self.value)


def file_type_from_api_object(api_object: V1FileType) -> FileType:
    return FileType(api_object.value)