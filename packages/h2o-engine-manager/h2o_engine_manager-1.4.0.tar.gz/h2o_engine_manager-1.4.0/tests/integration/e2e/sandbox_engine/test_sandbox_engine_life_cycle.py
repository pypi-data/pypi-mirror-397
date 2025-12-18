import http
import uuid

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState


@pytest.mark.timeout(180)
def test_sandbox_engine_life_cycle(
    sandbox_engine_client_super_admin,
    sandbox_engine_template_t1,
    sandbox_engine_image_i1,
):
    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    engine_id = f"sandbox-e1-{uuid.uuid4().hex[:8]}"

    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_t1.name,
            sandbox_engine_image=sandbox_engine_image_i1.name,
            display_name="Sandbox E1",
        ),
        sandbox_engine_id=engine_id,
    )

    assert engine.name == f"workspaces/{workspace_id}/sandboxEngines/{engine_id}"
    assert engine.display_name == "Sandbox E1"
    assert engine.state == SandboxEngineState.STATE_STARTING
    assert engine.sandbox_engine_image == sandbox_engine_image_i1.name
    assert engine.sandbox_engine_template == sandbox_engine_template_t1.name
    assert engine.create_time is not None
    assert engine.sandbox_engine_template_info.milli_cpu_request == 100
    assert engine.sandbox_engine_template_info.milli_cpu_limit == 200
    assert engine.sandbox_engine_template_info.memory_bytes_request == "10Mi"
    assert engine.sandbox_engine_template_info.memory_bytes_limit == "20Mi"
    assert engine.sandbox_engine_template_info.storage_bytes == "10Mi"
    assert engine.sandbox_engine_template_info.max_idle_duration == "4h"
    assert engine.sandbox_engine_template_info.gpu == 0

    # Terminate the sandbox engine
    engine = sandbox_engine_client_super_admin.terminate_sandbox_engine(name=engine.name)
    assert engine.state == SandboxEngineState.STATE_TERMINATING

    # Wait for termination to complete
    sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=30)
    engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
    assert engine.state == SandboxEngineState.STATE_TERMINATED

    # Delete the sandbox engine
    sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)

    # Engine might be deleted immediately or might be in DELETING state
    try:
        deleted_engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert deleted_engine.state == SandboxEngineState.STATE_DELETING
    except CustomApiException as e:
        # If already deleted, that's acceptable
        assert e.status == http.HTTPStatus.NOT_FOUND

    # Wait for deletion to complete (this handles both cases)
    sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=30)

    # Verify engine is fully deleted
    with pytest.raises(CustomApiException) as exc:
        sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND