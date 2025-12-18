import http
import json
import re
import time

import pytest

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_image.image import SandboxEngineImage
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_create_sandbox_engine_image(
    sandbox_engine_image_client_super_admin,
    sandbox_engine_image_client,
    delete_all_sandbox_engine_images_before_after,
):
    to_create = SandboxEngineImage(
        image = "my-image",
        display_name = "display my image",
        enabled = True,
        image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        image_pull_secrets = ["secret1", "secret2"],
    )
    to_create_id = "i1"
    now_before = time.time()

    # regular user cannot create image
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_image_client.create_sandbox_engine_image(
            parent=GLOBAL_WORKSPACE,
            sandbox_engine_image=to_create,
            sandbox_engine_image_id=to_create_id,
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN

    # super-admin can create image
    created: SandboxEngineImage = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_image=to_create,
        sandbox_engine_image_id=to_create_id,
    )

    assert created.name == "workspaces/global/sandboxEngineImages/i1"
    assert created.display_name == "display my image"
    assert created.enabled is True
    assert created.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS
    assert created.image_pull_secrets == ["secret1", "secret2"]
    now_after = time.time()
    assert now_before <= created.create_time.timestamp() <= now_after
    assert created.update_time is None
    assert re.match(r"^users/.+$", created.creator)
    assert created.updater == ""
    assert created.creator_display_name == "test-super-admin"
    assert created.updater_display_name == ""

    # Already exists error
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
            parent=GLOBAL_WORKSPACE,
            sandbox_engine_image=to_create,
            sandbox_engine_image_id=to_create_id,
        )
    assert exc.value.status == http.HTTPStatus.CONFLICT
    assert "already exists" in json.loads(exc.value.body)["message"]
