from typing import List

from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.engine import (
    sandbox_engine_from_api_object,
)
from h2o_engine_manager.gen.model.v1_list_sandbox_engines_response import (
    V1ListSandboxEnginesResponse,
)


class SandboxEnginesPage:
    """SandboxEnginesPage represents a page of SandboxEngines."""

    def __init__(self, list_api_response: V1ListSandboxEnginesResponse):
        """
        Initializes SandboxEnginesPage.

        Args:
            list_api_response (V1ListSandboxEnginesResponse): list API response object.
        """
        self.sandbox_engines: List[SandboxEngine] = [
            sandbox_engine_from_api_object(api_object=api_object)
            for api_object in list_api_response.sandbox_engines
        ]
        self.next_page_token: str = list_api_response.next_page_token