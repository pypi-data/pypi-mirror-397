import pprint

from h2o_engine_manager.clients.sandbox.filesystem.file_info import FileInfo
from h2o_engine_manager.clients.sandbox.filesystem.file_info import (
    file_info_from_api_object,
)
from h2o_engine_manager.gen.model.v1_write_file_response import V1WriteFileResponse


class WriteFileResponse:
    """
    Response from writing a file.
    """

    def __init__(
        self,
        file_info: FileInfo,
    ):
        """
        WriteFileResponse contains metadata about the written file.

        Args:
            file_info: Metadata about the written file.
        """
        self.file_info = file_info

    def __repr__(self) -> str:
        return pprint.pformat({
            "file_info": self.file_info,
        })

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def write_file_response_from_api_object(
    api_object: V1WriteFileResponse,
) -> WriteFileResponse:
    return WriteFileResponse(
        file_info=file_info_from_api_object(api_object=api_object.file_info),
    )