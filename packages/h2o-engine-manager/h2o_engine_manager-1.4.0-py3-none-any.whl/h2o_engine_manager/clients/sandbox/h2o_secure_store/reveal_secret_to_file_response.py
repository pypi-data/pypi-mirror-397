import pprint
from typing import Optional

from h2o_engine_manager.clients.sandbox.filesystem.file_info import FileInfo
from h2o_engine_manager.clients.sandbox.filesystem.file_info import (
    file_info_from_api_object,
)
from h2o_engine_manager.gen.model.v1_reveal_secret_to_file_response import (
    V1RevealSecretToFileResponse,
)


class RevealSecretToFileResponse:
    """
    RevealSecretToFileResponse contains the result of revealing a secret to a file.
    """

    def __init__(
        self,
        secret_version: str = "",
        file_info: Optional[FileInfo] = None,
    ):
        """
        RevealSecretToFileResponse represents the result of revealing a secret to a file.

        Args:
            secret_version: The resource name of the SecretVersion that was revealed.
                Format: "workspaces/*/secrets/*/versions/*"
                If "latest" was used in the request, this will contain the actual version ID.
            file_info: Metadata about the written file.
        """
        self.secret_version = secret_version
        self.file_info = file_info

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def reveal_secret_to_file_response_from_api_object(
    api_object: V1RevealSecretToFileResponse,
) -> RevealSecretToFileResponse:
    file_info = None
    if api_object.file_info:
        file_info = file_info_from_api_object(api_object=api_object.file_info)

    return RevealSecretToFileResponse(
        secret_version=api_object.secret_version if api_object.secret_version else "",
        file_info=file_info,
    )
