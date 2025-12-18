import pprint
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

from h2o_engine_manager.clients.sandbox.process.process_state import ProcessState
from h2o_engine_manager.clients.sandbox.process.process_state import (
    process_state_from_api_object,
)
from h2o_engine_manager.clients.sandbox.process.secret_environment_variable import (
    SecretEnvironmentVariable,
)
from h2o_engine_manager.clients.sandbox.process.secret_environment_variable import (
    secret_environment_variable_from_api_object,
)
from h2o_engine_manager.gen.model.v1_process import V1Process
from h2o_engine_manager.gen.model.v1_secret_environment_variable import (
    V1SecretEnvironmentVariable,
)


class Process:
    """
    Process represents a process running in a sandbox engine.
    """

    def __init__(
        self,
        name: str = "",
        command: str = "",
        args: Optional[List[str]] = None,
        working_directory: str = "",
        environment_variables: Optional[Dict[str, str]] = None,
        secret_environment_variables: Optional[
            Dict[str, SecretEnvironmentVariable]
        ] = None,
        state: ProcessState = ProcessState.STATE_UNSPECIFIED,
        exit_code: Optional[int] = None,
        create_time: Optional[datetime] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ):
        """
        Process represents a process in a sandbox engine.

        Args:
            name: The resource name of the process.
                Format: "workspaces/*/sandboxEngines/*/processes/*"
            command: The command that will be executed.
            args: Optional arguments for the command.
            working_directory: Optional working directory for the process.
            environment_variables: Optional map of environment variables.
            secret_environment_variables: Optional map of environment variables
                populated from H2O Secure Store secrets.
            state: The state of the process.
            exit_code: Output only. The exit code of the process.
            create_time: Output only. The time the process was created.
            start_time: Output only. The time the process started execution.
            end_time: Output only. The time the process finished.
        """
        self.name = name
        self.command = command
        self.args = args if args is not None else []
        self.working_directory = working_directory
        self.environment_variables = (
            environment_variables if environment_variables is not None else {}
        )
        self.secret_environment_variables = (
            secret_environment_variables
            if secret_environment_variables is not None
            else {}
        )
        self.state = state
        self.exit_code = exit_code
        self.create_time = create_time
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def process_from_api_object(api_object: V1Process) -> Process:
    secret_env_vars = {}
    if api_object.secret_environment_variables:
        for key, value in api_object.secret_environment_variables.items():
            secret_env_vars[key] = secret_environment_variable_from_api_object(value)

    return Process(
        name=api_object.name if api_object.name else "",
        command=api_object.command if api_object.command else "",
        args=list(api_object.args) if api_object.args else [],
        working_directory=(
            api_object.working_directory if api_object.working_directory else ""
        ),
        environment_variables=(
            dict(api_object.environment_variables)
            if api_object.environment_variables
            else {}
        ),
        secret_environment_variables=secret_env_vars,
        state=(
            process_state_from_api_object(api_object.state)
            if api_object.state
            else ProcessState.STATE_UNSPECIFIED
        ),
        exit_code=int(api_object.exit_code) if api_object.exit_code is not None else None,
        create_time=api_object.create_time,
        start_time=api_object.start_time,
        end_time=api_object.end_time,
    )


def process_to_api_object(process: Process) -> V1Process:
    """
    Convert Process to V1Process API object.

    Args:
        process: The Process object to convert.

    Returns:
        V1Process: The API object ready to be sent to the server.
    """
    # Build secret environment variables for API
    api_secret_env_vars = {}
    if process.secret_environment_variables:
        for key, value in process.secret_environment_variables.items():
            api_secret_env_vars[key] = V1SecretEnvironmentVariable(
                secret_version=value.secret_version
            )

    return V1Process(
        command=process.command,
        args=process.args,
        working_directory=process.working_directory,
        environment_variables=process.environment_variables,
        secret_environment_variables=api_secret_env_vars,
    )