import http
import re
import time

import pytest

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_image.image import SandboxEngineImage
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_update_sandbox_engine_images(
    sandbox_engine_image_client_super_admin,
    sandbox_engine_image_client_admin,
    sandbox_engine_image_client,
    delete_all_sandbox_engine_images_before_after,
):
    # Create initial sandbox engine image
    original = SandboxEngineImage(
        image="my-image",
        display_name="display original",
        enabled=True,
        image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        image_pull_secrets=["secret1", "secret2"],
    )
    created = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_image=original,
        sandbox_engine_image_id="i1",
    )

    # Verify initial state
    assert created.name == "workspaces/global/sandboxEngineImages/i1"
    assert created.image == "my-image"
    assert created.display_name == "display original"
    assert created.enabled is True
    assert created.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS
    assert created.image_pull_secrets == ["secret1", "secret2"]
    assert re.match(r"^users/.+$", created.creator)
    assert created.updater == ""
    assert created.creator_display_name == "test-super-admin"
    assert created.updater_display_name == ""

    original_creator = created.creator
    original_create_time = created.create_time

    # Test that regular user cannot update
    to_update_by_regular_user = SandboxEngineImage(
        name=created.name,
        image="my-image-2",
        display_name="updated by regular user",
        enabled=True,
        image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        image_pull_secrets=["secret1", "secret2"],
    )
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_image_client.update_sandbox_engine_image(
            sandbox_engine_image=to_update_by_regular_user
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN

    # Test partial update with specific field mask (only "image" field)
    now_before_partial_update = time.time()
    to_update_partial = SandboxEngineImage(
        name=created.name,
        image="my-image-2",
        display_name="this should not be updated",
        enabled=False,
        image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_NEVER,
        image_pull_secrets=["secret3"],
    )
    partially_updated = sandbox_engine_image_client_super_admin.update_sandbox_engine_image(
        sandbox_engine_image=to_update_partial,
        update_mask="image"
    )
    now_after_partial_update = time.time()

    # Verify that only "image" field was updated, other fields remain unchanged
    assert partially_updated.name == "workspaces/global/sandboxEngineImages/i1"
    assert partially_updated.image == "my-image-2"  # Updated
    assert partially_updated.display_name == "display original"  # NOT updated
    assert partially_updated.enabled is True  # NOT updated
    assert partially_updated.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS  # NOT updated
    assert partially_updated.image_pull_secrets == ["secret1", "secret2"]  # NOT updated
    assert partially_updated.create_time == original_create_time
    assert partially_updated.update_time is not None
    assert partially_updated.create_time != partially_updated.update_time
    assert now_before_partial_update <= partially_updated.update_time.timestamp() <= now_after_partial_update
    assert partially_updated.creator == original_creator
    assert partially_updated.updater == original_creator
    assert partially_updated.creator_display_name == "test-super-admin"
    assert partially_updated.updater_display_name == "test-super-admin"

    # Test full update with default mask (all fields)
    now_before_full_update = time.time()
    to_update_full = SandboxEngineImage(
        name=created.name,
        image="my-image-3",
        display_name="display updated",
        enabled=False,
        image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
        image_pull_secrets=["secret3", "secret4"],
    )
    fully_updated = sandbox_engine_image_client_super_admin.update_sandbox_engine_image(
        sandbox_engine_image=to_update_full
    )
    now_after_full_update = time.time()

    # Verify that all updatable fields were updated
    assert fully_updated.name == "workspaces/global/sandboxEngineImages/i1"
    assert fully_updated.image == "my-image-3"
    assert fully_updated.display_name == "display updated"
    assert fully_updated.enabled is False
    assert fully_updated.image_pull_policy == ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT
    assert fully_updated.image_pull_secrets == ["secret3", "secret4"]
    assert fully_updated.create_time == original_create_time
    assert fully_updated.update_time is not None
    assert now_before_full_update <= fully_updated.update_time.timestamp() <= now_after_full_update
    assert fully_updated.creator == original_creator
    assert fully_updated.updater == original_creator
    assert fully_updated.creator_display_name == "test-super-admin"
    assert fully_updated.updater_display_name == "test-super-admin"
