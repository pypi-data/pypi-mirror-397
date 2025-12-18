import http
import uuid

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox.process.ps import Process
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState
from h2o_engine_manager.gen.exceptions import ApiValueError


@pytest.mark.timeout(300)
def test_process_operations_require_creator_authentication(
    process_client,
    process_client_super_admin,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_process_auth_test,
    sandbox_engine_image_process_auth_test,
):
    """Test that only the creator can perform process operations on a sandbox engine."""
    workspace_id = "default"
    engine_id = f"sandbox-proc-auth-{uuid.uuid4().hex[:8]}"

    # Super admin (creator) creates a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_process_auth_test.name,
            sandbox_engine_image=sandbox_engine_image_process_auth_test.name,
            display_name="Process Auth Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Creator (super admin) should be able to create a process
        process = process_client_super_admin.create_process(
            parent=engine.name,
            process=Process(
                command="echo",
                args=["Created by super admin"],
            ),
            auto_run=True,
        )

        # Wait for process to complete
        process_client_super_admin.wait_process(name=process.name)

        # Non-creator (basic user) should NOT be able to get the process
        with pytest.raises(CustomApiException) as exc:
            process_client.get_process(name=process.name)
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to create a process
        with pytest.raises(CustomApiException) as exc:
            process_client.create_process(
                parent=engine.name,
                process=Process(
                    command="echo",
                    args=["Created by basic user"],
                ),
                auto_run=True,
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to list processes
        with pytest.raises(CustomApiException) as exc:
            process_client.list_processes(parent=engine.name)
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to wait for process
        with pytest.raises(CustomApiException) as exc:
            process_client.wait_process(name=process.name)
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to read output
        with pytest.raises(CustomApiException) as exc:
            process_client.read_output(name=process.name)
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to send signal
        with pytest.raises(CustomApiException) as exc:
            process_client.send_signal(name=process.name, signal=15)
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Verify creator (super admin) can still access the process
        fetched_process = process_client_super_admin.get_process(name=process.name)
        assert fetched_process.name == process.name

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_process_operations_require_running_state(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_process_state_test,
    sandbox_engine_image_process_state_test,
):
    """Test that process operations fail when engine is not in RUNNING state."""
    workspace_id = "default"
    engine_id = f"sandbox-proc-state-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_process_state_test.name,
            sandbox_engine_image=sandbox_engine_image_process_state_test.name,
            display_name="Process State Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Engine is in STARTING state - process operations should fail
        assert engine.state == SandboxEngineState.STATE_STARTING

        process_client = super_admin_clients.sandbox_clients.process_client

        # Test that create_process fails when engine is STARTING
        with pytest.raises(CustomApiException) as exc:
            process_client.create_process(
                parent=engine.name,
                process=Process(
                    command="echo",
                    args=["test"],
                ),
                auto_run=True,
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST
        assert "not in running state" in str(exc.value).lower()

        # Wait for engine to be RUNNING
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Now process operations should succeed
        process = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="echo",
                args=["Engine is now running"],
            ),
            auto_run=True,
        )

        process_client.wait_process(name=process.name)
        output = process_client.read_output(name=process.name)
        assert b"Engine is now running" in output

        # Terminate the engine
        sandbox_engine_client_super_admin.terminate_sandbox_engine(name=engine.name)

        # Wait a bit for state to update to TERMINATING
        import time
        time.sleep(2)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)

        # Process operations should fail when engine is TERMINATING or TERMINATED
        if engine.state in [
            SandboxEngineState.STATE_TERMINATING,
            SandboxEngineState.STATE_TERMINATED,
        ]:
            with pytest.raises(CustomApiException) as exc:
                process_client.create_process(
                    parent=engine.name,
                    process=Process(
                        command="echo",
                        args=["test"],
                    ),
                    auto_run=True,
                )
            assert exc.value.status == http.HTTPStatus.BAD_REQUEST
            assert "not in running state" in str(exc.value).lower()

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_process_operations_validate_resource_name_format(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_process_validation_test,
    sandbox_engine_image_process_validation_test,
):
    """Test that process operations validate resource name format."""
    workspace_id = "default"
    engine_id = f"sandbox-proc-validation-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_process_validation_test.name,
            sandbox_engine_image=sandbox_engine_image_process_validation_test.name,
            display_name="Process Validation Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        process_client = super_admin_clients.sandbox_clients.process_client

        # Test with invalid parent resource name (missing workspaces/ prefix)
        # This is caught by client-side validation, so we expect ApiValueError
        with pytest.raises(ApiValueError) as exc:
            process_client.create_process(
                parent="invalid-parent-name",
                process=Process(
                    command="echo",
                    args=["test"],
                ),
            )
        assert "must match regular expression" in str(exc.value)

        # Test with invalid parent resource name (wrong format)
        # This is caught by client-side validation, so we expect ApiValueError
        with pytest.raises(ApiValueError) as exc:
            process_client.create_process(
                parent="workspaces/default",  # Missing sandboxEngines/ part
                process=Process(
                    command="echo",
                    args=["test"],
                ),
            )
        assert "must match regular expression" in str(exc.value)

        # Test with empty parent resource name
        # This is caught by client-side validation, so we expect ApiValueError
        with pytest.raises(ApiValueError) as exc:
            process_client.create_process(
                parent="",
                process=Process(
                    command="echo",
                    args=["test"],
                ),
            )
        assert "must match regular expression" in str(exc.value)

        # Test with valid parent resource name should succeed
        process = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="echo",
                args=["Valid resource name"],
            ),
            auto_run=True,
        )

        process_client.wait_process(name=process.name)
        output = process_client.read_output(name=process.name)
        assert b"Valid resource name" in output

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_process_operations_on_nonexistent_engine(
    super_admin_clients,
):
    """Test that process operations fail gracefully on non-existent engine."""
    process_client = super_admin_clients.sandbox_clients.process_client

    # Use a properly formatted but non-existent engine name
    nonexistent_engine_name = (
        f"workspaces/default/sandboxEngines/nonexistent-{uuid.uuid4().hex[:8]}"
    )

    # Test create_process on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        process_client.create_process(
            parent=nonexistent_engine_name,
            process=Process(
                command="echo",
                args=["test"],
            ),
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test list_processes on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        process_client.list_processes(parent=nonexistent_engine_name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Use a properly formatted but non-existent process name
    nonexistent_process_name = (
        f"{nonexistent_engine_name}/processes/nonexistent-{uuid.uuid4().hex[:8]}"
    )

    # Test get_process on non-existent process
    with pytest.raises(CustomApiException) as exc:
        process_client.get_process(name=nonexistent_process_name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test start_process on non-existent process
    with pytest.raises(CustomApiException) as exc:
        process_client.start_process(name=nonexistent_process_name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test wait_process on non-existent process
    with pytest.raises(CustomApiException) as exc:
        process_client.wait_process(name=nonexistent_process_name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test read_output on non-existent process
    with pytest.raises(CustomApiException) as exc:
        process_client.read_output(name=nonexistent_process_name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test send_signal on non-existent process
    with pytest.raises(CustomApiException) as exc:
        process_client.send_signal(name=nonexistent_process_name, signal=15)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND