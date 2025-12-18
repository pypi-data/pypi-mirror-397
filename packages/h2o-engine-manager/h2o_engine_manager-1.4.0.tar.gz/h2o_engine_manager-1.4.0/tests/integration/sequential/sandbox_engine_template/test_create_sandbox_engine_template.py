import http
import json
import re
import time

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_template.template import (
    SandboxEngineTemplate,
)
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_create_sandbox_engine_template(
    sandbox_engine_template_client_super_admin,
    sandbox_engine_template_client,
    delete_all_sandbox_engine_templates_before_after,
):
    to_create = SandboxEngineTemplate(
        memory_bytes_limit="2Gi",
        max_idle_duration="1h",
        display_name="display my template",
        milli_cpu_request=500,
        milli_cpu_limit=1000,
        gpu_resource="nvidia.com/gpu",
        gpu=1,
        memory_bytes_request="1Gi",
        storage_bytes="10Gi",
        environmental_variables={"KEY1": "VALUE1", "KEY2": "VALUE2"},
        enabled=True,
    )
    to_create_id = "t1"
    now_before = time.time()

    # regular user cannot create template
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_template_client.create_sandbox_engine_template(
            parent=GLOBAL_WORKSPACE,
            sandbox_engine_template=to_create,
            sandbox_engine_template_id=to_create_id,
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN

    # super-admin can create template
    created: SandboxEngineTemplate = (
        sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
            parent=GLOBAL_WORKSPACE,
            sandbox_engine_template=to_create,
            sandbox_engine_template_id=to_create_id,
        )
    )

    assert created.name == "workspaces/global/sandboxEngineTemplates/t1"
    assert created.display_name == "display my template"
    assert created.enabled is True
    assert created.milli_cpu_request == 500
    assert created.milli_cpu_limit == 1000
    assert created.gpu_resource == "nvidia.com/gpu"
    assert created.gpu == 1
    assert created.memory_bytes_request == "1Gi"
    assert created.memory_bytes_limit == "2Gi"
    assert created.storage_bytes == "10Gi"
    assert created.max_idle_duration == "1h"
    assert created.environmental_variables == {"KEY1": "VALUE1", "KEY2": "VALUE2"}
    now_after = time.time()
    assert now_before <= created.create_time.timestamp() <= now_after
    assert created.update_time is None
    assert re.match(r"^users/.+$", created.creator)
    assert created.updater == ""
    assert created.creator_display_name == "test-super-admin"
    assert created.updater_display_name == ""

    # Already exists error
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
            parent=GLOBAL_WORKSPACE,
            sandbox_engine_template=to_create,
            sandbox_engine_template_id=to_create_id,
        )
    assert exc.value.status == http.HTTPStatus.CONFLICT
    assert "already exists" in json.loads(exc.value.body)["message"]