from typing import List

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.sandbox_engine_image.image import SandboxEngineImage
from h2o_engine_manager.clients.sandbox_engine_image.image_config import (
    SandboxEngineImageConfig,
)
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_apply_sandbox_engine_images_super_admin(
    sandbox_engine_image_client_super_admin,
    delete_all_sandbox_engine_images_before_after,
):
    sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_image=SandboxEngineImage(
            image = "my-image-1",
            display_name = "display my image",
            image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="img1",
    )
    sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_image=SandboxEngineImage(
            image = "my-image-2",
            image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_NEVER,
        ),
        sandbox_engine_image_id="img2",
    )
    images = sandbox_engine_image_client_super_admin.list_all_sandbox_engine_images(parent=GLOBAL_WORKSPACE)
    assert len(images) == 2
    assert images[0].name == "workspaces/global/sandboxEngineImages/img2"
    assert images[1].name == "workspaces/global/sandboxEngineImages/img1"
    assert images[1].display_name == "display my image"

    configs: List[SandboxEngineImageConfig] = [
        SandboxEngineImageConfig(
            sandbox_engine_image_id="i1",
            image = "my-image-1",
            image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
        ),
        SandboxEngineImageConfig(
            sandbox_engine_image_id="i2",
            image = "my-image-2",
            image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
        ),
        SandboxEngineImageConfig(
            sandbox_engine_image_id="i3",
            image = "my-image-3",
            image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
        )
    ]

    # When applying SandboxEngineImage configs.
    applied_images: list[SandboxEngineImage] = sandbox_engine_image_client_super_admin.apply_sandbox_engine_image_configs(configs=configs)

    # Then only applied images exist with specified params.
    assert len(applied_images) == 3
    assert applied_images[0].name == "workspaces/global/sandboxEngineImages/i3"
    assert applied_images[0].image == "my-image-3"
    assert applied_images[0].image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
    assert applied_images[0].enabled is True
    assert applied_images[0].display_name == ""

    assert applied_images[1].name == "workspaces/global/sandboxEngineImages/i2"
    assert applied_images[1].image == "my-image-2"
    assert applied_images[1].image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT

    assert applied_images[2].name == "workspaces/global/sandboxEngineImages/i1"
    assert applied_images[2].image == "my-image-1"
    assert applied_images[2].image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
