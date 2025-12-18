import json
import os

import pytest
from kubernetes import client
from kubernetes import config

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState
from tests.integration.conftest import WORKSPACE_BOTH_RESOURCES
from tests.integration.conftest import WORKSPACE_NO_RESOURCES
from tests.integration.conftest import WORKSPACE_ONLY_ANNOTATIONS
from tests.integration.conftest import WORKSPACE_ONLY_LABELS


def delete_sandbox_engine_if_exists(client_instance, workspace_id: str, engine_id: str):
    """
    Delete a sandbox engine, ignoring NOT_FOUND errors (simulating allow_missing=True).
    Re-raises any other unexpected exceptions.
    """
    try:
        client_instance.delete_sandbox_engine(
            name=f"workspaces/{workspace_id}/sandboxEngines/{engine_id}"
        )
    except CustomApiException as exc:
        if exc.status != 404:
            raise


def get_sandbox_pod(namespace: str, engine_uid: str):
    """Get the SandboxEngine pod for the specified engine UID."""
    return client.CoreV1Api().read_namespaced_pod(
        namespace=namespace, name=f"engine-{engine_uid}"
    )


@pytest.mark.timeout(180)
def test_workspace_no_resources(
    sandbox_engine_client_super_admin,
    sandbox_engine_template_ws_resource1,
    sandbox_engine_image_ws_resource1,
):
    """
    Test creating engine in workspace with no resource labels/annotations.
    Pod should not have workspace-specific labels/annotations.
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_NO_RESOURCES
    engine_id = "sandbox-no-resources"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_ws_resource1.name,
                sandbox_engine_image=sandbox_engine_image_ws_resource1.name,
                display_name="Sandbox with no workspace resources",
            ),
            sandbox_engine_id=engine_id,
        )

        # Wait for engine to reach RUNNING state
        engine = sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=60)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        pod = get_sandbox_pod(namespace=namespace, engine_uid=engine.uid)

        # Verify workspace labels/annotations are not present
        assert "lbl1" not in pod.metadata.labels
        assert "lbl2" not in pod.metadata.labels
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

    finally:
        delete_sandbox_engine_if_exists(sandbox_engine_client_super_admin, workspace_id, engine_id)


@pytest.mark.timeout(180)
def test_workspace_only_labels(
    sandbox_engine_client_super_admin,
    sandbox_engine_template_ws_resource2,
    sandbox_engine_image_ws_resource2,
):
    """
    Test creating engine in workspace with only resource labels.
    Since labels mode is ENABLED, pod should have workspace labels applied.
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_ONLY_LABELS
    engine_id = "sandbox-only-labels"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_ws_resource2.name,
                sandbox_engine_image=sandbox_engine_image_ws_resource2.name,
                display_name="Sandbox with workspace labels",
            ),
            sandbox_engine_id=engine_id,
        )

        # Wait for engine to reach RUNNING state
        engine = sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=60)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        pod = get_sandbox_pod(namespace=namespace, engine_uid=engine.uid)

        # Verify workspace labels are applied (labels mode is ENABLED)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        # Verify workspace annotations are not present (workspace has no annotations)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

    finally:
        delete_sandbox_engine_if_exists(sandbox_engine_client_super_admin, workspace_id, engine_id)


@pytest.mark.timeout(180)
def test_workspace_only_annotations(
    sandbox_engine_client_super_admin,
    sandbox_engine_template_ws_resource3,
    sandbox_engine_image_ws_resource3,
):
    """
    Test creating engine in workspace with only resource annotations.
    Since annotations mode is DISABLED, pod should NOT have workspace annotations applied.
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_ONLY_ANNOTATIONS
    engine_id = "sandbox-only-annotations"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_ws_resource3.name,
                sandbox_engine_image=sandbox_engine_image_ws_resource3.name,
                display_name="Sandbox with workspace annotations",
            ),
            sandbox_engine_id=engine_id,
        )

        # Wait for engine to reach RUNNING state
        engine = sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=60)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        pod = get_sandbox_pod(namespace=namespace, engine_uid=engine.uid)

        # Verify workspace annotations are NOT applied (annotations mode is DISABLED)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

        # Verify workspace labels are not present (workspace has no labels)
        assert "lbl1" not in pod.metadata.labels
        assert "lbl2" not in pod.metadata.labels

    finally:
        delete_sandbox_engine_if_exists(sandbox_engine_client_super_admin, workspace_id, engine_id)


@pytest.mark.timeout(180)
def test_workspace_both_labels_and_annotations_with_pod_template(
    sandbox_engine_client_super_admin,
    sandbox_engine_template_ws_resource4,
    sandbox_engine_image_ws_resource4,
):
    """
    Test creating engine in workspace with both labels and annotations.
    Template also has yaml_pod_template_spec with non-conflicting labels/annotations.
    Since labels mode is ENABLED and annotations mode is DISABLED:
    - Pod should have workspace labels applied
    - Pod should have template labels applied
    - Pod should NOT have workspace annotations applied (mode disabled)
    - Pod should have template annotations applied
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_BOTH_RESOURCES
    engine_id = "sandbox-both-resources"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_ws_resource4.name,
                sandbox_engine_image=sandbox_engine_image_ws_resource4.name,
                display_name="Sandbox with both workspace resources",
            ),
            sandbox_engine_id=engine_id,
        )

        # Wait for engine to reach RUNNING state
        engine = sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=60)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        pod = get_sandbox_pod(namespace=namespace, engine_uid=engine.uid)

        # Verify workspace labels are applied (labels mode is ENABLED)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        # Verify template labels are also present (non-conflicting)
        assert pod.metadata.labels["profile-label"] == "profile-value"

        # Verify workspace annotations are NOT applied (annotations mode is DISABLED)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

        # Verify template annotations are still present (from yaml_pod_template_spec)
        assert pod.metadata.annotations["profile-annotation"] == "profile-value"

    finally:
        delete_sandbox_engine_if_exists(sandbox_engine_client_super_admin, workspace_id, engine_id)


@pytest.mark.timeout(30)
def test_workspace_conflict_with_pod_template_returns_400(
    sandbox_engine_client_super_admin,
    sandbox_engine_template_ws_resource5,
    sandbox_engine_image_ws_resource5,
):
    """
    Test creating engine where template's yaml_pod_template_spec conflicts with workspace resource labels.
    Since labels mode is ENABLED, should return 400 BadRequest immediately without creating the engine.
    Note: annotations mode is DISABLED, so annotation conflicts are not checked.
    """
    workspace_id = WORKSPACE_ONLY_LABELS
    engine_id = "sandbox-conflict-test"

    with pytest.raises(CustomApiException) as exc_info:
        sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_ws_resource5.name,
                sandbox_engine_image=sandbox_engine_image_ws_resource5.name,
                display_name="Sandbox with conflicting resources",
            ),
            sandbox_engine_id=engine_id,
        )

    # Verify error message contains the expected conflict message
    error_body = json.loads(exc_info.value.body)
    error_message = error_body["message"]
    expected_message = 'validation error: workspace resource labels conflict: label "lbl1" from workspace ("val1") conflicts with podTemplateSpec label ("conflict-value")'
    assert expected_message in error_message

    # Verify engine was not created
    try:
        sandbox_engine_client_super_admin.get_sandbox_engine(
            name=f"workspaces/{workspace_id}/sandboxEngines/{engine_id}"
        )
        # If we get here, engine was created (should not happen)
        pytest.fail("Engine should not have been created due to conflict")
    except CustomApiException as exc:
        # Expected - engine should not exist
        if exc.status != 404:
            # Unexpected exception, re-raise
            raise