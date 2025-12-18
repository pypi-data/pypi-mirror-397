import base64
import pprint

from h2o_engine_manager.clients.sandbox.filesystem.file_info import FileInfo
from h2o_engine_manager.clients.sandbox.filesystem.file_info import (
    file_info_from_api_object,
)
from h2o_engine_manager.gen.model.v1_read_file_response import V1ReadFileResponse


class ReadFileResponse:
    """
    Response from reading a file.
    """

    def __init__(
        self,
        content: bytes,
        file_info: FileInfo,
    ):
        """
        ReadFileResponse contains the file content and metadata.

        Args:
            content: The raw content of the file as bytes.
            file_info: Metadata about the file.
        """
        self.content = content
        self.file_info = file_info

    def __repr__(self) -> str:
        return pprint.pformat({
            "content": f"<{len(self.content)} bytes>",
            "file_info": self.file_info,
        })

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def read_file_response_from_api_object(
    api_object: V1ReadFileResponse,
) -> ReadFileResponse:
    # Decode base64 content back to bytes
    content = b""
    if api_object.content:
        if isinstance(api_object.content, str):
            # Content is base64-encoded string, decode it
            content = base64.b64decode(api_object.content)
        else:
            # Content is already bytes
            content = api_object.content

    return ReadFileResponse(
        content=content,
        file_info=file_info_from_api_object(api_object=api_object.file_info),
    )