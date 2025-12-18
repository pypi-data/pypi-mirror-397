from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox.h2o_drive.download_file_response import (
    DownloadFileResponse,
)
from h2o_engine_manager.clients.sandbox.h2o_drive.download_file_response import (
    download_file_response_from_api_object,
)
from h2o_engine_manager.clients.sandbox.h2o_drive.upload_file_response import (
    UploadFileResponse,
)
from h2o_engine_manager.clients.sandbox.h2o_drive.upload_file_response import (
    upload_file_response_from_api_object,
)
from h2o_engine_manager.gen import ApiException
from h2o_engine_manager.gen import Configuration
from h2o_engine_manager.gen.api.h2_o_drive_service_api import H2ODriveServiceApi
from h2o_engine_manager.gen.model.h2_o_drive_service_download_file_request import (
    H2ODriveServiceDownloadFileRequest,
)
from h2o_engine_manager.gen.model.h2_o_drive_service_upload_file_request import (
    H2ODriveServiceUploadFileRequest,
)


class H2ODriveClient:
    """H2ODriveClient manages H2O Drive operations within a SandboxEngine.

    This client provides methods to upload and download files between a SandboxEngine's
    filesystem and H2O Drive cloud storage. The AI Engine Manager acts as a proxy,
    so the sandbox engine does not connect directly to H2O Drive.
    """

    def __init__(
        self,
        connection_config: ConnectionConfig,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
    ):
        """
        Args:
            connection_config: AIEM connection configuration object.
            verify_ssl: Set to False to disable SSL certificate verification.
            ssl_ca_cert: Path to a CA cert bundle with certificates of trusted CAs.
        """

        configuration = Configuration(host=connection_config.aiem_url)
        configuration.verify_ssl = verify_ssl
        configuration.ssl_ca_cert = ssl_ca_cert

        with TokenApiClient(
            configuration, connection_config.token_provider
        ) as api_client:
            self.service_api = H2ODriveServiceApi(api_client)

    def download_file(
        self,
        name: str,
        remote_path: str,
        local_path: str,
        workspace: Optional[str] = None,
        create_parent_directories: bool = False,
        overwrite: Optional[bool] = None,
    ) -> DownloadFileResponse:
        """
        Download a file from H2O Drive to the sandbox filesystem.

        Retrieves a file from H2O Drive and writes it to the specified path
        in the sandbox filesystem. The caller must have read permissions for
        the specified workspace.

        Args:
            name (str): SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            remote_path (str): The relative path of the file in H2O Drive to download.
                Must be relative to the workspace root (no leading slash).
                Example: "data/input.csv"
            local_path (str): The absolute path in the sandbox filesystem where
                the file should be written.
                Must start with a forward slash (e.g., "/workspace/data/input.csv").
            workspace (Optional[str]): The workspace resource name to use for H2O Drive access.
                Format: "workspaces/*"
                If not specified, defaults to the sandbox engine's parent workspace.
            create_parent_directories (bool): If True, creates parent directories
                if they don't exist. Defaults to False.
            overwrite (Optional[bool]): Controls overwrite behavior.
                If True or None, overwrites the file if it exists.
                If False, the operation will fail if the file already exists.

        Returns:
            DownloadFileResponse: Response containing metadata about the downloaded file.
        """
        body_kwargs = {
            "remote_path": remote_path,
            "local_path": local_path,
            "create_parent_directories": create_parent_directories,
        }
        if workspace is not None:
            body_kwargs["workspace"] = workspace
        if overwrite is not None:
            body_kwargs["overwrite"] = overwrite
        body = H2ODriveServiceDownloadFileRequest(**body_kwargs)

        try:
            api_response = self.service_api.h2_o_drive_service_download_file(
                name=name,
                body=body,
            )
            return download_file_response_from_api_object(api_object=api_response)
        except ApiException as e:
            raise CustomApiException(e)

    def upload_file(
        self,
        name: str,
        local_path: str,
        remote_path: str,
        workspace: Optional[str] = None,
    ) -> UploadFileResponse:
        """
        Upload a file from the sandbox filesystem to H2O Drive.

        Reads a file from the sandbox filesystem and stores it in H2O Drive
        at the specified path. If the file already exists in H2O Drive, it
        will be overwritten. The caller must have write permissions for the
        specified workspace.

        Args:
            name (str): SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            local_path (str): The absolute path of the file in the sandbox filesystem
                to upload.
                Must start with a forward slash (e.g., "/workspace/output/results.csv").
            remote_path (str): The relative path in H2O Drive where the file should be stored.
                Must be relative to the workspace root (no leading slash).
                Example: "output/results.csv"
            workspace (Optional[str]): The workspace resource name to use for H2O Drive access.
                Format: "workspaces/*"
                If not specified, defaults to the sandbox engine's parent workspace.

        Returns:
            UploadFileResponse: Response containing the number of bytes uploaded.
        """
        body_kwargs = {
            "local_path": local_path,
            "remote_path": remote_path,
        }
        if workspace is not None:
            body_kwargs["workspace"] = workspace
        body = H2ODriveServiceUploadFileRequest(**body_kwargs)

        try:
            api_response = self.service_api.h2_o_drive_service_upload_file(
                name=name,
                body=body,
            )
            return upload_file_response_from_api_object(api_object=api_response)
        except ApiException as e:
            raise CustomApiException(e)
