from typing import List
from typing import Optional

from h2o_engine_manager.clients.auth.token_api_client import TokenApiClient
from h2o_engine_manager.clients.connection_config import ConnectionConfig
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_image.image import SandboxEngineImage
from h2o_engine_manager.clients.sandbox_engine_image.image import from_api_object
from h2o_engine_manager.clients.sandbox_engine_image.image_config import (
    SandboxEngineImageConfig,
)
from h2o_engine_manager.clients.sandbox_engine_image.page import SandboxEngineImagesPage
from h2o_engine_manager.gen import ApiException
from h2o_engine_manager.gen.api.sandbox_engine_image_service_api import (
    SandboxEngineImageServiceApi,
)
from h2o_engine_manager.gen.configuration import Configuration
from h2o_engine_manager.gen.model.v1_list_sandbox_engine_images_response import (
    V1ListSandboxEngineImagesResponse,
)
from h2o_engine_manager.gen.model.v1_sandbox_engine_image import V1SandboxEngineImage


class SandboxEngineImageClient:
    """SandboxEngineImageClient manages SandboxEngineImages."""

    def __init__(
        self,
        connection_config: ConnectionConfig,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
    ):
        """Initializes SandboxEngineImageClient.

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
            self.service_api = SandboxEngineImageServiceApi(api_client)

    def create_sandbox_engine_image(
        self,
        parent: str,
        sandbox_engine_image: SandboxEngineImage,
        sandbox_engine_image_id: str,
    ) -> SandboxEngineImage:
        """Standard Create method.

        Args:
            parent (str): Name of the version's parent workspace. Format: `workspaces/*`.
            sandbox_engine_image (SandboxEngineImage): SandboxEngineImage to create.
            sandbox_engine_image_id (str): Specify the SandboxEngineImage ID,
                which will become a part of the SandboxEngineImage resource name.
                It must:
                    - contain 1-63 characters
                    - contain only lowercase alphanumeric characters or hyphen ('-')
                    - start with an alphabetic character
                    - end with an alphanumeric character

        Returns:
            SandboxEngineImage: created SandboxEngineImage.
        """
        created_api_object: V1SandboxEngineImage
        try:
            created_api_object = self.service_api.sandbox_engine_image_service_create_sandbox_engine_image(
                parent=parent,
                sandbox_engine_image_id=sandbox_engine_image_id,
                sandbox_engine_image=sandbox_engine_image.to_api_object(),
            ).sandbox_engine_image
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(created_api_object)

    def get_sandbox_engine_image(self, name: str) -> SandboxEngineImage:
        """Standard Get method.

        Args:
            name: Name of the SandboxEngineImage to retrieve. Format: `workspaces/global/sandboxEngineImages/*`
        """
        api_object: V1SandboxEngineImage

        try:
            api_object = self.service_api.sandbox_engine_image_service_get_sandbox_engine_image(
                name_11=name
            ).sandbox_engine_image
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def list_sandbox_engine_images(
        self,
        parent: str,
        page_size: int = 0,
        page_token: str = "",
    ) -> SandboxEngineImagesPage:
        """Standard list method.

        Args:
            parent (str): Name of the workspace from which to list versions. Format: `workspaces/*`.
            page_size (int): Maximum number of SandboxEngineImages to return in a response.
                If unspecified (or set to 0), at most 50 SandboxEngineImages will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the SandboxEngineImagesPage.

        Returns:
            SandboxEngineImagesPage: SandboxEngineImagesPage object.
        """
        list_response: V1ListSandboxEngineImagesResponse

        try:
            list_response = (
                self.service_api.sandbox_engine_image_service_list_sandbox_engine_images(
                    parent=parent,
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return SandboxEngineImagesPage(list_response)

    def list_all_sandbox_engine_images(self, parent: str) -> List[SandboxEngineImage]:
        """Help method for listing all SandboxEngineImages.

        Args:
            parent (str): Name of the workspace from which to list versions. Format: `workspaces/*`.
        """

        all_versions: List[SandboxEngineImage] = []
        next_page_token = ""
        while True:
            versions_page = self.list_sandbox_engine_images(
                parent=parent,
                page_size=1000,
                page_token=next_page_token,
            )
            all_versions = all_versions + versions_page.sandbox_engine_images
            next_page_token = versions_page.next_page_token
            if next_page_token == "":
                break

        return all_versions

    def update_sandbox_engine_image(
        self,
        sandbox_engine_image: SandboxEngineImage,
        update_mask: str = "*",
    ) -> SandboxEngineImage:
        """Standard Update method.

        Args:
            sandbox_engine_image (SandboxEngineImage): version to update.
            update_mask (str): The field mask to use for the update.
                Allowed field paths are:
                    - display_name
                    - enabled
                    - image
                    - image_pull_policy
                    - image_pull_secrets
                Default value "*" will update all updatable fields.

        Returns:
            SandboxEngineImage: Updated SandboxEngineImage.
        """
        updated_api_object: V1SandboxEngineImage

        try:
            updated_api_object = (
                self.service_api.sandbox_engine_image_service_update_sandbox_engine_image(
                    sandbox_engine_image_name=sandbox_engine_image.name,
                    update_mask=update_mask,
                    sandbox_engine_image=sandbox_engine_image.to_resource(),
                ).sandbox_engine_image
            )
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=updated_api_object)

    def delete_sandbox_engine_image(self, name: str) -> None:
        """Standard Delete method.

        Args:
            name (str): Name of the SandboxEngineImage to delete. Format is `workspaces/global/sandboxEngineImages/*`
        """
        try:
            self.service_api.sandbox_engine_image_service_delete_sandbox_engine_image(
                name_10=name
            )
        except ApiException as e:
            raise CustomApiException(e)

    def delete_all_sandbox_engine_images(self, parent: str) -> None:
        """Help method for deleting all SandboxEngineImages in a specified parent workspace.

        Args:
            parent (str): Parent workspace name. Format is `workspaces/*`.
        """
        versions = self.list_all_sandbox_engine_images(parent=parent)
        for version in versions:
            self.delete_sandbox_engine_image(name=version.name)

    def apply_sandbox_engine_image_configs(
        self,
        configs: List[SandboxEngineImageConfig],
        parent: str = "workspaces/global",
    ) -> List[SandboxEngineImage]:
        """
        Set all SandboxEngineImages to a state defined in the configs in the specified parent workspace.
        SandboxEngineImages that are not specified in the configs will be deleted in the specified parent workspace.
        SandboxEngineImages that are specified in the configs will be recreated with the new values
            in the specified parent workspace.

        Args:
            configs: SandboxEngineImage configurations that should be applied.
            parent: Workspace name in which to apply configs. Format is `workspaces/*`.

        Returns: applied SandboxEngineImages

        """
        self.delete_all_sandbox_engine_images(parent=parent)

        for cfg in configs:
            self.create_sandbox_engine_image(
                parent=parent,
                sandbox_engine_image=cfg.to_sandbox_engine_image(),
                sandbox_engine_image_id=cfg.sandbox_engine_image_id,
            )

        return self.list_all_sandbox_engine_images(parent=parent)
