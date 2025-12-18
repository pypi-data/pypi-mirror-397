import http
import uuid

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox.filesystem.file_type import FileType
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState


@pytest.mark.timeout(300)
def test_write_and_read_file(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_test1,
    sandbox_engine_image_fs_test1,
):
    """Test writing and reading files in a sandbox engine filesystem."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-test-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_test1.name,
            sandbox_engine_image=sandbox_engine_image_fs_test1.name,
            display_name="Filesystem Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    assert engine.state == SandboxEngineState.STATE_STARTING

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the filesystem client from the super_admin_clients
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Test WriteFile: Write a test file with some content
        test_content = b"Hello from filesystem E2E test!\nThis is a test file.\nLine 3."
        write_response = filesystem_client.write_file(
            name=engine.name,
            path="/workspace/test_file.txt",
            content=test_content,
            create_parent_directories=True,
        )

        # Verify write response contains file info
        assert write_response.file_info is not None
        assert write_response.file_info.path == "/workspace/test_file.txt"
        assert write_response.file_info.size == len(test_content)
        assert write_response.file_info.type == FileType.FILE_TYPE_REGULAR
        assert write_response.file_info.mode is not None

        # Test ReadFile: Read back the file we just wrote
        read_response = filesystem_client.read_file(
            name=engine.name,
            path="/workspace/test_file.txt",
        )

        # Verify read response contains the correct content and file info
        assert read_response.content == test_content
        assert read_response.file_info is not None
        assert read_response.file_info.path == "/workspace/test_file.txt"
        assert read_response.file_info.size == len(test_content)
        assert read_response.file_info.type == FileType.FILE_TYPE_REGULAR

        # Test WriteFile: Overwrite the file with new content
        new_content = b"Updated content for the test file."
        write_response2 = filesystem_client.write_file(
            name=engine.name,
            path="/workspace/test_file.txt",
            content=new_content,
            overwrite=True,
        )

        assert write_response2.file_info.path == "/workspace/test_file.txt"
        assert write_response2.file_info.size == len(new_content)

        # Test ReadFile: Verify the file was overwritten
        read_response2 = filesystem_client.read_file(
            name=engine.name,
            path="/workspace/test_file.txt",
        )

        assert read_response2.content == new_content
        assert read_response2.file_info.size == len(new_content)

        # Test WriteFile: Write a file in a subdirectory
        subdir_content = b"File in subdirectory"
        write_response3 = filesystem_client.write_file(
            name=engine.name,
            path="/workspace/data/subfile.txt",
            content=subdir_content,
            create_parent_directories=True,
        )

        assert write_response3.file_info.path == "/workspace/data/subfile.txt"
        assert write_response3.file_info.size == len(subdir_content)

        # Test ReadFile: Read file from subdirectory
        read_response3 = filesystem_client.read_file(
            name=engine.name,
            path="/workspace/data/subfile.txt",
        )

        assert read_response3.content == subdir_content

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            # Log cleanup error but don't fail the test if cleanup fails
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_read_nonexistent_file(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_test2,
    sandbox_engine_image_fs_test2,
):
    """Test reading a file that doesn't exist returns an error."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-err-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_test2.name,
            sandbox_engine_image=sandbox_engine_image_fs_test2.name,
            display_name="Filesystem Error Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the filesystem client
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Try to read a file that doesn't exist
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.read_file(
                name=engine.name,
                path="/workspace/nonexistent_file.txt",
            )

        # Verify we got a NOT_FOUND error
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            # Log cleanup error but don't fail the test if cleanup fails
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_write_without_parent_directories_fails(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_test3,
    sandbox_engine_image_fs_test3,
):
    """Test writing to a path without creating parent directories fails."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-fail-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_test3.name,
            sandbox_engine_image=sandbox_engine_image_fs_test3.name,
            display_name="Filesystem Fail Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the filesystem client
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Try to write to a path where parent directories don't exist
        # and create_parent_directories is False
        with pytest.raises(CustomApiException):
            filesystem_client.write_file(
                name=engine.name,
                path="/workspace/deep/nested/path/file.txt",
                content=b"This should fail",
                create_parent_directories=False,
            )

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            # Log cleanup error but don't fail the test if cleanup fails
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_make_directory(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_test4,
    sandbox_engine_image_fs_test4,
):
    """Test creating directories in a sandbox engine filesystem."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-mkdir-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_test4.name,
            sandbox_engine_image=sandbox_engine_image_fs_test4.name,
            display_name="MakeDirectory Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the filesystem client
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Test MakeDirectory: Create a simple directory
        mkdir_response = filesystem_client.make_directory(
            name=engine.name,
            path="/workspace/test_dir",
            create_parent_directories=True,
        )

        # Verify response contains file info for the created directory
        assert mkdir_response is not None
        assert mkdir_response.path == "/workspace/test_dir"
        assert mkdir_response.type == FileType.FILE_TYPE_DIRECTORY
        assert mkdir_response.mode is not None

        # Test MakeDirectory: Create nested directories with create_parent_directories
        nested_mkdir_response = filesystem_client.make_directory(
            name=engine.name,
            path="/workspace/deep/nested/path",
            create_parent_directories=True,
        )

        assert nested_mkdir_response is not None
        assert nested_mkdir_response.path == "/workspace/deep/nested/path"
        assert nested_mkdir_response.type == FileType.FILE_TYPE_DIRECTORY

        # Test that directory exists by writing a file inside it
        test_content = b"File in nested directory"
        write_response = filesystem_client.write_file(
            name=engine.name,
            path="/workspace/deep/nested/path/test.txt",
            content=test_content,
        )

        assert write_response.file_info.path == "/workspace/deep/nested/path/test.txt"

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_list_directory(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_test5,
    sandbox_engine_image_fs_test5,
):
    """Test listing directory contents in a sandbox engine filesystem."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-ls-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_test5.name,
            sandbox_engine_image=sandbox_engine_image_fs_test5.name,
            display_name="ListDirectory Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the filesystem client
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Create some test files and directories
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/file1.txt",
            content=b"File 1 content",
            create_parent_directories=True,
        )
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/file2.txt",
            content=b"File 2 content",
            create_parent_directories=True,
        )
        filesystem_client.make_directory(
            name=engine.name,
            path="/workspace/subdir",
            create_parent_directories=True,
        )
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/subdir/nested_file.txt",
            content=b"Nested file content",
        )

        # Test ListDirectory: List the workspace directory
        files = filesystem_client.list_directory(
            name=engine.name,
            path="/workspace",
        )

        # Verify response contains the files and directory we created
        assert files is not None
        assert len(files) >= 3  # file1.txt, file2.txt, subdir

        # Check that the files are present
        file_paths = {f.path for f in files}
        assert "/workspace/file1.txt" in file_paths
        assert "/workspace/file2.txt" in file_paths
        assert "/workspace/subdir" in file_paths

        # Check file types
        for file_info in files:
            if file_info.path in ["/workspace/file1.txt", "/workspace/file2.txt"]:
                assert file_info.type == FileType.FILE_TYPE_REGULAR
                assert file_info.size > 0
            elif file_info.path == "/workspace/subdir":
                assert file_info.type == FileType.FILE_TYPE_DIRECTORY

        # Test ListDirectory: List subdirectory
        subdir_files = filesystem_client.list_directory(
            name=engine.name,
            path="/workspace/subdir",
        )

        assert subdir_files is not None
        assert len(subdir_files) == 1
        assert subdir_files[0].path == "/workspace/subdir/nested_file.txt"
        assert subdir_files[0].type == FileType.FILE_TYPE_REGULAR

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_stat_file(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_test6,
    sandbox_engine_image_fs_test6,
):
    """Test getting file metadata in a sandbox engine filesystem."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-stat-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_test6.name,
            sandbox_engine_image=sandbox_engine_image_fs_test6.name,
            display_name="StatFile Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the filesystem client
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Create a test file
        test_content = b"Test file for stat operation"
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/stat_test.txt",
            content=test_content,
            create_parent_directories=True,
        )

        # Test StatFile: Get metadata for the file
        stat_response = filesystem_client.stat_file(
            name=engine.name,
            path="/workspace/stat_test.txt",
        )

        # Verify response contains file info
        assert stat_response is not None
        assert stat_response.path == "/workspace/stat_test.txt"
        assert stat_response.size == len(test_content)
        assert stat_response.type == FileType.FILE_TYPE_REGULAR
        assert stat_response.mode is not None
        assert stat_response.modify_time is not None

        # Create a directory and get its metadata
        filesystem_client.make_directory(
            name=engine.name,
            path="/workspace/stat_dir",
            create_parent_directories=True,
        )

        # Test StatFile: Get metadata for the directory
        dir_stat_response = filesystem_client.stat_file(
            name=engine.name,
            path="/workspace/stat_dir",
        )

        assert dir_stat_response is not None
        assert dir_stat_response.path == "/workspace/stat_dir"
        assert dir_stat_response.type == FileType.FILE_TYPE_DIRECTORY
        assert dir_stat_response.mode is not None
        assert dir_stat_response.modify_time is not None

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_move_file(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_test7,
    sandbox_engine_image_fs_test7,
):
    """Test moving and renaming files in a sandbox engine filesystem."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-mv-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_test7.name,
            sandbox_engine_image=sandbox_engine_image_fs_test7.name,
            display_name="Move Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the filesystem client
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Create a test file
        test_content = b"File to be moved"
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/original.txt",
            content=test_content,
            create_parent_directories=True,
        )

        # Test Move: Rename a file
        move_response = filesystem_client.move(
            name=engine.name,
            source_path="/workspace/original.txt",
            destination_path="/workspace/renamed.txt",
        )

        # Verify move response
        assert move_response is not None
        assert move_response.path == "/workspace/renamed.txt"
        assert move_response.type == FileType.FILE_TYPE_REGULAR
        assert move_response.size == len(test_content)

        # Verify the file exists at the new location
        read_response = filesystem_client.read_file(
            name=engine.name,
            path="/workspace/renamed.txt",
        )
        assert read_response.content == test_content

        # Verify the original file no longer exists
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.read_file(
                name=engine.name,
                path="/workspace/original.txt",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Test Move: Move to a different directory
        filesystem_client.make_directory(
            name=engine.name,
            path="/workspace/target_dir",
            create_parent_directories=True,
        )

        move_response2 = filesystem_client.move(
            name=engine.name,
            source_path="/workspace/renamed.txt",
            destination_path="/workspace/target_dir/moved.txt",
        )

        assert move_response2.path == "/workspace/target_dir/moved.txt"

        # Verify the file exists in the new location
        read_response2 = filesystem_client.read_file(
            name=engine.name,
            path="/workspace/target_dir/moved.txt",
        )
        assert read_response2.content == test_content

        # Test Move: Move with overwrite
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/file_to_overwrite.txt",
            content=b"This will be overwritten",
            create_parent_directories=True,
        )

        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/source_file.txt",
            content=b"Source content",
            create_parent_directories=True,
        )

        move_response3 = filesystem_client.move(
            name=engine.name,
            source_path="/workspace/source_file.txt",
            destination_path="/workspace/file_to_overwrite.txt",
            overwrite=True,
        )

        assert move_response3.path == "/workspace/file_to_overwrite.txt"

        # Verify the file was overwritten
        read_response3 = filesystem_client.read_file(
            name=engine.name,
            path="/workspace/file_to_overwrite.txt",
        )
        assert read_response3.content == b"Source content"

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_remove_file_and_directory(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_fs_test8,
    sandbox_engine_image_fs_test8,
):
    """Test removing files and directories in a sandbox engine filesystem."""
    workspace_id = "default"
    engine_id = f"sandbox-fs-rm-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_fs_test8.name,
            sandbox_engine_image=sandbox_engine_image_fs_test8.name,
            display_name="Remove Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the filesystem client
        filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

        # Create a test file
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/file_to_remove.txt",
            content=b"File to be removed",
            create_parent_directories=True,
        )

        # Verify the file exists
        read_response = filesystem_client.read_file(
            name=engine.name,
            path="/workspace/file_to_remove.txt",
        )
        assert read_response.content == b"File to be removed"

        # Test Remove: Delete the file
        filesystem_client.remove(
            name=engine.name,
            path="/workspace/file_to_remove.txt",
        )

        # Verify the file no longer exists
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.read_file(
                name=engine.name,
                path="/workspace/file_to_remove.txt",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Test Remove: Delete an empty directory
        filesystem_client.make_directory(
            name=engine.name,
            path="/workspace/empty_dir",
            create_parent_directories=True,
        )

        filesystem_client.remove(
            name=engine.name,
            path="/workspace/empty_dir",
        )

        # Verify the directory no longer exists (stat should fail)
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.stat_file(
                name=engine.name,
                path="/workspace/empty_dir",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

        # Test Remove: Delete a directory recursively
        filesystem_client.make_directory(
            name=engine.name,
            path="/workspace/dir_with_contents/subdir",
            create_parent_directories=True,
        )
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/dir_with_contents/file1.txt",
            content=b"File 1",
        )
        filesystem_client.write_file(
            name=engine.name,
            path="/workspace/dir_with_contents/subdir/file2.txt",
            content=b"File 2",
        )

        # Remove the directory recursively
        filesystem_client.remove(
            name=engine.name,
            path="/workspace/dir_with_contents",
            recursive=True,
        )

        # Verify the directory and its contents no longer exist
        with pytest.raises(CustomApiException) as exc:
            filesystem_client.stat_file(
                name=engine.name,
                path="/workspace/dir_with_contents",
            )
        assert exc.value.status == http.HTTPStatus.NOT_FOUND

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")