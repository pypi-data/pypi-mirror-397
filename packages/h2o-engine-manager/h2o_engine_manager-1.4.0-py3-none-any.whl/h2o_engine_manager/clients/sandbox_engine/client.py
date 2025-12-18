import http
import time
from typing import List
from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.exception import TimeoutException
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.engine import (
    sandbox_engine_from_api_object,
)
from h2o_engine_manager.clients.sandbox_engine.engine import (
    sandbox_engine_to_api_object,
)
from h2o_engine_manager.clients.sandbox_engine.page import SandboxEnginesPage
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState
from h2o_engine_manager.gen import ApiException
from h2o_engine_manager.gen import Configuration
from h2o_engine_manager.gen.api.sandbox_engine_service_api import (
    SandboxEngineServiceApi,
)
from h2o_engine_manager.gen.model.v1_list_sandbox_engines_response import (
    V1ListSandboxEnginesResponse,
)
from h2o_engine_manager.gen.model.v1_sandbox_engine import V1SandboxEngine


class SandboxEngineClient:
    """SandboxEngineClient manages SandboxEngines."""

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
            self.service_api = SandboxEngineServiceApi(api_client)

    def create_sandbox_engine(
        self,
        parent: str,
        sandbox_engine: SandboxEngine,
        sandbox_engine_id: str,
    ) -> SandboxEngine:
        """
        Create sandbox engine.

        Args:
            parent (str): Name of the engine's parent workspace. Format: "workspaces/*".
            sandbox_engine (SandboxEngine): SandboxEngine to create.
            sandbox_engine_id (str): The ID to use for the SandboxEngine, which will form
                the engine's resource name.
                This value must:
                - contain 1-63 characters
                - contain only lowercase alphanumeric characters or hyphen ('-')
                - start with an alphabetic character
                - end with an alphanumeric character
        Returns:
            SandboxEngine: created SandboxEngine.
        """
        created_api_object: V1SandboxEngine
        try:
            created_api_object = self.service_api.sandbox_engine_service_create_sandbox_engine(
                parent=parent,
                sandbox_engine=sandbox_engine_to_api_object(sandbox_engine=sandbox_engine),
                sandbox_engine_id=sandbox_engine_id,
            ).sandbox_engine
        except ApiException as e:
            raise CustomApiException(e)

        return sandbox_engine_from_api_object(api_object=created_api_object)

    def get_sandbox_engine(
        self,
        name: str,
    ) -> SandboxEngine:
        """
        Get sandbox engine.

        Args:
            name: SandboxEngine resource name. Format: "workspaces/*/sandboxEngines/*"
        Returns:
            SandboxEngine: sandbox engine
        """

        api_object: V1SandboxEngine

        try:
            api_object = self.service_api.sandbox_engine_service_get_sandbox_engine(name_12=name).sandbox_engine
        except ApiException as e:
            raise CustomApiException(e)

        return sandbox_engine_from_api_object(api_object=api_object)

    def list_sandbox_engines(
        self,
        parent: str,
        page_size: int = 0,
        page_token: str = "",
    ) -> SandboxEnginesPage:
        """Standard list method.

        Args:
            parent (str): Name of the workspace from which to list sandboxEngines. Format: `workspaces/*`.
            page_size (int): Maximum number of SandboxEngines to return in a response.
                If unspecified (or set to 0), at most 50 SandboxEngines will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the SandboxEnginesPage.

        Returns:
            SandboxEnginesPage: SandboxEnginesPage object.
        """
        list_response: V1ListSandboxEnginesResponse

        try:
            list_response = (
                self.service_api.sandbox_engine_service_list_sandbox_engines(
                    parent=parent,
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return SandboxEnginesPage(list_api_response=list_response)

    def list_all_sandbox_engines(self, parent: str) -> List[SandboxEngine]:
        """Help method for listing all SandboxEngines.

        Args:
            parent (str): Name of the workspace from which to list sandboxEngines. Format: `workspaces/*`.
        """

        all_sandbox_engines: List[SandboxEngine] = []
        next_page_token = ""
        while True:
            page = self.list_sandbox_engines(
                parent=parent,
                page_size=1000,
                page_token=next_page_token,
            )
            all_sandbox_engines = all_sandbox_engines + page.sandbox_engines
            next_page_token = page.next_page_token
            if next_page_token == "":
                break

        return all_sandbox_engines

    def terminate_sandbox_engine(
        self,
        name: str,
    ) -> SandboxEngine:
        """
        Terminate sandbox engine.
        Method returns instantly, but it may take some time until the engine is terminated.

        Args:
            name: SandboxEngine resource name. Format: "workspaces/*/sandboxEngines/*"
        Returns: terminated sandboxEngine
        """
        api_engine: V1SandboxEngine

        try:
            api_engine = self.service_api.sandbox_engine_service_terminate_sandbox_engine(
                name_1=name,
                body=None,
            ).sandbox_engine
        except ApiException as e:
            raise CustomApiException(e)

        return sandbox_engine_from_api_object(api_object=api_engine)

    def delete_sandbox_engine(
        self,
        name: str,
    ) -> None:
        """
        Start sandbox engine deletion.
        Method returns instantly, but it may take some time until the engine is deleted.

        Args:
            name: SandboxEngine resource name. Format: "workspaces/*/sandboxEngines/*"
        """
        try:
            self.service_api.sandbox_engine_service_delete_sandbox_engine(name_11=name)
        except ApiException as e:
            raise CustomApiException(e)

    def wait(self, name: str, timeout_seconds: Optional[float] = None) -> Optional[SandboxEngine]:
        """
        Blocks execution until the sandboxEngine with the given name reaches a stable state
        or until it is no longer found.

        Args:
            name: SandboxEngine resource name for which to wait. Format: "workspaces/*/sandboxEngines/*"
            timeout_seconds: Time limit in seconds for how long to wait.
        Returns: engine that has finished waiting or nothing, if engine is no longer found.
        """
        start = time.time()

        while True:
            try:
                engine = self.get_sandbox_engine(name=name)

                # SandboxEngine is considered stable when it's in RUNNING, TERMINATED, or FAILED state
                if engine.state in [
                    SandboxEngineState.STATE_RUNNING,
                    SandboxEngineState.STATE_TERMINATED,
                    SandboxEngineState.STATE_FAILED,
                ]:
                    return engine

                if timeout_seconds is not None and time.time() - start > timeout_seconds:
                    raise TimeoutException()

                time.sleep(5)
            except CustomApiException as exc:
                if exc.status == http.HTTPStatus.NOT_FOUND:
                    return None

                raise exc