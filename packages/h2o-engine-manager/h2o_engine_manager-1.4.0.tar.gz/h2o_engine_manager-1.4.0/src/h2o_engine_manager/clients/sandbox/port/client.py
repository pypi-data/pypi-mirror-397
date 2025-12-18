import http
import time
from typing import List
from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.exception import TimeoutException
from h2o_engine_manager.clients.sandbox.port.port import Port
from h2o_engine_manager.clients.sandbox.port.port import port_from_api_object
from h2o_engine_manager.clients.sandbox.port.port import port_to_api_object
from h2o_engine_manager.clients.sandbox.port.state import PortState
from h2o_engine_manager.gen import ApiException
from h2o_engine_manager.gen import Configuration
from h2o_engine_manager.gen.api.port_service_api import PortServiceApi
from h2o_engine_manager.gen.model.required_the_port_resource_to_update import (
    RequiredThePortResourceToUpdate,
)


class PortClient:
    """PortClient manages port operations within a SandboxEngine."""

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
            self.service_api = PortServiceApi(api_client)

    def create_port(
        self,
        parent: str,
        port: Port,
        port_id: str,
    ) -> Port:
        """
        Create a new port in the sandbox engine.

        Args:
            parent (str): The parent SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            port (Port): The Port to create.
            port_id (str): The port number to expose (1024-65535).
                This will become the port ID in the resource name.

        Returns:
            Port: The created port.
        """
        api_port = port_to_api_object(port)

        try:
            api_response = self.service_api.port_service_create_port(
                parent=parent,
                port=api_port,
                port_id=port_id,
            )
            return port_from_api_object(api_object=api_response.port)
        except ApiException as e:
            raise CustomApiException(e)

    def get_port(
        self,
        name: str,
    ) -> Port:
        """
        Get a port by its resource name.

        Args:
            name (str): Port resource name.
                Format: "workspaces/*/sandboxEngines/*/ports/*"

        Returns:
            Port: The port.
        """
        try:
            api_response = self.service_api.port_service_get_port(
                name=name,
            )
            return port_from_api_object(api_object=api_response.port)
        except ApiException as e:
            raise CustomApiException(e)

    def list_ports(
        self,
        parent: str,
        page_size: int = 0,
        page_token: str = "",
    ) -> tuple[List[Port], str]:
        """
        List ports in a sandbox engine.

        Args:
            parent (str): The parent SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            page_size (int): Maximum number of ports to return.
                If unspecified (or set to 0), at most 50 ports will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Token for pagination.
                Leave unset to receive the initial page.

        Returns:
            tuple[List[Port], str]: A tuple of (ports, next_page_token).
        """
        try:
            api_response = self.service_api.port_service_list_ports(
                parent=parent,
                page_size=page_size,
                page_token=page_token,
            )
            ports = []
            if api_response.ports:
                ports = [
                    port_from_api_object(api_object=p) for p in api_response.ports
                ]
            next_page_token = (
                api_response.next_page_token if api_response.next_page_token else ""
            )
            return ports, next_page_token
        except ApiException as e:
            raise CustomApiException(e)

    def update_port(
        self,
        port: Port,
        update_mask: List[str],
    ) -> Port:
        """
        Update a port.

        Args:
            port (Port): The Port resource to update.
                The name field must be set to identify which port to update.
            update_mask (List[str]): Field mask specifying which fields to update.
                Updatable fields: display_name, public
                Example: ["display_name", "public"]

        Returns:
            Port: The updated port.
        """
        api_port = RequiredThePortResourceToUpdate(
            display_name=port.display_name,
            public=port.public,
        )

        try:
            api_response = self.service_api.port_service_update_port(
                port_name=port.name,
                port=api_port,
                update_mask=",".join(update_mask),
            )
            return port_from_api_object(api_object=api_response.port)
        except ApiException as e:
            raise CustomApiException(e)

    def delete_port(
        self,
        name: str,
    ) -> None:
        """
        Delete a port.

        Args:
            name (str): Port resource name.
                Format: "workspaces/*/sandboxEngines/*/ports/*"
        """
        try:
            self.service_api.port_service_delete_port(
                name=name,
            )
        except ApiException as e:
            raise CustomApiException(e)

    def wait(
        self,
        name: str,
        timeout_seconds: Optional[float] = None,
    ) -> Optional[Port]:
        """
        Blocks execution until the port reaches a stable state or is no longer found.

        A port is considered stable when it reaches STATE_READY or STATE_FAILED.

        Args:
            name (str): Port resource name.
                Format: "workspaces/*/sandboxEngines/*/ports/*"
            timeout_seconds (float, optional): Time limit in seconds for how long to wait.
                If not specified, waits indefinitely.

        Returns:
            Port: The port that has reached a stable state, or None if port was deleted.

        Raises:
            TimeoutException: If timeout_seconds is specified and the port doesn't
                reach a stable state within the timeout.
        """
        start = time.time()

        while True:
            try:
                port = self.get_port(name=name)

                # Port is considered stable when it's in READY or FAILED state
                if port.state in [
                    PortState.STATE_READY,
                    PortState.STATE_FAILED,
                ]:
                    return port

                if timeout_seconds is not None and time.time() - start > timeout_seconds:
                    raise TimeoutException()

                time.sleep(1)
            except CustomApiException as exc:
                if exc.status == http.HTTPStatus.NOT_FOUND:
                    return None

                raise exc
