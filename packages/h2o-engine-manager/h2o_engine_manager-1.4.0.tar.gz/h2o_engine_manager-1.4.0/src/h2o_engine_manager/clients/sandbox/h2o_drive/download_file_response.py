import pprint
from typing import Optional

from h2o_engine_manager.clients.sandbox.filesystem.file_info import FileInfo
from h2o_engine_manager.clients.sandbox.filesystem.file_info import (
    file_info_from_api_object,
)
from h2o_engine_manager.gen.model.v1_download_file_response import (
    V1DownloadFileResponse,
)


class DownloadFileResponse:
    """
    DownloadFileResponse contains the result of downloading a file from H2O Drive.
    """

    def __init__(
        self,
        file_info: Optional[FileInfo] = None,
    ):
        """
        DownloadFileResponse represents the result of downloading a file from H2O Drive.

        Args:
            file_info: Metadata about the downloaded file written to the sandbox filesystem.
        """
        self.file_info = file_info

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def download_file_response_from_api_object(
    api_object: V1DownloadFileResponse,
) -> DownloadFileResponse:
    file_info = None
    if api_object.file_info:
        file_info = file_info_from_api_object(api_object=api_object.file_info)

    return DownloadFileResponse(
        file_info=file_info,
    )
