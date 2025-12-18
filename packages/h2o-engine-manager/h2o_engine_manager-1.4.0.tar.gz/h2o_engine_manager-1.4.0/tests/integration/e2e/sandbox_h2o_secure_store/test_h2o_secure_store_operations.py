import uuid

import pytest
from h2o_secure_store.clients.secret_version.secret_version import SecretVersion

from h2o_engine_manager.clients.sandbox.filesystem.file_type import FileType
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState


@pytest.mark.timeout(300)
def test_reveal_secret_to_file(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_secure_store_test1,
    sandbox_engine_image_secure_store_test1,
    secure_store_secret_client,
    secure_store_secret_version_client,
):
    """Test revealing a secret and writing it to a file in sandbox engine filesystem."""
    workspace_id = "default"
    engine_id = f"sandbox-ss-test-{uuid.uuid4().hex[:8]}"
    secret_id = f"test-secret-{uuid.uuid4().hex[:8]}"
    secret_value = b"my-super-secret-api-key-12345"

    # Create a secret in the secure store
    secret = secure_store_secret_client.create_secret(
        parent=f"workspaces/{workspace_id}",
        secret_id=secret_id,
        display_name="Test Secret for Reveal",
    )

    # Create a secret version with the actual value
    secret_version = secure_store_secret_version_client.create_secret_version(
        parent=secret.name,
        secret_version=SecretVersion(value=secret_value),
    )

    try:
        # Create a sandbox engine
        engine = sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_secure_store_test1.name,
                sandbox_engine_image=sandbox_engine_image_secure_store_test1.name,
                display_name="Secure Store Test Engine",
            ),
            sandbox_engine_id=engine_id,
        )

        assert engine.state == SandboxEngineState.STATE_STARTING

        try:
            # Wait for the sandbox engine to be running
            sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
            engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
            assert engine.state == SandboxEngineState.STATE_RUNNING

            # Get the secure store client and filesystem client
            h2o_secure_store_client = super_admin_clients.sandbox_clients.h2o_secure_store_client
            filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

            # Test RevealSecretToFile: Reveal a secret and write it to a file
            target_path = "/workspace/credentials/secret.txt"

            response = h2o_secure_store_client.reveal_secret_to_file(
                name=engine.name,
                secret_version=f"{secret.name}/versions/latest",
                path=target_path,
            )

            # Verify response contains the secret version name
            assert response.secret_version is not None
            assert secret_id in response.secret_version

            # Verify file info is returned
            assert response.file_info is not None
            assert response.file_info.path == target_path
            assert response.file_info.type == FileType.FILE_TYPE_REGULAR
            assert response.file_info.size == len(secret_value)

            # Verify the file was actually created by reading it
            read_response = filesystem_client.read_file(
                name=engine.name,
                path=target_path,
            )

            # The file should contain the secret value
            assert read_response.content == secret_value

        finally:
            # Clean up: Delete the sandbox engine
            try:
                sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
            except Exception as cleanup_error:
                print(f"Cleanup error: {cleanup_error}")

    finally:
        # Clean up: Delete the secret
        try:
            secure_store_secret_client.delete_secret(name=secret.name)
        except Exception as cleanup_error:
            print(f"Secret cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_reveal_secret_creates_parent_directories(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_secure_store_test2,
    sandbox_engine_image_secure_store_test2,
    secure_store_secret_client,
    secure_store_secret_version_client,
):
    """Test that revealing a secret creates parent directories automatically."""
    workspace_id = "default"
    engine_id = f"sandbox-ss-dir-{uuid.uuid4().hex[:8]}"
    secret_id = f"test-secret-dir-{uuid.uuid4().hex[:8]}"
    secret_value = b"nested-directory-secret-value"

    # Create a secret in the secure store
    secret = secure_store_secret_client.create_secret(
        parent=f"workspaces/{workspace_id}",
        secret_id=secret_id,
        display_name="Test Secret for Nested Dir",
    )

    # Create a secret version with the actual value
    secure_store_secret_version_client.create_secret_version(
        parent=secret.name,
        secret_version=SecretVersion(value=secret_value),
    )

    try:
        # Create a sandbox engine
        engine = sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_secure_store_test2.name,
                sandbox_engine_image=sandbox_engine_image_secure_store_test2.name,
                display_name="Secure Store Dir Test Engine",
            ),
            sandbox_engine_id=engine_id,
        )

        try:
            # Wait for the sandbox engine to be running
            sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
            engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
            assert engine.state == SandboxEngineState.STATE_RUNNING

            # Get the secure store client
            h2o_secure_store_client = super_admin_clients.sandbox_clients.h2o_secure_store_client

            # Test with deeply nested path - parent directories should be created automatically
            deeply_nested_path = "/workspace/deep/nested/directory/structure/secret.txt"

            response = h2o_secure_store_client.reveal_secret_to_file(
                name=engine.name,
                secret_version=f"{secret.name}/versions/latest",
                path=deeply_nested_path,
            )

            # Verify the file was created at the nested path
            assert response.file_info is not None
            assert response.file_info.path == deeply_nested_path
            assert response.file_info.type == FileType.FILE_TYPE_REGULAR
            assert response.file_info.size == len(secret_value)

        finally:
            # Clean up: Delete the sandbox engine
            try:
                sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
            except Exception as cleanup_error:
                print(f"Cleanup error: {cleanup_error}")

    finally:
        # Clean up: Delete the secret
        try:
            secure_store_secret_client.delete_secret(name=secret.name)
        except Exception as cleanup_error:
            print(f"Secret cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_reveal_secret_overwrites_existing_file(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_secure_store_test3,
    sandbox_engine_image_secure_store_test3,
    secure_store_secret_client,
    secure_store_secret_version_client,
):
    """Test that revealing a secret overwrites an existing file."""
    workspace_id = "default"
    engine_id = f"sandbox-ss-overwrite-{uuid.uuid4().hex[:8]}"
    secret_id = f"test-secret-overwrite-{uuid.uuid4().hex[:8]}"
    secret_value = b"this-is-the-secret-value-that-overwrites"

    # Create a secret in the secure store
    secret = secure_store_secret_client.create_secret(
        parent=f"workspaces/{workspace_id}",
        secret_id=secret_id,
        display_name="Test Secret for Overwrite",
    )

    # Create a secret version with the actual value
    secure_store_secret_version_client.create_secret_version(
        parent=secret.name,
        secret_version=SecretVersion(value=secret_value),
    )

    try:
        # Create a sandbox engine
        engine = sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_secure_store_test3.name,
                sandbox_engine_image=sandbox_engine_image_secure_store_test3.name,
                display_name="Secure Store Overwrite Test Engine",
            ),
            sandbox_engine_id=engine_id,
        )

        try:
            # Wait for the sandbox engine to be running
            sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
            engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
            assert engine.state == SandboxEngineState.STATE_RUNNING

            # Get the clients
            h2o_secure_store_client = super_admin_clients.sandbox_clients.h2o_secure_store_client
            filesystem_client = super_admin_clients.sandbox_clients.filesystem_client

            target_path = "/workspace/secret_file.txt"

            # First, create a file with some initial content
            initial_content = b"This is the original content that should be overwritten"
            filesystem_client.write_file(
                name=engine.name,
                path=target_path,
                content=initial_content,
                create_parent_directories=True,
            )

            # Verify the initial file exists
            read_response1 = filesystem_client.read_file(
                name=engine.name,
                path=target_path,
            )
            assert read_response1.content == initial_content

            # Now reveal a secret to the same path - should overwrite
            response = h2o_secure_store_client.reveal_secret_to_file(
                name=engine.name,
                secret_version=f"{secret.name}/versions/latest",
                path=target_path,
            )

            # Verify the file was overwritten
            assert response.file_info is not None
            assert response.file_info.path == target_path
            assert response.file_info.size == len(secret_value)

            # Read the file again - content should be the secret value
            read_response2 = filesystem_client.read_file(
                name=engine.name,
                path=target_path,
            )

            # The content should be the secret value, not the original content
            assert read_response2.content == secret_value
            assert read_response2.content != initial_content

        finally:
            # Clean up: Delete the sandbox engine
            try:
                sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
            except Exception as cleanup_error:
                print(f"Cleanup error: {cleanup_error}")

    finally:
        # Clean up: Delete the secret
        try:
            secure_store_secret_client.delete_secret(name=secret.name)
        except Exception as cleanup_error:
            print(f"Secret cleanup error: {cleanup_error}")
