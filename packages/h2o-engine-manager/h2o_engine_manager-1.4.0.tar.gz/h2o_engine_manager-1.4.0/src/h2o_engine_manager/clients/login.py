import ssl
from dataclasses import dataclass
from typing import Optional
from typing import Union
from urllib.parse import urljoin

import requests
from h2o_authn import TokenProvider

from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.connection_config import discover_platform_connection
from h2o_engine_manager.clients.connection_config import get_connection
from h2o_engine_manager.clients.dai_engine.dai_engine_client import DAIEngineClient
from h2o_engine_manager.clients.dai_engine_profile.client import DAIEngineProfileClient
from h2o_engine_manager.clients.dai_engine_version.client import DAIEngineVersionClient
from h2o_engine_manager.clients.dai_license.client import DAILicenseClient
from h2o_engine_manager.clients.h2o_engine.client import H2OEngineClient
from h2o_engine_manager.clients.h2o_engine_profile.client import H2OEngineProfileClient
from h2o_engine_manager.clients.h2o_engine_version.client import H2OEngineVersionClient
from h2o_engine_manager.clients.notebook_engine.client import NotebookEngineClient
from h2o_engine_manager.clients.notebook_engine_image.client import (
    NotebookEngineImageClient,
)
from h2o_engine_manager.clients.notebook_engine_profile.client import (
    NotebookEngineProfileClient,
)
from h2o_engine_manager.clients.sandbox.filesystem.client import FilesystemClient
from h2o_engine_manager.clients.sandbox.h2o_drive.client import H2ODriveClient
from h2o_engine_manager.clients.sandbox.h2o_secure_store.client import (
    H2OSecureStoreClient,
)
from h2o_engine_manager.clients.sandbox.metrics.client import MetricsClient
from h2o_engine_manager.clients.sandbox.port.client import PortClient
from h2o_engine_manager.clients.sandbox.process.client import ProcessClient
from h2o_engine_manager.clients.sandbox_engine.client import SandboxEngineClient
from h2o_engine_manager.clients.sandbox_engine_image.client import (
    SandboxEngineImageClient,
)
from h2o_engine_manager.clients.sandbox_engine_template.client import (
    SandboxEngineTemplateClient,
)


@dataclass
class SandboxClients:
    filesystem_client: FilesystemClient
    h2o_drive_client: H2ODriveClient
    h2o_secure_store_client: H2OSecureStoreClient
    metrics_client: MetricsClient
    port_client: PortClient
    process_client: ProcessClient

class Clients:
    def __init__(
        self,
        dai_engine_client: DAIEngineClient,
        h2o_engine_client: H2OEngineClient,
        dai_engine_profile_client: DAIEngineProfileClient,
        h2o_engine_profile_client: H2OEngineProfileClient,
        notebook_engine_profile_client: NotebookEngineProfileClient,
        dai_engine_version_client: DAIEngineVersionClient,
        h2o_engine_version_client: H2OEngineVersionClient,
        notebook_engine_image_client: NotebookEngineImageClient,
        sandbox_engine_image_client: SandboxEngineImageClient,
        sandbox_engine_template_client: SandboxEngineTemplateClient,
        sandbox_engine_client: SandboxEngineClient,
        notebook_engine_client: NotebookEngineClient,
        dai_license_client: DAILicenseClient,
        sandbox_clients: SandboxClients
    ) -> None:
        self.dai_engine_client = dai_engine_client
        self.h2o_engine_client = h2o_engine_client
        self.dai_engine_profile_client = dai_engine_profile_client
        self.h2o_engine_profile_client = h2o_engine_profile_client
        self.notebook_engine_profile_client = notebook_engine_profile_client
        self.dai_engine_version_client = dai_engine_version_client
        self.h2o_engine_version_client = h2o_engine_version_client
        self.notebook_engine_image_client = notebook_engine_image_client
        self.sandbox_engine_image_client = sandbox_engine_image_client
        self.sandbox_engine_template_client = sandbox_engine_template_client
        self.sandbox_engine_client = sandbox_engine_client
        self.notebook_engine_client = notebook_engine_client
        self.dai_license_client = dai_license_client
        self.sandbox_clients = sandbox_clients


def login(
    environment: Optional[str] = None,
    token_provider: Optional[TokenProvider] = None,
    platform_token: Optional[str] = None,
    default_workspace_id: str = "default",
    config_path: Optional[str] = None,
    verify_ssl: bool = True,
    ssl_ca_cert: Optional[str] = None,
) -> Clients:
    """Initializes AI Engine Manager clients for H2O AI Cloud.

    All arguments are optional. Configuration-less login is dependent on having the H2O CLI configured.
    See: https://docs.h2o.ai/h2o-ai-cloud/developerguide/cli#platform-token
    The Discovery Service is used to discover the Engine Manager service endpoint.
    See: https://pypi.org/project/h2o-cloud-discovery/

    Args:
        environment (str, optional): The H2O Cloud environment URL to use (e.g. https://cloud.h2o.ai).
            If left empty, the environment will be read from the H2O CLI configuration or environmental variables.
            Then, h2o-cloud-discovery will be used to discover the Engine Manager service endpoint.
        token_provider (TokenProvider, optional) = Token provider. Takes priority over platform_token argument.
        platform_token (str, optional): H2O Platform Token.
            If neither 'token_provider' nor 'platform_token' is provided the platform token will be read
            from the H2O CLI configuration.
        default_workspace_id (str, optional): The default workspace ID which will client use to manipulate with
            resources. Defaults to `default`.
        config_path: (str, optional): Path to the H2O AI Cloud configuration file.
            Defaults to '~/.h2oai/h2o-cli-config.toml'.
        verify_ssl: Set to False to disable SSL certificate verification.
        ssl_ca_cert: Path to a CA cert bundle with certificates of trusted CAs.

    Raises:
        FileNotFoundError: When the H2O CLI configuration file is needed but cannot be found.
        TomlDecodeError: When the H2O CLI configuration file is needed but cannot be processed.
        LookupError: When the service endpoint cannot be discovered.
        ConnectionError: When a communication with server failed.
    """
    ssl_context = ssl.create_default_context(cafile=ssl_ca_cert)  # Will use system store if None
    if not verify_ssl:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    cfg = discover_platform_connection(
        environment_url=environment,
        platform_token=platform_token,
        token_provider=token_provider,
        config_path=config_path,
        ssl_context=ssl_context,
    )

    return __init_clients(
        cfg=cfg, default_workspace_id=default_workspace_id, verify_ssl=verify_ssl, ssl_ca_cert=ssl_ca_cert,
    )


def login_custom(
    endpoint: str,
    refresh_token: str,
    issuer_url: str,
    client_id: str,
    client_secret: Optional[str] = None,
    default_workspace_id: str = "default",
    verify_ssl: bool = True,
    ssl_ca_cert: Optional[str] = None,
) -> Clients:
    """Initializes AI Engine Manager clients.

    Args:
        endpoint (str): The Engine Manager service endpoint URL (e.g. https://enginemanager.cloud.h2o.ai).
        refresh_token (str): The OIDC refresh token.
        issuer_url (str): The OIDC issuer URL.
        client_id (str): The OIDC Client ID that issued the 'refresh_token'.
        client_secret (str, optional): Optional OIDC Client Secret that issued the 'refresh_token'. Defaults to None.
        default_workspace_id (str, optional): The default workspace ID which will client use to manipulate with
            resources. Defaults to `default`.
        verify_ssl: Set to False to disable SSL certificate verification.
        ssl_ca_cert: Path to a CA cert bundle with certificates of trusted CAs.
    """
    # Remove trailing slash from the URL for the generated clients
    endpoint = endpoint.rstrip("/")
    cfg = get_connection(
        aiem_url=endpoint,
        refresh_token=refresh_token,
        issuer_url=issuer_url,
        client_id=client_id,
        client_secret=client_secret,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )

    return __init_clients(
        cfg=cfg, default_workspace_id=default_workspace_id, verify_ssl=verify_ssl, ssl_ca_cert=ssl_ca_cert,
    )


def __init_clients(
    cfg: ConnectionConfig,
    default_workspace_id: str,
    verify_ssl: bool,
    ssl_ca_cert: Optional[str],
):
    # Verify that the server is reachable
    version_url = urljoin(cfg.aiem_url, "version")

    verify_param: Union[bool, str]
    if verify_ssl:
        verify_param = True
        if ssl_ca_cert:
            verify_param = ssl_ca_cert
    else:
        verify_param = False

    resp = requests.get(version_url, verify=verify_param)
    if not (200 <= resp.status_code <= 299):
        raise ConnectionError(
            f"Server is not reachable. Status code: {resp.status_code}, Response body: {resp.text}"
        )

    dai_engine_client = DAIEngineClient(
        connection_config=cfg, default_workspace_id=default_workspace_id, verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    h2o_engine_client = H2OEngineClient(
        connection_config=cfg, default_workspace_id=default_workspace_id, verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    dai_engine_profile_client = DAIEngineProfileClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    h2o_engine_profile_client = H2OEngineProfileClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    notebook_engine_profile_client = NotebookEngineProfileClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    dai_engine_version_client = DAIEngineVersionClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    h2o_engine_version_client = H2OEngineVersionClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    notebook_engine_image_client = NotebookEngineImageClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    sandbox_engine_image_client = SandboxEngineImageClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    sandbox_engine_template_client = SandboxEngineTemplateClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    sandbox_engine_client = SandboxEngineClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    notebook_engine_client = NotebookEngineClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    dai_license_client = DAILicenseClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    sandbox_engine_filesystem_client = FilesystemClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    sandbox_engine_process_client = ProcessClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    sandbox_engine_port_client = PortClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    sandbox_engine_h2o_drive_client = H2ODriveClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    sandbox_engine_h2o_secure_store_client = H2OSecureStoreClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )
    sandbox_engine_metrics_client = MetricsClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )

    return Clients(
        dai_engine_client=dai_engine_client,
        h2o_engine_client=h2o_engine_client,
        dai_engine_profile_client=dai_engine_profile_client,
        h2o_engine_profile_client=h2o_engine_profile_client,
        notebook_engine_profile_client=notebook_engine_profile_client,
        dai_engine_version_client=dai_engine_version_client,
        h2o_engine_version_client=h2o_engine_version_client,
        notebook_engine_image_client=notebook_engine_image_client,
        sandbox_engine_image_client=sandbox_engine_image_client,
        sandbox_engine_template_client=sandbox_engine_template_client,
        sandbox_engine_client=sandbox_engine_client,
        notebook_engine_client=notebook_engine_client,
        dai_license_client=dai_license_client,
        sandbox_clients=SandboxClients(
            filesystem_client=sandbox_engine_filesystem_client,
            h2o_drive_client=sandbox_engine_h2o_drive_client,
            h2o_secure_store_client=sandbox_engine_h2o_secure_store_client,
            metrics_client=sandbox_engine_metrics_client,
            port_client=sandbox_engine_port_client,
            process_client=sandbox_engine_process_client,
        )
    )
