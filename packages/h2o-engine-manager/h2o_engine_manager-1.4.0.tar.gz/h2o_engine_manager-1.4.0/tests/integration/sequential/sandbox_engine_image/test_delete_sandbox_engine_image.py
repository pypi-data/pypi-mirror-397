import http
import json

import pytest

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_image.image import SandboxEngineImage
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_delete_sandbox_engine_images(
    sandbox_engine_image_client_super_admin,
    sandbox_engine_image_client,
    delete_all_sandbox_engine_images_before_after,
):
    created = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_image=(SandboxEngineImage(
            image = "my-image",
            display_name = "display my image",
            enabled = True,
            image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
            image_pull_secrets = ["secret1", "secret2"],
        )),
        sandbox_engine_image_id="i1",
    )

    # Regular user cannot delete.
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_image_client.delete_sandbox_engine_image(name=created.name)
    assert exc.value.status == http.HTTPStatus.FORBIDDEN

    # Only super-admin can delete.
    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=created.name)

    # Check that image no longer exists.
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_image_client_super_admin.get_sandbox_engine_image(name=created.name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
    assert "not found" in json.loads(exc.value.body)["message"]
