import http
import re
import time

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_template.template import (
    SandboxEngineTemplate,
)
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_update_sandbox_engine_templates(
    sandbox_engine_template_client_super_admin,
    sandbox_engine_template_client_admin,
    sandbox_engine_template_client,
    delete_all_sandbox_engine_templates_before_after,
):
    # Create initial sandbox engine template
    original = SandboxEngineTemplate(
        memory_bytes_limit="2Gi",
        max_idle_duration="1h",
        display_name="display original",
        milli_cpu_request=500,
        milli_cpu_limit=1000,
        gpu_resource="nvidia.com/gpu",
        gpu=1,
        memory_bytes_request="1Gi",
        storage_bytes="10Gi",
        environmental_variables={"KEY1": "VALUE1"},
        enabled=True,
    )
    created = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_template=original,
        sandbox_engine_template_id="t1",
    )

    # Verify initial state
    assert created.name == "workspaces/global/sandboxEngineTemplates/t1"
    assert created.display_name == "display original"
    assert created.enabled is True
    assert created.milli_cpu_request == 500
    assert created.milli_cpu_limit == 1000
    assert created.gpu_resource == "nvidia.com/gpu"
    assert created.gpu == 1
    assert created.memory_bytes_request == "1Gi"
    assert created.memory_bytes_limit == "2Gi"
    assert created.storage_bytes == "10Gi"
    assert created.max_idle_duration == "1h"
    assert created.environmental_variables == {"KEY1": "VALUE1"}
    assert re.match(r"^users/.+$", created.creator)
    assert created.updater == ""
    assert created.creator_display_name == "test-super-admin"
    assert created.updater_display_name == ""

    original_creator = created.creator
    original_create_time = created.create_time

    # Test that regular user cannot update
    to_update_by_regular_user = SandboxEngineTemplate(
        name=created.name,
        memory_bytes_limit="4Gi",
        max_idle_duration="2h",
        display_name="updated by regular user",
        milli_cpu_request=1000,
        milli_cpu_limit=2000,
        memory_bytes_request="2Gi",
        storage_bytes="20Gi",
        enabled=True,
    )
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_template_client.update_sandbox_engine_template(
            sandbox_engine_template=to_update_by_regular_user
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN

    # Test partial update with specific field mask (only "display_name" field)
    now_before_partial_update = time.time()
    to_update_partial = SandboxEngineTemplate(
        name=created.name,
        memory_bytes_limit="4Gi",
        max_idle_duration="2h",
        display_name="display updated",
        milli_cpu_request=1000,
        milli_cpu_limit=2000,
        memory_bytes_request="2Gi",
        storage_bytes="20Gi",
        enabled=False,
    )
    partially_updated = (
        sandbox_engine_template_client_super_admin.update_sandbox_engine_template(
            sandbox_engine_template=to_update_partial, update_mask="display_name"
        )
    )
    now_after_partial_update = time.time()

    # Verify that only "display_name" field was updated, other fields remain unchanged
    assert partially_updated.name == "workspaces/global/sandboxEngineTemplates/t1"
    assert partially_updated.display_name == "display updated"  # Updated
    assert partially_updated.milli_cpu_request == 500  # NOT updated
    assert partially_updated.milli_cpu_limit == 1000  # NOT updated
    assert partially_updated.memory_bytes_request == "1Gi"  # NOT updated
    assert partially_updated.memory_bytes_limit == "2Gi"  # NOT updated
    assert partially_updated.storage_bytes == "10Gi"  # NOT updated
    assert partially_updated.max_idle_duration == "1h"  # NOT updated
    assert partially_updated.enabled is True  # NOT updated
    assert partially_updated.create_time == original_create_time
    assert partially_updated.update_time is not None
    assert partially_updated.create_time != partially_updated.update_time
    assert (
        now_before_partial_update
        <= partially_updated.update_time.timestamp()
        <= now_after_partial_update
    )
    assert partially_updated.creator == original_creator
    assert partially_updated.updater == original_creator
    assert partially_updated.creator_display_name == "test-super-admin"
    assert partially_updated.updater_display_name == "test-super-admin"

    # Test full update with default mask (all fields)
    now_before_full_update = time.time()
    to_update_full = SandboxEngineTemplate(
        name=created.name,
        memory_bytes_limit="8Gi",
        max_idle_duration="4h",
        display_name="display fully updated",
        milli_cpu_request=2000,
        milli_cpu_limit=4000,
        gpu_resource="amd.com/gpu",
        gpu=2,
        memory_bytes_request="4Gi",
        storage_bytes="50Gi",
        environmental_variables={"KEY2": "VALUE2", "KEY3": "VALUE3"},
        enabled=False,
    )
    fully_updated = (
        sandbox_engine_template_client_super_admin.update_sandbox_engine_template(
            sandbox_engine_template=to_update_full
        )
    )
    now_after_full_update = time.time()

    # Verify that all updatable fields were updated
    assert fully_updated.name == "workspaces/global/sandboxEngineTemplates/t1"
    assert fully_updated.display_name == "display fully updated"
    assert fully_updated.milli_cpu_request == 2000
    assert fully_updated.milli_cpu_limit == 4000
    assert fully_updated.gpu_resource == "amd.com/gpu"
    assert fully_updated.gpu == 2
    assert fully_updated.memory_bytes_request == "4Gi"
    assert fully_updated.memory_bytes_limit == "8Gi"
    assert fully_updated.storage_bytes == "50Gi"
    assert fully_updated.max_idle_duration == "4h"
    assert fully_updated.environmental_variables == {"KEY2": "VALUE2", "KEY3": "VALUE3"}
    assert fully_updated.enabled is False
    assert fully_updated.create_time == original_create_time
    assert fully_updated.update_time is not None
    assert (
        now_before_full_update
        <= fully_updated.update_time.timestamp()
        <= now_after_full_update
    )
    assert fully_updated.creator == original_creator
    assert fully_updated.updater == original_creator
    assert fully_updated.creator_display_name == "test-super-admin"
    assert fully_updated.updater_display_name == "test-super-admin"