import uuid

import pytest

from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState


@pytest.mark.timeout(600)
def test_upload_download_between_engines(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_drive_test1,
    sandbox_engine_image_drive_test1,
    sandbox_engine_template_drive_test2,
    sandbox_engine_image_drive_test2,
):
    """Test uploading a file from one engine to H2O Drive and downloading it to another engine.

    This test validates the complete H2O Drive workflow:
    1. Create two sandbox engines
    2. Write a file to engine 1's filesystem
    3. Upload the file from engine 1 to H2O Drive
    4. Download the file from H2O Drive to engine 2
    5. Verify the content matches
    """
    workspace_id = "default"
    engine1_id = f"sandbox-drive-src-{uuid.uuid4().hex[:8]}"
    engine2_id = f"sandbox-drive-dst-{uuid.uuid4().hex[:8]}"

    # Create both sandbox engines
    engine1 = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_drive_test1.name,
            sandbox_engine_image=sandbox_engine_image_drive_test1.name,
            display_name="Drive Source Engine",
        ),
        sandbox_engine_id=engine1_id,
    )

    engine2 = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_drive_test2.name,
            sandbox_engine_image=sandbox_engine_image_drive_test2.name,
            display_name="Drive Destination Engine",
        ),
        sandbox_engine_id=engine2_id,
    )

    assert engine1.state == SandboxEngineState.STATE_STARTING
    assert engine2.state == SandboxEngineState.STATE_STARTING

    try:
        # Wait for both engines to be running
        sandbox_engine_client_super_admin.wait(name=engine1.name, timeout_seconds=120)
        sandbox_engine_client_super_admin.wait(name=engine2.name, timeout_seconds=120)

        engine1 = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine1.name)
        engine2 = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine2.name)

        assert engine1.state == SandboxEngineState.STATE_RUNNING
        assert engine2.state == SandboxEngineState.STATE_RUNNING

        # Get the clients
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client
        h2o_drive_client = super_admin_clients.sandbox_clients.h2o_drive_client

        # Step 1: Write a test file to engine 1's filesystem
        test_content = b"Hello from H2O Drive E2E test!\nThis file will travel between engines.\nLine 3 with special chars: \xc2\xa9\xe2\x84\xa2"
        unique_filename = f"drive_test_{uuid.uuid4().hex[:8]}.txt"
        local_path_engine1 = f"/workspace/{unique_filename}"
        remote_path = f"e2e_tests/{unique_filename}"
        local_path_engine2 = f"/workspace/downloaded_{unique_filename}"

        write_response = filesystem_client.write_file(
            name=engine1.name,
            path=local_path_engine1,
            content=test_content,
            create_parent_directories=True,
        )

        assert write_response.file_info is not None
        assert write_response.file_info.path == local_path_engine1
        assert write_response.file_info.size == len(test_content)

        # Step 2: Upload the file from engine 1 to H2O Drive
        upload_response = h2o_drive_client.upload_file(
            name=engine1.name,
            local_path=local_path_engine1,
            remote_path=remote_path,
        )

        assert upload_response.bytes_uploaded == len(test_content)

        # Step 3: Download the file from H2O Drive to engine 2
        download_response = h2o_drive_client.download_file(
            name=engine2.name,
            remote_path=remote_path,
            local_path=local_path_engine2,
            create_parent_directories=True,
        )

        assert download_response.file_info is not None
        assert download_response.file_info.path == local_path_engine2
        assert download_response.file_info.size == len(test_content)

        # Step 4: Read the file from engine 2 and verify content
        read_response = filesystem_client.read_file(
            name=engine2.name,
            path=local_path_engine2,
        )

        assert read_response.content == test_content
        assert read_response.file_info.size == len(test_content)

    finally:
        # Clean up: Delete both sandbox engines
        for engine in [engine1, engine2]:
            try:
                sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
            except Exception as cleanup_error:
                print(f"Cleanup error for {engine.name}: {cleanup_error}")
