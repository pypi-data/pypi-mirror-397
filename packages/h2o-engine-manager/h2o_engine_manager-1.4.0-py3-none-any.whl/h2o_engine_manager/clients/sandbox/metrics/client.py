from typing import Any
from typing import Dict
from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox.metrics.metrics import Metrics
from h2o_engine_manager.clients.sandbox.metrics.metrics import metrics_from_api_object
from h2o_engine_manager.gen import ApiException
from h2o_engine_manager.gen import Configuration
from h2o_engine_manager.gen.api.metrics_service_api import MetricsServiceApi


class MetricsClient:
    """MetricsClient reads resource usage metrics from a SandboxEngine."""

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
            self.service_api = MetricsServiceApi(api_client)

    def read_metrics(
        self,
        name: str,
        disk_path: str = "",
        strict_mode: bool = False,
    ) -> Metrics:
        """
        Read current resource usage metrics for a sandbox engine.

        Returns a snapshot of memory, CPU, and disk statistics collected
        at the time of the request.

        Args:
            name (str): The SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            disk_path (str): Optional filesystem path to measure for disk usage.
                Must be an absolute path (e.g., "/", "/workspace").
                If not specified, defaults to the root filesystem ("/").
            strict_mode (bool): If True, returns an error if metrics cannot be collected.
                If False (default), returns partial metrics with zero values
                for unavailable metrics (graceful degradation).

        Returns:
            Metrics: A snapshot of resource usage metrics including memory, CPU,
                and disk statistics.
        """
        try:
            kwargs: Dict[str, Any] = {}
            if disk_path:
                kwargs["disk_path"] = disk_path
            if strict_mode:
                kwargs["strict_mode"] = strict_mode

            api_response = self.service_api.metrics_service_read_metrics(
                name=name,
                **kwargs,
            )
            return metrics_from_api_object(api_object=api_response.metrics)
        except ApiException as e:
            raise CustomApiException(e)