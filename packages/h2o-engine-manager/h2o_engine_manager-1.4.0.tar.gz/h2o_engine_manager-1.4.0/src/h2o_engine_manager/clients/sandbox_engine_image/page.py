import pprint

from h2o_engine_manager.clients.sandbox_engine_image.image import from_api_object
from h2o_engine_manager.gen.model.v1_list_sandbox_engine_images_response import (
    V1ListSandboxEngineImagesResponse,
)


class SandboxEngineImagesPage:
    """
    Represents a list of SandboxEngineImages together with a next_page_token for listing all SandboxEngineImages.
    """

    def __init__(self, list_api_response: V1ListSandboxEngineImagesResponse) -> None:
        api_objects = list_api_response.sandbox_engine_images
        self.sandbox_engine_images = []
        for api_version in api_objects:
            self.sandbox_engine_images.append(from_api_object(api_version))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
