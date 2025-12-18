from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.dai_license.dai_license_metadata import (
    DAILicenseMetadata,
)
from h2o_engine_manager.clients.dai_license.dai_license_metadata import from_api_object
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.gen import ApiException
from h2o_engine_manager.gen.api.dai_license_service_api import DAILicenseServiceApi
from h2o_engine_manager.gen.configuration import Configuration
from h2o_engine_manager.gen.model.v1_dai_license_metadata import V1DAILicenseMetadata


class DAILicenseClient:
    """DAILicenseClient retrieves DAI license metadata."""

    def __init__(
        self,
        connection_config: ConnectionConfig,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
    ):
        """Initializes DAILicenseClient.

        Args:
            connection_config (ConnectionConfig): AIEM connection configuration object.
            verify_ssl: Set to False to disable SSL certificate verification.
            ssl_ca_cert: Path to a CA cert bundle with certificates of trusted CAs.
        """
        configuration = Configuration(host=connection_config.aiem_url)
        configuration.verify_ssl = verify_ssl
        configuration.ssl_ca_cert = ssl_ca_cert

        with TokenApiClient(
            configuration, connection_config.token_provider
        ) as api_client:
            self.service_api = DAILicenseServiceApi(api_client)

    def get_dai_license_metadata(self) -> Optional[DAILicenseMetadata]:
        """Gets the configured DAI license metadata.

        Returns:
            DAILicenseMetadata: The DAI license metadata, or None if no license is configured.
        """
        api_metadata: V1DAILicenseMetadata

        try:
            response = self.service_api.d_ai_license_service_get_dai_license_metadata()
            api_metadata = response.dai_license_metadata
        except ApiException as e:
            raise CustomApiException(e)

        if api_metadata is None:
            return None

        return from_api_object(api_metadata)