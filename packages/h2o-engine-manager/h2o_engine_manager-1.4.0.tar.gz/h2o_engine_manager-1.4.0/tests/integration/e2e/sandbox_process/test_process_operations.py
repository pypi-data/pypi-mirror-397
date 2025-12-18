import http
import uuid

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox.process.process_state import ProcessState
from h2o_engine_manager.clients.sandbox.process.ps import Process
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState


@pytest.mark.timeout(300)
def test_create_and_run_process(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_process_test1,
    sandbox_engine_image_process_test1,
):
    """Test creating and running a process in a sandbox engine."""
    workspace_id = "default"
    engine_id = f"sandbox-proc-test-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_process_test1.name,
            sandbox_engine_image=sandbox_engine_image_process_test1.name,
            display_name="Process Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    assert engine.state == SandboxEngineState.STATE_STARTING

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the process client
        process_client = super_admin_clients.sandbox_clients.process_client

        # Test CreateProcess: Create a simple echo process with auto_run=True
        process = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="echo",
                args=["Hello from process E2E test!"],
            ),
            auto_run=True,
        )

        # Verify process was created and started
        assert process.name is not None
        assert process.command == "echo"
        assert process.args == ["Hello from process E2E test!"]
        assert process.state in [ProcessState.STATE_RUNNING, ProcessState.STATE_SUCCEEDED]

        # Test WaitProcess: Wait for the process to complete
        completed_process = process_client.wait_process(name=process.name)

        # Verify process completed successfully
        assert completed_process.state == ProcessState.STATE_SUCCEEDED
        assert completed_process.exit_code == 0

        # Test ReadOutput: Read the output from the process
        output = process_client.read_output(
            name=process.name,
            output_stream="OUTPUT_STREAM_COMBINED",
        )

        # Verify output contains expected text
        assert b"Hello from process E2E test!" in output

    finally:
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_create_process_with_deferred_execution(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_process_test2,
    sandbox_engine_image_process_test2,
):
    """Test creating a process with deferred execution (auto_run=False) and starting it explicitly."""
    workspace_id = "default"
    engine_id = f"sandbox-proc-defer-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_process_test2.name,
            sandbox_engine_image=sandbox_engine_image_process_test2.name,
            display_name="Process Deferred Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the process client
        process_client = super_admin_clients.sandbox_clients.process_client

        # Test CreateProcess: Create a process with auto_run=False
        process = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="sh",
                args=["-c", "echo 'Deferred process started'"],
            ),
            process_id="deferred-process",
            auto_run=False,
        )

        # Verify process is in PENDING state
        assert process.name is not None
        assert process.state == ProcessState.STATE_PENDING
        assert "deferred-process" in process.name

        # Test StartProcess: Start the process explicitly
        started_process = process_client.start_process(name=process.name)

        # Verify process started
        assert started_process.state in [ProcessState.STATE_RUNNING, ProcessState.STATE_SUCCEEDED]

        # Wait for process to complete
        completed_process = process_client.wait_process(name=process.name)
        assert completed_process.state == ProcessState.STATE_SUCCEEDED
        assert completed_process.exit_code == 0

        # Read output
        output = process_client.read_output(name=process.name)
        assert b"Deferred process started" in output

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_list_processes(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_process_test3,
    sandbox_engine_image_process_test3,
):
    """Test listing processes in a sandbox engine."""
    workspace_id = "default"
    engine_id = f"sandbox-proc-list-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_process_test3.name,
            sandbox_engine_image=sandbox_engine_image_process_test3.name,
            display_name="Process List Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the process client
        process_client = super_admin_clients.sandbox_clients.process_client

        # Create multiple processes
        process1 = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="echo",
                args=["Process 1"],
            ),
            auto_run=True,
        )

        process2 = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="echo",
                args=["Process 2"],
            ),
            auto_run=True,
        )

        process3 = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="echo",
                args=["Process 3"],
            ),
            auto_run=True,
        )

        # Wait for processes to complete
        process_client.wait_process(name=process1.name)
        process_client.wait_process(name=process2.name)
        process_client.wait_process(name=process3.name)

        # Test ListProcesses: List all processes
        processes, next_page_token = process_client.list_processes(
            parent=engine.name,
            page_size=10,
        )

        # Verify we got at least 3 processes
        assert len(processes) >= 3

        # Verify process names are in the list
        process_names = {p.name for p in processes}
        assert process1.name in process_names
        assert process2.name in process_names
        assert process3.name in process_names

        # Verify all processes completed successfully
        for proc in processes:
            if proc.name in [process1.name, process2.name, process3.name]:
                assert proc.state == ProcessState.STATE_SUCCEEDED
                assert proc.exit_code == 0

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_send_signal_to_process(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_process_test4,
    sandbox_engine_image_process_test4,
):
    """Test sending a signal to terminate a running process."""
    workspace_id = "default"
    engine_id = f"sandbox-proc-sig-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_process_test4.name,
            sandbox_engine_image=sandbox_engine_image_process_test4.name,
            display_name="Process Signal Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the process client
        process_client = super_admin_clients.sandbox_clients.process_client

        # Create a long-running process
        process = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="sleep",
                args=["30"],
            ),
            auto_run=True,
        )

        # Verify process is running
        assert process.state == ProcessState.STATE_RUNNING

        # Test SendSignal: Send SIGTERM (signal 15) to terminate the process
        signaled_process = process_client.send_signal(
            name=process.name,
            signal=15,  # SIGTERM
        )

        # Process might still be running or already terminated
        # Just verify the signal was sent (no exception)
        assert signaled_process is not None

        # Wait for the process to terminate
        completed_process = process_client.wait_process(name=process.name)

        # Verify process terminated (might be SUCCEEDED or FAILED depending on timing)
        assert completed_process.state in [ProcessState.STATE_SUCCEEDED, ProcessState.STATE_FAILED]

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_process_with_environment_variables(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_process_test5,
    sandbox_engine_image_process_test5,
):
    """Test creating a process with environment variables."""
    workspace_id = "default"
    engine_id = f"sandbox-proc-env-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_process_test5.name,
            sandbox_engine_image=sandbox_engine_image_process_test5.name,
            display_name="Process Env Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the process client
        process_client = super_admin_clients.sandbox_clients.process_client

        # Create a process with environment variables
        process = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="sh",
                args=["-c", "echo MY_VAR is: $MY_VAR"],
                environment_variables={
                    "MY_VAR": "test_value_123",
                },
            ),
            auto_run=True,
        )

        # Wait for process to complete
        completed_process = process_client.wait_process(name=process.name)
        assert completed_process.state == ProcessState.STATE_SUCCEEDED
        assert completed_process.exit_code == 0

        # Read output and verify environment variable was set
        output = process_client.read_output(name=process.name)
        assert b"MY_VAR is: test_value_123" in output

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_wait_process_by_polling(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_process_test6,
    sandbox_engine_image_process_test6,
):
    """Test wait_process_by_polling method for client-side polling."""
    workspace_id = "default"
    engine_id = f"sandbox-proc-poll-{uuid.uuid4().hex[:8]}"

    # Create a sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_process_test6.name,
            sandbox_engine_image=sandbox_engine_image_process_test6.name,
            display_name="Process Polling Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        # Wait for the sandbox engine to be running
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get the process client
        process_client = super_admin_clients.sandbox_clients.process_client

        # Test wait_process_by_polling with a quick process
        process = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="echo",
                args=["Testing polling wait"],
            ),
            auto_run=True,
        )

        # Wait using the polling method with custom timeout and interval
        completed_process = process_client.wait_process_by_polling(
            name=process.name,
            timeout_seconds=60,
            poll_interval_seconds=1,
        )

        # Verify process completed successfully
        assert completed_process.state == ProcessState.STATE_SUCCEEDED
        assert completed_process.exit_code == 0

        # Read output to verify process ran
        output = process_client.read_output(name=process.name)
        assert b"Testing polling wait" in output

        # Test timeout behavior with a long-running process
        long_process = process_client.create_process(
            parent=engine.name,
            process=Process(
                command="sleep",
                args=["10"],
            ),
            auto_run=True,
        )

        # Attempt to wait with a very short timeout (should raise TimeoutError)
        with pytest.raises(TimeoutError) as exc_info:
            process_client.wait_process_by_polling(
                name=long_process.name,
                timeout_seconds=2,
                poll_interval_seconds=1,
            )

        # Verify the error message contains useful information
        assert "did not reach final state" in str(exc_info.value)
        assert long_process.name in str(exc_info.value)

    finally:
        # Clean up: Delete the sandbox engine
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")