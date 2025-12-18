import base64
from typing import List
from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox.filesystem.file_info import FileInfo
from h2o_engine_manager.clients.sandbox.filesystem.file_info import (
    file_info_from_api_object,
)
from h2o_engine_manager.clients.sandbox.filesystem.read_file_response import (
    ReadFileResponse,
)
from h2o_engine_manager.clients.sandbox.filesystem.read_file_response import (
    read_file_response_from_api_object,
)
from h2o_engine_manager.clients.sandbox.filesystem.write_file_response import (
    WriteFileResponse,
)
from h2o_engine_manager.clients.sandbox.filesystem.write_file_response import (
    write_file_response_from_api_object,
)
from h2o_engine_manager.gen import ApiException
from h2o_engine_manager.gen import Configuration
from h2o_engine_manager.gen.api.filesystem_service_api import FilesystemServiceApi
from h2o_engine_manager.gen.model.filesystem_service_make_directory_request import (
    FilesystemServiceMakeDirectoryRequest,
)
from h2o_engine_manager.gen.model.filesystem_service_move_request import (
    FilesystemServiceMoveRequest,
)
from h2o_engine_manager.gen.model.filesystem_service_remove_request import (
    FilesystemServiceRemoveRequest,
)
from h2o_engine_manager.gen.model.filesystem_service_write_file_request import (
    FilesystemServiceWriteFileRequest,
)


class FilesystemClient:
    """FilesystemClient manages filesystem operations within a SandboxEngine."""

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
            self.service_api = FilesystemServiceApi(api_client)

    def read_file(
        self,
        name: str,
        path: str,
    ) -> ReadFileResponse:
        """
        Read a file from the sandbox engine filesystem.

        Args:
            name (str): SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            path (str): The absolute path to the file to read.
                Must start with a forward slash (e.g., "/workspace/app.js").
                If the path is a symbolic link, it will be resolved to the target file.

        Returns:
            ReadFileResponse: Response containing file content and metadata.
        """
        try:
            api_response = self.service_api.filesystem_service_read_file(
                name=name,
                path=path,
            )
            return read_file_response_from_api_object(api_object=api_response)
        except ApiException as e:
            raise CustomApiException(e)

    def write_file(
        self,
        name: str,
        path: str,
        content: bytes,
        create_parent_directories: bool = False,
        overwrite: Optional[bool] = None,
    ) -> WriteFileResponse:
        """
        Write content to a file in the sandbox engine filesystem.

        Args:
            name (str): SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            path (str): The absolute path where the file should be written.
                Must start with a forward slash (e.g., "/workspace/app.js").
            content (bytes): The raw content to write to the file as bytes.
                For text files, provide UTF-8 encoded text.
            create_parent_directories (bool): If True, creates parent directories
                if they don't exist. Defaults to False.
            overwrite (Optional[bool]): Controls overwrite behavior.
                If True or None, overwrites the file if it exists.
                If False, the operation will fail if the file already exists.

        Returns:
            WriteFileResponse: Response containing metadata about the written file.
        """
        # Convert bytes to base64 string for the API
        content_base64 = base64.b64encode(content).decode('utf-8')

        body = FilesystemServiceWriteFileRequest(
            path=path,
            content=content_base64,
            create_parent_directories=create_parent_directories,
            overwrite=overwrite,
        )

        try:
            api_response = self.service_api.filesystem_service_write_file(
                name=name,
                body=body,
            )
            return write_file_response_from_api_object(api_object=api_response)
        except ApiException as e:
            raise CustomApiException(e)

    def remove(
        self,
        name: str,
        path: str,
        recursive: bool = False,
    ) -> None:
        """
        Remove (delete) a file or directory.

        Args:
            name (str): SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            path (str): The absolute path to the file or directory to delete.
                Must start with a forward slash (e.g., "/workspace/app.js").
                If the path is a symbolic link, the link itself is removed, not its target.
            recursive (bool): If True, removes directories and their contents recursively
                (similar to `rm -rf`). If False, non-empty directories will cause an error.
                Defaults to False.
        """
        body = FilesystemServiceRemoveRequest(
            path=path,
            recursive=recursive,
        )

        try:
            self.service_api.filesystem_service_remove(
                name=name,
                body=body,
            )
        except ApiException as e:
            raise CustomApiException(e)

    def move(
        self,
        name: str,
        source_path: str,
        destination_path: str,
        overwrite: Optional[bool] = None,
        create_parent_directories: bool = False,
    ) -> FileInfo:
        """
        Move or rename a file, directory, or symbolic link.

        Args:
            name (str): SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            source_path (str): The absolute path of the source.
                Must start with a forward slash (e.g., "/workspace/old.js").
                If the source is a symbolic link, the link itself is moved, not its target.
            destination_path (str): The absolute path of the destination.
                Must start with a forward slash (e.g., "/workspace/new.js").
            overwrite (Optional[bool]): If True, overwrites the destination if it exists.
                If False or None, the operation will fail if the destination exists.
                Defaults to None.
            create_parent_directories (bool): If True, creates parent directories
                of the destination path if they don't exist. Defaults to False.

        Returns:
            FileInfo: Metadata about the moved entry at its new location.
        """
        body = FilesystemServiceMoveRequest(
            source_path=source_path,
            destination_path=destination_path,
            overwrite=overwrite,
            create_parent_directories=create_parent_directories,
        )

        try:
            api_response = self.service_api.filesystem_service_move(
                name=name,
                body=body,
            )
            return file_info_from_api_object(api_object=api_response.file_info)
        except ApiException as e:
            raise CustomApiException(e)

    def list_directory(
        self,
        name: str,
        path: str,
    ) -> List[FileInfo]:
        """
        List files and directories in a given directory.

        Args:
            name (str): SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            path (str): The absolute path to the directory to list.
                Must start with a forward slash (e.g., "/workspace").
                Lists only direct children of the directory (non-recursive).

        Returns:
            List[FileInfo]: List of file and directory information.
        """
        try:
            api_response = self.service_api.filesystem_service_list_directory(
                name=name,
                path=path,
            )
            if not api_response.files:
                return []
            return [
                file_info_from_api_object(api_object=f) for f in api_response.files
            ]
        except ApiException as e:
            raise CustomApiException(e)

    def stat_file(
        self,
        name: str,
        path: str,
    ) -> FileInfo:
        """
        Get metadata about a file or directory (similar to Unix stat).

        Args:
            name (str): SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            path (str): The absolute path to the file or directory.
                Must start with a forward slash (e.g., "/workspace/app.js").
                If the path is a symbolic link, metadata about the target file
                is returned (symlink is followed).

        Returns:
            FileInfo: Metadata about the file or directory.
        """
        try:
            api_response = self.service_api.filesystem_service_stat_file(
                name=name,
                path=path,
            )
            return file_info_from_api_object(api_object=api_response.file_info)
        except ApiException as e:
            raise CustomApiException(e)

    def make_directory(
        self,
        name: str,
        path: str,
        create_parent_directories: bool = False,
    ) -> FileInfo:
        """
        Create a directory (similar to Unix mkdir).

        Args:
            name (str): SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            path (str): The absolute path where the directory should be created.
                Must start with a forward slash (e.g., "/workspace/data").
                The directory will be created with 0755 permissions (rwxr-xr-x).
            create_parent_directories (bool): If True, creates parent directories
                if they don't exist. If False, the operation will fail if parent
                directories don't exist. Defaults to False.

        Returns:
            FileInfo: Metadata about the created directory.
        """
        body = FilesystemServiceMakeDirectoryRequest(
            path=path,
            create_parent_directories=create_parent_directories,
        )

        try:
            api_response = self.service_api.filesystem_service_make_directory(
                name=name,
                body=body,
            )
            return file_info_from_api_object(api_object=api_response.file_info)
        except ApiException as e:
            raise CustomApiException(e)