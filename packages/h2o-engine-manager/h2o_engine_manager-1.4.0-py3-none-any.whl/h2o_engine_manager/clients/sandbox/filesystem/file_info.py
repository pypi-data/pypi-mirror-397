import pprint
from datetime import datetime
from typing import Optional

from h2o_engine_manager.clients.sandbox.filesystem.file_type import FileType
from h2o_engine_manager.clients.sandbox.filesystem.file_type import (
    file_type_from_api_object,
)
from h2o_engine_manager.gen.model.v1_file_info import V1FileInfo


class FileInfo:
    """
    FileInfo contains metadata about a file or directory.
    """

    def __init__(
        self,
        path: str = "",
        size: int = 0,
        file_type: FileType = FileType.FILE_TYPE_UNSPECIFIED,
        modify_time: Optional[datetime] = None,
        mode: str = "",
    ):
        """
        FileInfo represents metadata about a file or directory.

        Args:
            path: The absolute path of the file or directory.
            size: The size of the file in bytes.
                For directories, this is typically 0 or the size of the directory metadata.
            file_type: The type of the filesystem entry (regular file, directory, or symlink).
            modify_time: The last modification time of the file or directory (mtime).
            mode: Unix file mode and permission bits in octal notation.
                Examples: "0644" (rw-r--r--), "0755" (rwxr-xr-x), "0777" (rwxrwxrwx).
        """
        self.path = path
        self.size = size
        self.type = file_type
        self.modify_time = modify_time
        self.mode = mode

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def file_info_from_api_object(api_object: V1FileInfo) -> FileInfo:
    return FileInfo(
        path=api_object.path if api_object.path else "",
        size=int(api_object.size) if api_object.size else 0,
        file_type=file_type_from_api_object(api_object=api_object.type),
        modify_time=api_object.modify_time,
        mode=api_object.mode if api_object.mode else "",
    )