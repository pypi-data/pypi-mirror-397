import http
import uuid

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox.port.port import Port
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState
from h2o_engine_manager.gen.exceptions import ApiValueError


@pytest.mark.timeout(300)
def test_port_operations_require_creator_authentication(
    port_client,
    port_client_super_admin,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_port_auth_test,
    sandbox_engine_image_port_auth_test,
):
    """Test that only the creator can perform port operations on a sandbox engine."""
    workspace_id = "default"
    engine_id = f"sandbox-port-auth-{uuid.uuid4().hex[:8]}"

    # Super admin (creator) creates a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_port_auth_test.name,
            sandbox_engine_image=sandbox_engine_image_port_auth_test.name,
            display_name="Port Auth Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Creator (super admin) should be able to create a port
        port = port_client_super_admin.create_port(
            parent=engine.name,
            port=Port(
                display_name="Auth Test Port",
                public=False,
            ),
            port_id="8888",
        )

        # Non-creator (basic user) should NOT be able to get the port
        with pytest.raises(CustomApiException) as exc:
            port_client.get_port(name=port.name)
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to create a port
        with pytest.raises(CustomApiException) as exc:
            port_client.create_port(
                parent=engine.name,
                port=Port(
                    display_name="Unauthorized Port",
                    public=False,
                ),
                port_id="9999",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to list ports
        with pytest.raises(CustomApiException) as exc:
            port_client.list_ports(parent=engine.name)
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to update port
        with pytest.raises(CustomApiException) as exc:
            port.display_name = "Changed Name"
            port_client.update_port(port=port, update_mask=["display_name"])
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to delete port
        with pytest.raises(CustomApiException) as exc:
            port_client.delete_port(name=port.name)
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Verify creator (super admin) can still access the port
        fetched_port = port_client_super_admin.get_port(name=port.name)
        assert fetched_port.name == port.name

        # Clean up: Creator deletes the port
        port_client_super_admin.delete_port(name=port.name)

    finally:
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_port_operations_require_starting_or_running_state(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_port_state_test,
    sandbox_engine_image_port_state_test,
):
    """Test that port operations work when engine is STARTING or RUNNING, but fail in other states."""
    workspace_id = "default"
    engine_id = f"sandbox-port-state-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_port_state_test.name,
            sandbox_engine_image=sandbox_engine_image_port_state_test.name,
            display_name="Port State Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Engine is in STARTING state - port operations should work (ports allow STARTING or RUNNING)
        assert engine.state == SandboxEngineState.STATE_STARTING

        port_client = super_admin_clients.sandbox_clients.port_client

        # Port operations should succeed when engine is STARTING
        port_starting = port_client.create_port(
            parent=engine.name,
            port=Port(
                display_name="Port Created While Starting",
                public=False,
            ),
            port_id="5555",
        )
        assert port_starting.name is not None

        # Clean up port created during STARTING
        port_client.delete_port(name=port_starting.name)

        # Wait for engine to be RUNNING
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Port operations should also succeed when engine is RUNNING
        port_running = port_client.create_port(
            parent=engine.name,
            port=Port(
                display_name="Port Created While Running",
                public=False,
            ),
            port_id="5556",
        )

        assert port_running.name is not None

        # Clean up
        port_client.delete_port(name=port_running.name)

        # Terminate the engine
        sandbox_engine_client_super_admin.terminate_sandbox_engine(name=engine.name)

        # Wait a bit for state to update to TERMINATING
        import time
        time.sleep(2)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)

        # Port operations should fail when engine is TERMINATING or TERMINATED
        if engine.state in [
            SandboxEngineState.STATE_TERMINATING,
            SandboxEngineState.STATE_TERMINATED,
        ]:
            with pytest.raises(CustomApiException) as exc:
                port_client.create_port(
                    parent=engine.name,
                    port=Port(
                        display_name="Test Port",
                        public=False,
                    ),
                    port_id="6666",
                )
            assert exc.value.status == http.HTTPStatus.BAD_REQUEST
            assert "starting or running" in str(exc.value).lower()

    finally:
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_port_operations_validate_resource_name_format(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_port_validation_test,
    sandbox_engine_image_port_validation_test,
):
    """Test that port operations validate resource name format."""
    workspace_id = "default"
    engine_id = f"sandbox-port-validation-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_port_validation_test.name,
            sandbox_engine_image=sandbox_engine_image_port_validation_test.name,
            display_name="Port Validation Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        port_client = super_admin_clients.sandbox_clients.port_client

        # Test with invalid parent resource name (missing workspaces/ prefix)
        with pytest.raises(ApiValueError) as exc:
            port_client.create_port(
                parent="invalid-parent-name",
                port=Port(
                    display_name="Test Port",
                    public=False,
                ),
                port_id="1234",
            )
        assert "must match regular expression" in str(exc.value)

        # Test with invalid parent resource name (wrong format)
        with pytest.raises(ApiValueError) as exc:
            port_client.create_port(
                parent="workspaces/default",  # Missing sandboxEngines/ part
                port=Port(
                    display_name="Test Port",
                    public=False,
                ),
                port_id="1234",
            )
        assert "must match regular expression" in str(exc.value)

        # Test with valid parent resource name should succeed
        port = port_client.create_port(
            parent=engine.name,
            port=Port(
                display_name="Valid Port",
                public=False,
            ),
            port_id="4321",
        )

        assert port.name is not None
        port_client.delete_port(name=port.name)

    finally:
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_port_operations_on_nonexistent_engine(
    super_admin_clients,
):
    """Test that port operations fail gracefully on non-existent engine."""
    port_client = super_admin_clients.sandbox_clients.port_client

    # Use a properly formatted but non-existent engine name
    nonexistent_engine_name = (
        f"workspaces/default/sandboxEngines/nonexistent-{uuid.uuid4().hex[:8]}"
    )

    # Test create_port on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        port_client.create_port(
            parent=nonexistent_engine_name,
            port=Port(
                display_name="Test Port",
                public=False,
            ),
            port_id="1111",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test list_ports on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        port_client.list_ports(parent=nonexistent_engine_name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Use a properly formatted but non-existent port name
    nonexistent_port_name = f"{nonexistent_engine_name}/ports/9999"

    # Test get_port on non-existent port
    with pytest.raises(CustomApiException) as exc:
        port_client.get_port(name=nonexistent_port_name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test delete_port on non-existent port
    with pytest.raises(CustomApiException) as exc:
        port_client.delete_port(name=nonexistent_port_name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


@pytest.mark.timeout(300)
def test_port_id_must_be_valid_port_number(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_port_num_validation_test,
    sandbox_engine_image_port_num_validation_test,
):
    """Test that port_id must be a valid port number (1024-65535)."""
    workspace_id = "default"
    engine_id = f"sandbox-port-num-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_port_num_validation_test.name,
            sandbox_engine_image=sandbox_engine_image_port_num_validation_test.name,
            display_name="Port Number Validation Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        port_client = super_admin_clients.sandbox_clients.port_client

        # Test with port number below valid range (< 1024)
        with pytest.raises(CustomApiException) as exc:
            port_client.create_port(
                parent=engine.name,
                port=Port(display_name="Low Port", public=False),
                port_id="80",
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST

        # Test with port number above valid range (> 65535)
        with pytest.raises(CustomApiException) as exc:
            port_client.create_port(
                parent=engine.name,
                port=Port(display_name="High Port", public=False),
                port_id="70000",
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST

        # Test with non-numeric port_id
        with pytest.raises(CustomApiException) as exc:
            port_client.create_port(
                parent=engine.name,
                port=Port(display_name="Invalid Port", public=False),
                port_id="not-a-number",
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST

        # Test with valid port number should succeed
        port = port_client.create_port(
            parent=engine.name,
            port=Port(display_name="Valid Port", public=False),
            port_id="8080",
        )

        assert port.name is not None
        port_client.delete_port(name=port.name)

    finally:
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")
