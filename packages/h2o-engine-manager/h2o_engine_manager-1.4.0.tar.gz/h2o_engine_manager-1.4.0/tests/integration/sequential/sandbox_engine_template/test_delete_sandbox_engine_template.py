import http
import json

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_template.template import (
    SandboxEngineTemplate,
)
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_delete_sandbox_engine_templates(
    sandbox_engine_template_client_super_admin,
    sandbox_engine_template_client,
    delete_all_sandbox_engine_templates_before_after,
):
    created = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
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

    # Regular user cannot delete.
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_template_client.delete_sandbox_engine_template(name=created.name)
    assert exc.value.status == http.HTTPStatus.FORBIDDEN

    # Only super-admin can delete.
    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(
        name=created.name
    )

    # Check that template no longer exists.
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_template_client_super_admin.get_sandbox_engine_template(
            name=created.name
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
    assert "not found" in json.loads(exc.value.body)["message"]