from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox.h2o_secure_store.reveal_secret_to_file_response import (
    RevealSecretToFileResponse,
)
from h2o_engine_manager.clients.sandbox.h2o_secure_store.reveal_secret_to_file_response import (
    reveal_secret_to_file_response_from_api_object,
)
from h2o_engine_manager.gen import ApiException
from h2o_engine_manager.gen import Configuration
from h2o_engine_manager.gen.api.h2_o_secure_store_service_api import (
    H2OSecureStoreServiceApi,
)
from h2o_engine_manager.gen.model.h2_o_secure_store_service_reveal_secret_to_file_request import (
    H2OSecureStoreServiceRevealSecretToFileRequest,
)


class H2OSecureStoreClient:
    """H2OSecureStoreClient manages H2O Secure Store operations within a SandboxEngine."""

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
            self.service_api = H2OSecureStoreServiceApi(api_client)

    def reveal_secret_to_file(
        self,
        name: str,
        secret_version: str,
        path: str,
    ) -> RevealSecretToFileResponse:
        """
        Reveal a secret value from H2O Secure Store and write it to a file.

        Retrieves a secret version from the secure store and writes its value to
        the specified path in the sandbox filesystem. The caller must be authorized
        to reveal the specified secret version.

        Files are created with secure 0600 permissions (owner read/write only)
        to protect sensitive data.

        Args:
            name (str): SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            secret_version (str): The resource name of the SecretVersion to reveal.
                Format: "workspaces/*/secrets/*/versions/*"
                The version segment can be a specific version ID or "latest" to
                retrieve the most recently created SecretVersion.
                Example: "workspaces/my-workspace/secrets/api-key/versions/latest"
            path (str): The absolute path in the sandbox filesystem where the secret
                value should be written.
                Must start with a forward slash (e.g., "/home/sandbox/.credentials/token").
                If the file exists, it will be overwritten.
                Parent directories will be created automatically if they don't exist.

        Returns:
            RevealSecretToFileResponse: Response containing the actual secret version
                name (resolved if "latest" was used) and metadata about the written file.
        """
        body = H2OSecureStoreServiceRevealSecretToFileRequest(
            secret_version=secret_version,
            path=path,
        )

        try:
            api_response = (
                self.service_api.h2_o_secure_store_service_reveal_secret_to_file(
                    name=name,
                    body=body,
                )
            )
            return reveal_secret_to_file_response_from_api_object(
                api_object=api_response
            )
        except ApiException as e:
            raise CustomApiException(e)
