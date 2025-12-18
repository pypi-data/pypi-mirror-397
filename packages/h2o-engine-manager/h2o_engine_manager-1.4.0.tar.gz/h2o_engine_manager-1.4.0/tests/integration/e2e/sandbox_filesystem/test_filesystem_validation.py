import http
import uuid

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState
from h2o_engine_manager.gen.exceptions import ApiValueError


@pytest.mark.timeout(300)
def test_filesystem_operations_require_creator_authentication(
    filesystem_client,
    filesystem_client_super_admin,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_auth_test,
    sandbox_engine_image_fs_auth_test,
):
    """Test that only the creator can perform filesystem operations on a sandbox engine."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-auth-{uuid.uuid4().hex[:8]}"

    # Super admin (creator) creates a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_auth_test.name,
            sandbox_engine_image=sandbox_engine_image_fs_auth_test.name,
            display_name="Filesystem Auth Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Creator (super admin) should be able to write a file
        filesystem_client_super_admin.write_file(
            name=engine.name,
            path="/workspace/creator_file.txt",
            content=b"Created by super admin",
            create_parent_directories=True,
        )

        # Non-creator (basic user) should NOT be able to read the file
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.read_file(
                name=engine.name,
                path="/workspace/creator_file.txt",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to write a file
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.write_file(
                name=engine.name,
                path="/workspace/basic_user_file.txt",
                content=b"Created by basic user",
                create_parent_directories=True,
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to list directory
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.list_directory(
                name=engine.name,
                path="/workspace",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to stat file
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.stat_file(
                name=engine.name,
                path="/workspace/creator_file.txt",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to make directory
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.make_directory(
                name=engine.name,
                path="/workspace/basic_user_dir",
                create_parent_directories=True,
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to move file
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.move(
                name=engine.name,
                source_path="/workspace/creator_file.txt",
                destination_path="/workspace/moved_file.txt",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Non-creator (basic user) should NOT be able to remove file
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.remove(
                name=engine.name,
                path="/workspace/creator_file.txt",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Verify creator (super admin) can still read the file
        read_response = filesystem_client_super_admin.read_file(
            name=engine.name,
            path="/workspace/creator_file.txt",
        )
        assert read_response.content == b"Created by super admin"

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_filesystem_operations_require_running_state(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_state_test,
    sandbox_engine_image_fs_state_test,
):
    """Test that filesystem operations fail when engine is not in RUNNING state."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-state-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_state_test.name,
            sandbox_engine_image=sandbox_engine_image_fs_state_test.name,
            display_name="Filesystem State Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Engine is in STARTING state - filesystem operations should fail
        assert engine.state == SandboxEngineState.STATE_STARTING

        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Test that read_file fails when engine is STARTING
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.read_file(
                name=engine.name,
                path="/workspace/test.txt",
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST
        assert "not in running state" in str(exc.value).lower()

        # Test that write_file fails when engine is STARTING
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.write_file(
                name=engine.name,
                path="/workspace/test.txt",
                content=b"Test content",
                create_parent_directories=True,
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST
        assert "not in running state" in str(exc.value).lower()

        # Test that list_directory fails when engine is STARTING
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.list_directory(
                name=engine.name,
                path="/workspace",
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST
        assert "not in running state" in str(exc.value).lower()

        # Test that stat_file fails when engine is STARTING
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.stat_file(
                name=engine.name,
                path="/workspace/test.txt",
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST
        assert "not in running state" in str(exc.value).lower()

        # Test that make_directory fails when engine is STARTING
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.make_directory(
                name=engine.name,
                path="/workspace/test_dir",
                create_parent_directories=True,
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST
        assert "not in running state" in str(exc.value).lower()

        # Test that move fails when engine is STARTING
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.move(
                name=engine.name,
                source_path="/workspace/source.txt",
                destination_path="/workspace/dest.txt",
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST
        assert "not in running state" in str(exc.value).lower()

        # Test that remove fails when engine is STARTING
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.remove(
                name=engine.name,
                path="/workspace/test.txt",
            )
        assert exc.value.status == http.HTTPStatus.BAD_REQUEST
        assert "not in running state" in str(exc.value).lower()

        # Wait for engine to be RUNNING
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Now filesystem operations should succeed
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/running_state_test.txt",
            content=b"Engine is now running",
            create_parent_directories=True,
        )

        read_response = filesystem_client.read_file(
            name=engine.name,
            path="/workspace/running_state_test.txt",
        )
        assert read_response.content == b"Engine is now running"

        # Terminate the engine
        sandbox_engine_client_super_admin.terminate_sandbox_engine(name=engine.name)

        # Wait a bit for state to update to TERMINATING
        import time

        time.sleep(2)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)

        # Filesystem operations should fail when engine is TERMINATING or TERMINATED
        if engine.state in [
            SandboxEngineState.STATE_TERMINATING,
            SandboxEngineState.STATE_TERMINATED,
        ]:
            with pytest.raises(CustomApiException) as exc:
                filesystem_client.read_file(
                    name=engine.name,
                    path="/workspace/running_state_test.txt",
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
def test_filesystem_operations_validate_resource_name_format(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_validation_test,
    sandbox_engine_image_fs_validation_test,
):
    """Test that filesystem operations validate resource name format."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-validation-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_validation_test.name,
            sandbox_engine_image=sandbox_engine_image_fs_validation_test.name,
            display_name="Filesystem Validation Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Test with invalid resource name (missing workspaces/ prefix)
        # This is caught by client-side validation, so we expect ApiValueError
        with pytest.raises(ApiValueError) as exc:
            filesystem_client.read_file(
                name="invalid-resource-name",
                path="/workspace/test.txt",
            )
        assert "must match regular expression" in str(exc.value)

        # Test with invalid resource name (wrong format)
        # This is caught by client-side validation, so we expect ApiValueError
        with pytest.raises(ApiValueError) as exc:
            filesystem_client.write_file(
                name="workspaces/default",  # Missing sandboxEngines/ part
                path="/workspace/test.txt",
                content=b"Test",
            )
        assert "must match regular expression" in str(exc.value)

        # Test with empty resource name
        # This is caught by client-side validation, so we expect ApiValueError
        with pytest.raises(ApiValueError) as exc:
            filesystem_client.list_directory(
                name="",
                path="/workspace",
            )
        assert "must match regular expression" in str(exc.value)

        # Test with valid resource name should succeed
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/valid_resource_test.txt",
            content=b"Valid resource name",
            create_parent_directories=True,
        )

        read_response = filesystem_client.read_file(
            name=engine.name,
            path="/workspace/valid_resource_test.txt",
        )
        assert read_response.content == b"Valid resource name"

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_filesystem_operations_on_nonexistent_engine(
    super_admin_clients,
):
    """Test that filesystem operations fail gracefully on non-existent engine."""
    filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

    # Use a properly formatted but non-existent engine name
    nonexistent_engine_name = (
        f"workspaces/default/sandboxEngines/nonexistent-{uuid.uuid4().hex[:8]}"
    )

    # Test read_file on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        filesystem_client.read_file(
            name=nonexistent_engine_name,
            path="/workspace/test.txt",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test write_file on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        filesystem_client.write_file(
            name=nonexistent_engine_name,
            path="/workspace/test.txt",
            content=b"Test content",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test list_directory on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        filesystem_client.list_directory(
            name=nonexistent_engine_name,
            path="/workspace",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test stat_file on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        filesystem_client.stat_file(
            name=nonexistent_engine_name,
            path="/workspace/test.txt",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test make_directory on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        filesystem_client.make_directory(
            name=nonexistent_engine_name,
            path="/workspace/test_dir",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test move on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        filesystem_client.move(
            name=nonexistent_engine_name,
            source_path="/workspace/source.txt",
            destination_path="/workspace/dest.txt",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # Test remove on non-existent engine
    with pytest.raises(CustomApiException) as exc:
        filesystem_client.remove(
            name=nonexistent_engine_name,
            path="/workspace/test.txt",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND