import http
import uuid

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState
from h2o_engine_manager.gen.exceptions import ApiValueError


@pytest.mark.timeout(300)
def test_h2o_drive_operations_require_creator_authentication(
    super_admin_clients,
    clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_drive_auth_test,
    sandbox_engine_image_drive_auth_test,
):
    """Test that only the creator can perform H2O Drive operations on a sandbox engine."""
    workspace_id = "default"
    engine_id = f"sandbox-drive-auth-{uuid.uuid4().hex[:8]}"

    # Super admin (creator) creates a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_drive_auth_test.name,
            sandbox_engine_image=sandbox_engine_image_drive_auth_test.name,
            display_name="Drive Auth Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get clients
        h2o_drive_client_super_admin = super_admin_clients.sandbox_clients.h2o_drive_client
        h2o_drive_client_basic = clients.sandbox_clients.h2o_drive_client
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Creator (super admin) should be able to write a file first
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/test_file.txt",
            content=b"Test content for drive upload",
            create_parent_directories=True,
        )

        # Non-creator (basic user) should NOT be able to upload a file
        with pytest.raises(CustomApiException) as exc:
            h2o_drive_client_basic.upload_file(
                name=engine.name,
                local_path="/workspace/test_file.txt",
                remote_path="test/uploaded_file.txt",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to download a file
        with pytest.raises(CustomApiException) as exc:
            h2o_drive_client_basic.download_file(
                name=engine.name,
                remote_path="test/some_file.txt",
                local_path="/workspace/downloaded_file.txt",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Creator (super admin) should be able to upload a file
        upload_response = h2o_drive_client_super_admin.upload_file(
            name=engine.name,
            local_path="/workspace/test_file.txt",
            remote_path="test/uploaded_file.txt",
        )
        assert upload_response.bytes_uploaded > 0

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_h2o_drive_operations_require_running_state(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_drive_state_test,
    sandbox_engine_image_drive_state_test,
):
    """Test that H2O Drive operations fail when engine is not in RUNNING state."""
    workspace_id = "default"
    engine_id = f"sandbox-drive-state-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_drive_state_test.name,
            sandbox_engine_image=sandbox_engine_image_drive_state_test.name,
            display_name="Drive State Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Engine is in STARTING state - H2O Drive operations should fail
        assert engine.state == SandboxEngineState.STATE_STARTING

        h2o_drive_client = super_admin_clients.sandbox_clients.h2o_drive_client

        # Test that upload_file fails when engine is STARTING
        with pytest.raises(CustomApiException) as exc:
            h2o_drive_client.upload_file(
                name=engine.name,
                local_path="/workspace/test.txt",
                remote_path="test/uploaded.txt",
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST
        assert "not in running state" in str(exc.value).lower()

        # Test that download_file fails when engine is STARTING
        with pytest.raises(CustomApiException) as exc:
            h2o_drive_client.download_file(
                name=engine.name,
                remote_path="test/file.txt",
                local_path="/workspace/downloaded.txt",
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST
        assert "not in running state" in str(exc.value).lower()

        # Wait for engine to be RUNNING
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Now H2O Drive operations should work (assuming Drive is configured)
        # Write a test file first
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/running_state_test.txt",
            content=b"Engine is now running",
            create_parent_directories=True,
        )

        # Upload should succeed now
        upload_response = h2o_drive_client.upload_file(
            name=engine.name,
            local_path="/workspace/running_state_test.txt",
            remote_path="test/running_state_test.txt",
        )
        assert upload_response.bytes_uploaded > 0

        # Terminate the engine
        sandbox_engine_client_super_admin.terminate_sandbox_engine(name=engine.name)

        # Wait a bit for state to update to TERMINATING
        import time

        time.sleep(2)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)

        # H2O Drive operations should fail when engine is TERMINATING or TERMINATED
        if engine.state in [
            SandboxEngineState.STATE_TERMINATING,
            SandboxEngineState.STATE_TERMINATED,
        ]:
            with pytest.raises(CustomApiException) as exc:
                h2o_drive_client.upload_file(
                    name=engine.name,
                    local_path="/workspace/test.txt",
                    remote_path="test/file.txt",
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
def test_h2o_drive_operations_validate_resource_name_format(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_drive_validation_test,
    sandbox_engine_image_drive_validation_test,
):
    """Test that H2O Drive operations validate resource name format."""
    workspace_id = "default"
    engine_id = f"sandbox-drive-validation-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_drive_validation_test.name,
            sandbox_engine_image=sandbox_engine_image_drive_validation_test.name,
            display_name="Drive Validation Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        h2o_drive_client = super_admin_clients.sandbox_clients.h2o_drive_client

        # Test with invalid resource name (missing workspaces/ prefix)
        with pytest.raises(ApiValueError) as exc:
            h2o_drive_client.upload_file(
                name="invalid-resource-name",
                local_path="/workspace/test.txt",
                remote_path="test/file.txt",
            )
        assert "must match regular expression" in str(exc.value)

        # Test with invalid resource name (wrong format)
        with pytest.raises(ApiValueError) as exc:
            h2o_drive_client.download_file(
                name="workspaces/default",  # Missing sandboxEngines/ part
                remote_path="test/file.txt",
                local_path="/workspace/test.txt",
            )
        assert "must match regular expression" in str(exc.value)

        # Test with empty resource name
        with pytest.raises(ApiValueError) as exc:
            h2o_drive_client.upload_file(
                name="",
                local_path="/workspace/test.txt",
                remote_path="test/file.txt",
            )
        assert "must match regular expression" in str(exc.value)

        # Test with valid resource name should succeed
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/valid_resource_test.txt",
            content=b"Valid resource name test",
            create_parent_directories=True,
        )

        upload_response = h2o_drive_client.upload_file(
            name=engine.name,
            local_path="/workspace/valid_resource_test.txt",
            remote_path="test/valid_resource_test.txt",
        )
        assert upload_response.bytes_uploaded > 0

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(60)
def test_h2o_drive_operations_on_nonexistent_engine(
    super_admin_clients,
):
    """Test that H2O Drive operations fail gracefully on non-existent engine."""
    h2o_drive_client = super_admin_clients.sandbox_clients.h2o_drive_client

    # Use a properly formatted but non-existent engine name
    nonexistent_engine_name = (
        f"workspaces/default/sandboxEngines/nonexistent-{uuid.uuid4().hex[:8]}"
    )

    # Test upload_file on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        h2o_drive_client.upload_file(
            name=nonexistent_engine_name,
            local_path="/workspace/test.txt",
            remote_path="test/file.txt",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test download_file on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        h2o_drive_client.download_file(
            name=nonexistent_engine_name,
            remote_path="test/file.txt",
            local_path="/workspace/test.txt",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
