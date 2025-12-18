import pprint

from h2o_engine_manager.clients.sandbox_engine_template.template import from_api_object
from h2o_engine_manager.gen.model.v1_list_sandbox_engine_templates_response import (
    V1ListSandboxEngineTemplatesResponse,
)


class SandboxEngineTemplatesPage:
    """
    Represents a list of SandboxEngineTemplates together with a next_page_token for listing all SandboxEngineTemplates.
    """

    def __init__(
        self, list_api_response: V1ListSandboxEngineTemplatesResponse
    ) -> None:
        api_objects = list_api_response.sandbox_engine_templates
        self.sandbox_engine_templates = []
        for api_template in api_objects:
            self.sandbox_engine_templates.append(from_api_object(api_template))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)