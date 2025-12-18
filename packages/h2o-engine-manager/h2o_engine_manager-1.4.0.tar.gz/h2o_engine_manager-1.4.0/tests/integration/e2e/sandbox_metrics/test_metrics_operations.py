import uuid

import pytest

from h2o_engine_manager.clients.sandbox.metrics.client import MetricsClient
from h2o_engine_manager.clients.sandbox_engine.client import SandboxEngineClient
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState

GLOBAL_WORKSPACE = "workspaces/global"


@pytest.mark.timeout(300)
def test_read_metrics_returns_resource_usage(
    sandbox_engine_client_super_admin: SandboxEngineClient,
    metrics_client_super_admin: MetricsClient,
    sandbox_engine_template_metrics_test1,
    sandbox_engine_image_metrics_test1,
):
    """Test that read_metrics returns memory, disk, and CPU usage statistics."""
    engine_id = f"metrics-test-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    sandbox_engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_metrics_test1.name,
            sandbox_engine_image=sandbox_engine_image_metrics_test1.name,
        ),
        sandbox_engine_id=engine_id,
    )
    sandbox_engine_name = sandbox_engine.name

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=sandbox_engine_name, timeout_seconds=120)
        sandbox_engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=sandbox_engine_name)
        assert sandbox_engine.state == SandboxEngineState.STATE_RUNNING

        # Read metrics from the sandbox engine
        metrics = metrics_client_super_admin.read_metrics(name=sandbox_engine_name)

        # Verify metrics structure
        assert metrics is not None
        assert metrics.collect_time is not None

        # Verify memory metrics
        assert metrics.memory is not None
        assert metrics.memory.current_bytes >= 0

        # Verify disk metrics
        assert metrics.disk is not None
        assert metrics.disk.total_bytes > 0
        assert metrics.disk.available_bytes >= 0
        assert metrics.disk.used_bytes >= 0
        assert metrics.disk.usage_ratio >= 0.0
        assert metrics.disk.usage_ratio <= 1.0

        # Verify CPU metrics
        assert metrics.cpu is not None
        assert metrics.cpu.usage_ratio >= 0.0

    finally:
        # Cleanup: delete the sandbox engine
        sandbox_engine_client_super_admin.delete_sandbox_engine(name=sandbox_engine_name)