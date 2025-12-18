import pprint

from h2o_engine_manager.gen.model.v1_secret_environment_variable import (
    V1SecretEnvironmentVariable,
)


class SecretEnvironmentVariable:
    """
    SecretEnvironmentVariable contains configuration for environment variables
    populated from H2O Secure Store secrets.
    """

    def __init__(
        self,
        secret_version: str = "",
    ):
        """
        SecretEnvironmentVariable references a secret version in H2O Secure Store.

        Args:
            secret_version: The resource name of the secret version to use.
                Format: "workspaces/*/secrets/*/versions/*"
                Example: "workspaces/my-workspace/secrets/api-key/versions/latest"
        """
        self.secret_version = secret_version

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def secret_environment_variable_from_api_object(
    api_object: V1SecretEnvironmentVariable,
) -> SecretEnvironmentVariable:
    return SecretEnvironmentVariable(
        secret_version=api_object.secret_version if api_object.secret_version else "",
    )