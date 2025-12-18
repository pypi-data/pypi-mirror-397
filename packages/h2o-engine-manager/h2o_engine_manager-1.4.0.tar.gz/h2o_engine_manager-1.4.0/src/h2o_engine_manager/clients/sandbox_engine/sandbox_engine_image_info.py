import pprint
from datetime import datetime
from typing import List
from typing import Optional

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.base.image_pull_policy import (
    from_image_pull_policy_api_object,
)
from h2o_engine_manager.gen.model.v1_sandbox_engine_image_info import (
    V1SandboxEngineImageInfo,
)


class SandboxEngineImageInfo:
    """
    The original SandboxEngineImage data used by SandboxEngine when using the SandboxEngineImage.
    """

    def __init__(
        self,
        image: str = "",
        name: str = "",
        display_name: str = "",
        enabled: bool = True,
        image_pull_policy: ImagePullPolicy = ImagePullPolicy.IMAGE_PULL_POLICY_UNSPECIFIED,
        image_pull_secrets: Optional[List[str]] = None,
        create_time: Optional[datetime] = None,
        update_time: Optional[datetime] = None,
        creator: str = "",
        updater: str = "",
        creator_display_name: str = "",
        updater_display_name: str = "",
    ):
        """
        SandboxEngineImageInfo represents the original SandboxEngineImage data.

        Args:
            image: Docker image name.
            name: Resource name.
            display_name: Human-readable name.
            enabled: Whether the image is enabled.
            image_pull_policy: Image pull policy.
            image_pull_secrets: Image pull secrets.
            create_time: Creation timestamp.
            update_time: Last update timestamp.
            creator: Creator identifier.
            updater: Last updater identifier.
            creator_display_name: Creator display name.
            updater_display_name: Last updater display name.
        """
        if image_pull_secrets is None:
            image_pull_secrets = []

        self.image = image
        self.name = name
        self.display_name = display_name
        self.enabled = enabled
        self.image_pull_policy = image_pull_policy
        self.image_pull_secrets = image_pull_secrets
        self.create_time = create_time
        self.update_time = update_time
        self.creator = creator
        self.updater = updater
        self.creator_display_name = creator_display_name
        self.updater_display_name = updater_display_name

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def sandbox_engine_image_info_from_api_object(
    api_object: Optional[V1SandboxEngineImageInfo],
) -> Optional[SandboxEngineImageInfo]:
    if api_object is None:
        return None

    return SandboxEngineImageInfo(
        image=api_object.image,
        name=api_object.name,
        display_name=api_object.display_name,
        enabled=api_object.enabled,
        image_pull_policy=from_image_pull_policy_api_object(
            api_object.image_pull_policy
        ),
        image_pull_secrets=api_object.image_pull_secrets,
        create_time=api_object.create_time,
        update_time=api_object.update_time,
        creator=api_object.creator,
        updater=api_object.updater,
        creator_display_name=api_object.creator_display_name,
        updater_display_name=api_object.updater_display_name,
    )