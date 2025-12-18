from typing import List
from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_template.page import (
    SandboxEngineTemplatesPage,
)
from h2o_engine_manager.clients.sandbox_engine_template.template import (
    SandboxEngineTemplate,
)
from h2o_engine_manager.clients.sandbox_engine_template.template import from_api_object
from h2o_engine_manager.clients.sandbox_engine_template.template_config import (
    SandboxEngineTemplateConfig,
)
from h2o_engine_manager.gen import ApiException
from h2o_engine_manager.gen.api.sandbox_engine_template_service_api import (
    SandboxEngineTemplateServiceApi,
)
from h2o_engine_manager.gen.configuration import Configuration
from h2o_engine_manager.gen.model.v1_list_sandbox_engine_templates_response import (
    V1ListSandboxEngineTemplatesResponse,
)
from h2o_engine_manager.gen.model.v1_sandbox_engine_template import (
    V1SandboxEngineTemplate,
)


class SandboxEngineTemplateClient:
    """SandboxEngineTemplateClient manages SandboxEngineTemplates."""

    def __init__(
        self,
        connection_config: ConnectionConfig,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
    ):
        """Initializes SandboxEngineTemplateClient.

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
            self.service_api = SandboxEngineTemplateServiceApi(api_client)

    def create_sandbox_engine_template(
        self,
        parent: str,
        sandbox_engine_template: SandboxEngineTemplate,
        sandbox_engine_template_id: str,
    ) -> SandboxEngineTemplate:
        """Standard Create method.

        Args:
            parent (str): Name of the template's parent workspace. Format: `workspaces/*`.
            sandbox_engine_template (SandboxEngineTemplate): SandboxEngineTemplate to create.
            sandbox_engine_template_id (str): Specify the SandboxEngineTemplate ID,
                which will become a part of the SandboxEngineTemplate resource name.
                It must:
                    - contain 1-63 characters
                    - contain only lowercase alphanumeric characters or hyphen ('-')
                    - start with an alphabetic character
                    - end with an alphanumeric character

        Returns:
            SandboxEngineTemplate: created SandboxEngineTemplate.
        """
        created_api_object: V1SandboxEngineTemplate
        try:
            created_api_object = self.service_api.sandbox_engine_template_service_create_sandbox_engine_template(
                parent=parent,
                sandbox_engine_template_id=sandbox_engine_template_id,
                sandbox_engine_template=sandbox_engine_template.to_api_object(),
            ).sandbox_engine_template
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(created_api_object)

    def get_sandbox_engine_template(self, name: str) -> SandboxEngineTemplate:
        """Standard Get method.

        Args:
            name: Name of the SandboxEngineTemplate to retrieve. Format: `workspaces/*/sandboxEngineTemplates/*`
        """
        api_object: V1SandboxEngineTemplate

        try:
            api_object = self.service_api.sandbox_engine_template_service_get_sandbox_engine_template(
                name_13=name
            ).sandbox_engine_template
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def list_sandbox_engine_templates(
        self,
        parent: str,
        page_size: int = 0,
        page_token: str = "",
    ) -> SandboxEngineTemplatesPage:
        """Standard list method.

        Args:
            parent (str): Name of the workspace from which to list templates. Format: `workspaces/*`.
            page_size (int): Maximum number of SandboxEngineTemplates to return in a response.
                If unspecified (or set to 0), at most 50 SandboxEngineTemplates will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the SandboxEngineTemplatesPage.

        Returns:
            SandboxEngineTemplatesPage: SandboxEngineTemplatesPage object.
        """
        list_response: V1ListSandboxEngineTemplatesResponse

        try:
            list_response = (
                self.service_api.sandbox_engine_template_service_list_sandbox_engine_templates(
                    parent=parent,
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return SandboxEngineTemplatesPage(list_response)

    def list_all_sandbox_engine_templates(
        self, parent: str
    ) -> List[SandboxEngineTemplate]:
        """Help method for listing all SandboxEngineTemplates.

        Args:
            parent (str): Name of the workspace from which to list templates. Format: `workspaces/*`.
        """

        all_templates: List[SandboxEngineTemplate] = []
        next_page_token = ""
        while True:
            templates_page = self.list_sandbox_engine_templates(
                parent=parent,
                page_size=1000,
                page_token=next_page_token,
            )
            all_templates = all_templates + templates_page.sandbox_engine_templates
            next_page_token = templates_page.next_page_token
            if next_page_token == "":
                break

        return all_templates

    def update_sandbox_engine_template(
        self,
        sandbox_engine_template: SandboxEngineTemplate,
        update_mask: str = "*",
    ) -> SandboxEngineTemplate:
        """Standard Update method.

        Args:
            sandbox_engine_template (SandboxEngineTemplate): template to update.
            update_mask (str): The field mask to use for the update.
                Allowed field paths are:
                    - display_name
                    - milli_cpu_request
                    - milli_cpu_limit
                    - gpu_resource
                    - gpu
                    - memory_bytes_request
                    - memory_bytes_limit
                    - storage_bytes
                    - environmental_variables
                    - yaml_pod_template_spec
                    - enabled
                    - max_idle_duration
                Default value "*" will update all updatable fields.

        Returns:
            SandboxEngineTemplate: Updated SandboxEngineTemplate.
        """
        updated_api_object: V1SandboxEngineTemplate

        try:
            updated_api_object = (
                self.service_api.sandbox_engine_template_service_update_sandbox_engine_template(
                    sandbox_engine_template_name=sandbox_engine_template.name,
                    update_mask=update_mask,
                    sandbox_engine_template=sandbox_engine_template.to_resource(),
                ).sandbox_engine_template
            )
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=updated_api_object)

    def delete_sandbox_engine_template(self, name: str) -> None:
        """Standard Delete method.

        Args:
            name (str): Name of the SandboxEngineTemplate to delete. Format is `workspaces/*/sandboxEngineTemplates/*`
        """
        try:
            self.service_api.sandbox_engine_template_service_delete_sandbox_engine_template(
                name_12=name
            )
        except ApiException as e:
            raise CustomApiException(e)

    def delete_all_sandbox_engine_templates(self, parent: str) -> None:
        """Help method for deleting all SandboxEngineTemplates in a specified parent workspace.

        Args:
            parent (str): Parent workspace name. Format is `workspaces/*`.
        """
        templates = self.list_all_sandbox_engine_templates(parent=parent)
        for template in templates:
            self.delete_sandbox_engine_template(name=template.name)

    def apply_sandbox_engine_template_configs(
        self,
        configs: List[SandboxEngineTemplateConfig],
        parent: str = "workspaces/global",
    ) -> List[SandboxEngineTemplate]:
        """
        Set all SandboxEngineTemplates to a state defined in the configs in the specified parent workspace.
        SandboxEngineTemplates that are not specified in the configs will be deleted in the specified parent workspace.
        SandboxEngineTemplates that are specified in the configs will be recreated with the new values
            in the specified parent workspace.

        Args:
            configs: SandboxEngineTemplate configurations that should be applied.
            parent: Workspace name in which to apply configs. Format is `workspaces/*`.

        Returns: applied SandboxEngineTemplates

        """
        self.delete_all_sandbox_engine_templates(parent=parent)

        for cfg in configs:
            self.create_sandbox_engine_template(
                parent=parent,
                sandbox_engine_template=cfg.to_sandbox_engine_template(),
                sandbox_engine_template_id=cfg.sandbox_engine_template_id,
            )

        return self.list_all_sandbox_engine_templates(parent=parent)