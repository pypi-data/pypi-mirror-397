from typing import List
from typing import Optional

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.sandbox_engine_image.image import SandboxEngineImage


class SandboxEngineImageConfig:
    """
    SandboxEngineImage configuration used as input for apply method.
    """

    def __init__(
        self,
        sandbox_engine_image_id: str,
        image: str,
        enabled: bool = True,
        display_name: str = "",
        image_pull_policy: ImagePullPolicy = ImagePullPolicy.IMAGE_PULL_POLICY_UNSPECIFIED,
        image_pull_secrets: Optional[List[str]] = None,
    ):
        self.sandbox_engine_image_id = sandbox_engine_image_id
        self.image = image
        self.enabled = enabled
        self.display_name = display_name
        self.image_pull_policy = image_pull_policy
        self.image_pull_secrets = image_pull_secrets

    def to_sandbox_engine_image(self):
        return SandboxEngineImage(
            image=self.image,
            enabled=self.enabled,
            display_name=self.display_name,
            image_pull_policy=self.image_pull_policy,
            image_pull_secrets=self.image_pull_secrets,
        )
