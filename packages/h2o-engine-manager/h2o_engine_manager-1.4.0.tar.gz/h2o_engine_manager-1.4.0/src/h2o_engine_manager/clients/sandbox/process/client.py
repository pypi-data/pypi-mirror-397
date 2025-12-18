import base64
import time
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox.process.process_state import ProcessState
from h2o_engine_manager.clients.sandbox.process.ps import Process
from h2o_engine_manager.clients.sandbox.process.ps import process_from_api_object
from h2o_engine_manager.clients.sandbox.process.ps import process_to_api_object
from h2o_engine_manager.clients.sandbox.process.secret_environment_variable import (
    SecretEnvironmentVariable,
)
from h2o_engine_manager.gen import ApiException
from h2o_engine_manager.gen import Configuration
from h2o_engine_manager.gen.api.process_service_api import ProcessServiceApi
from h2o_engine_manager.gen.model.process_service_send_signal_request import (
    ProcessServiceSendSignalRequest,
)


class ProcessClient:
    """ProcessClient manages process operations within a SandboxEngine."""

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
            self.service_api = ProcessServiceApi(api_client)

    def create_process(
        self,
        parent: str,
        process: Process,
        process_id: str = "",
        auto_run: bool = False,
    ) -> Process:
        """
        Create a new process in the sandbox engine.

        Args:
            parent (str): The parent SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            process (Process): The Process to create.
            process_id (str): Optional ID for the process.
                Must be 1-63 characters, lowercase alphanumeric or hyphen,
                start and end with alphanumeric. If not provided, a UUID is generated.
            auto_run (bool): If True, starts execution immediately.
                If False, the process is created in STATE_PENDING and requires
                a separate start_process() call.

        Returns:
            Process: The created process.
        """
        api_process = process_to_api_object(process)

        try:
            api_response = self.service_api.process_service_create_process(
                parent=parent,
                process=api_process,
                process_id=process_id,
                auto_run=auto_run,
            )
            return process_from_api_object(api_object=api_response.process)
        except ApiException as e:
            raise CustomApiException(e)

    def start_process(
        self,
        name: str,
    ) -> Process:
        """
        Start a process that is in STATE_PENDING.

        Args:
            name (str): Process resource name.
                Format: "workspaces/*/sandboxEngines/*/processes/*"

        Returns:
            Process: The started process.
        """
        try:
            api_response = self.service_api.process_service_start_process(
                name=name,
                body={},
            )
            return process_from_api_object(api_object=api_response.process)
        except ApiException as e:
            raise CustomApiException(e)

    def get_process(
        self,
        name: str,
    ) -> Process:
        """
        Get a process by its resource name.

        Args:
            name (str): Process resource name.
                Format: "workspaces/*/sandboxEngines/*/processes/*"

        Returns:
            Process: The process.
        """
        try:
            api_response = self.service_api.process_service_get_process(
                name_1=name,
            )
            return process_from_api_object(api_object=api_response.process)
        except ApiException as e:
            raise CustomApiException(e)

    def list_processes(
        self,
        parent: str,
        page_size: int = 0,
        page_token: str = "",
        filter: str = "",
    ) -> tuple[List[Process], str]:
        """
        List processes in a sandbox engine.

        Args:
            parent (str): The parent SandboxEngine resource name.
                Format: "workspaces/*/sandboxEngines/*"
            page_size (int): Maximum number of processes to return.
                If unspecified (or set to 0), the server default will be used.
            page_token (str): Token for pagination.
                Leave unset to receive the initial page.
            filter (str): Filter expression.

        Returns:
            tuple[List[Process], str]: A tuple of (processes, next_page_token).
        """
        try:
            api_response = self.service_api.process_service_list_processes(
                parent=parent,
                page_size=page_size,
                page_token=page_token,
                filter=filter,
            )
            processes = []
            if api_response.processes:
                processes = [
                    process_from_api_object(api_object=p)
                    for p in api_response.processes
                ]
            next_page_token = (
                api_response.next_page_token if api_response.next_page_token else ""
            )
            return processes, next_page_token
        except ApiException as e:
            raise CustomApiException(e)

    def send_signal(
        self,
        name: str,
        signal: int,
    ) -> Process:
        """
        Send a signal to a running process.

        Args:
            name (str): Process resource name.
                Format: "workspaces/*/sandboxEngines/*/processes/*"
            signal (int): The signal number to send (e.g., 9 for SIGKILL, 15 for SIGTERM).

        Returns:
            Process: The process after sending the signal.
        """
        body = ProcessServiceSendSignalRequest(
            signal=signal,
        )

        try:
            api_response = self.service_api.process_service_send_signal(
                name=name,
                body=body,
            )
            return process_from_api_object(api_object=api_response.process)
        except ApiException as e:
            raise CustomApiException(e)

    def wait_process(
        self,
        name: str,
    ) -> Process:
        """
        Wait for a process to complete (blocking call).

        This method blocks until the process reaches a terminal state
        (STATE_SUCCEEDED or STATE_FAILED).

        Args:
            name (str): Process resource name.
                Format: "workspaces/*/sandboxEngines/*/processes/*"

        Returns:
            Process: The completed process.
        """
        try:
            api_response = self.service_api.process_service_wait_process(
                name=name,
                body={},
            )
            return process_from_api_object(api_object=api_response.process)
        except ApiException as e:
            raise CustomApiException(e)

    def wait_process_by_polling(
        self,
        name: str,
        timeout_seconds: Optional[int] = 300,
        poll_interval_seconds: int = 1,
    ) -> Process:
        """
        Wait for a process to reach a final state by polling (client-side blocking).

        This method repeatedly calls get_process until the process reaches
        a final state (STATE_SUCCEEDED or STATE_FAILED) or the timeout is reached.

        Args:
            name (str): Process resource name.
                Format: "workspaces/*/sandboxEngines/*/processes/*"
            timeout_seconds (Optional[int]): Maximum time to wait in seconds (default: 300).
                If None, waits indefinitely.
            poll_interval_seconds (int): Time to wait between polling attempts in seconds (default: 1).

        Returns:
            Process: The process in its final state.

        Raises:
            TimeoutError: If the process does not reach a final state within the timeout.
        """
        start_time = time.time()
        final_states = {ProcessState.STATE_SUCCEEDED, ProcessState.STATE_FAILED}

        while True:
            process = self.get_process(name=name)

            if process.state in final_states:
                return process

            if timeout_seconds is not None:
                elapsed_time = time.time() - start_time
                if elapsed_time >= timeout_seconds:
                    raise TimeoutError(
                        f"Process {name} did not reach final state within {timeout_seconds} seconds. "
                        f"Current state: {process.state.value}"
                    )

            time.sleep(poll_interval_seconds)

    def read_output(
        self,
        name: str,
        output_stream: str = "OUTPUT_STREAM_COMBINED",
    ) -> bytes:
        """
        Read the complete output from a process.

        Args:
            name (str): Process resource name.
                Format: "workspaces/*/sandboxEngines/*/processes/*"
            output_stream (str): Which output stream to read.
                Options:
                - "OUTPUT_STREAM_STDOUT": Read only stdout
                - "OUTPUT_STREAM_STDERR": Read only stderr
                - "OUTPUT_STREAM_COMBINED": Read combined stdout and stderr (default)

        Returns:
            bytes: The output data as bytes.
        """
        try:
            api_response = self.service_api.process_service_read_output(
                name=name,
                output_stream=output_stream,
            )
            # OpenAPI generator returns bytes fields as base64-encoded strings
            # Decode the base64 string to get the raw bytes
            if api_response.data:
                return base64.b64decode(api_response.data)
            return b""
        except ApiException as e:
            raise CustomApiException(e)

    def stream_output(
        self,
        name: str,
        skip_replay: bool = False,
    ) -> Iterator[bytes]:
        """
        Stream output from a process as it becomes available.

        This returns an iterator that yields output chunks as they are produced.

        Args:
            name (str): Process resource name.
                Format: "workspaces/*/sandboxEngines/*/processes/*"
            skip_replay (bool): If True, skips replaying existing output and only
                streams new output. If False, replays all existing output first.

        Yields:
            bytes: Output chunks as they become available.
        """
        try:
            # Note: stream_output returns a streaming response
            response = self.service_api.process_service_stream_output(
                name=name,
                skip_replay=skip_replay,
                _preload_content=False,
            )

            # Iterate over the streaming response
            for chunk in response.stream():
                if chunk:
                    # Each chunk is a StreamResultOfV1StreamOutputResponse
                    # Extract the output data from the result
                    if hasattr(chunk, 'result') and hasattr(chunk.result, 'output'):
                        if chunk.result.output:
                            yield chunk.result.output

        except ApiException as e:
            raise CustomApiException(e)