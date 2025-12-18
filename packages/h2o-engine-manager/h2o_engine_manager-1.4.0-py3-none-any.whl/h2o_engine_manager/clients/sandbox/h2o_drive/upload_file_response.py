import pprint

from h2o_engine_manager.gen.model.v1_upload_file_response import V1UploadFileResponse


class UploadFileResponse:
    """
    UploadFileResponse contains the result of uploading a file to H2O Drive.
    """

    def __init__(
        self,
        bytes_uploaded: int = 0,
    ):
        """
        UploadFileResponse represents the result of uploading a file to H2O Drive.

        Args:
            bytes_uploaded: The number of bytes read from the local filesystem and uploaded.
        """
        self.bytes_uploaded = bytes_uploaded

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def upload_file_response_from_api_object(
    api_object: V1UploadFileResponse,
) -> UploadFileResponse:
    return UploadFileResponse(
        bytes_uploaded=int(api_object.bytes_uploaded)
        if api_object.bytes_uploaded
        else 0,
    )
