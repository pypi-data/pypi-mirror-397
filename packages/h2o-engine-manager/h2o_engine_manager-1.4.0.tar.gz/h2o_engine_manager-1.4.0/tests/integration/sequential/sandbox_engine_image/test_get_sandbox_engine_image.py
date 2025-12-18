import http
import json

import pytest

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_image.image import SandboxEngineImage
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_get_sandbox_engine_image(
    sandbox_engine_image_client_super_admin,
    sandbox_engine_image_client,
    delete_all_sandbox_engine_images_before_after,
):
    sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_image=(SandboxEngineImage(
            image = "my-image",
            display_name = "display my image",
            enabled = True,
            image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
            image_pull_secrets = ["secret1", "secret2"],
        )),
        sandbox_engine_image_id="i1",
    )

    # Non-existent image raises NOT FOUND.
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_image_client.get_sandbox_engine_image(name="workspaces/global/sandboxEngineImages/not-found")
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
    assert "not found" in json.loads(exc.value.body)["message"]

    image_get = sandbox_engine_image_client.get_sandbox_engine_image(name="workspaces/global/sandboxEngineImages/i1")

    assert image_get.name == "workspaces/global/sandboxEngineImages/i1"
    assert image_get.display_name == "display my image"
    assert image_get.enabled is True
    assert image_get.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
    assert image_get.image_pull_secrets == ["secret1", "secret2"]
