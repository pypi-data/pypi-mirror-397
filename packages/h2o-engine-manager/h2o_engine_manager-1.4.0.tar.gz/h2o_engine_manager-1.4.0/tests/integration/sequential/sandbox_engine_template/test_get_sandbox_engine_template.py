import http
import json

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_template.template import (
    SandboxEngineTemplate,
)
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_get_sandbox_engine_template(
    sandbox_engine_template_client_super_admin,
    sandbox_engine_template_client,
    delete_all_sandbox_engine_templates_before_after,
):
    sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_template=(
            SandboxEngineTemplate(
                memory_bytes_limit="2Gi",
                max_idle_duration="1h",
                display_name="display my template",
                milli_cpu_request=500,
                milli_cpu_limit=1000,
                memory_bytes_request="1Gi",
                storage_bytes="10Gi",
                enabled=True,
            )
        ),
        sandbox_engine_template_id="t1",
    )

    # Non-existent template raises NOT FOUND.
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_template_client.get_sandbox_engine_template(
            name="workspaces/global/sandboxEngineTemplates/not-found"
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
    assert "not found" in json.loads(exc.value.body)["message"]

    template_get = sandbox_engine_template_client.get_sandbox_engine_template(
        name="workspaces/global/sandboxEngineTemplates/t1"
    )

    assert template_get.name == "workspaces/global/sandboxEngineTemplates/t1"
    assert template_get.display_name == "display my template"
    assert template_get.enabled is True
    assert template_get.milli_cpu_request == 500
    assert template_get.milli_cpu_limit == 1000
    assert template_get.memory_bytes_request == "1Gi"
    assert template_get.memory_bytes_limit == "2Gi"
    assert template_get.storage_bytes == "10Gi"
    assert template_get.max_idle_duration == "1h"