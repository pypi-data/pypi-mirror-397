import http
import json
import os
import time

import pytest
from kubernetes import client
from kubernetes import config

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.notebook_engine.engine import NotebookEngine
from h2o_engine_manager.clients.notebook_engine.state import NotebookEngineState
from tests.integration.conftest import WORKSPACE_BOTH_RESOURCES
from tests.integration.conftest import WORKSPACE_NO_RESOURCES
from tests.integration.conftest import WORKSPACE_ONLY_ANNOTATIONS
from tests.integration.conftest import WORKSPACE_ONLY_LABELS

# Time to wait for operator to create pod (engine won't reach RUNNING with non-existing images)
POD_CREATION_WAIT_SECONDS = 10


def delete_notebook_engine_if_exists(client, workspace_id: str, engine_id: str):
    """
    Delete a notebook engine, ignoring NOT_FOUND errors (simulating allow_missing=True).
    Re-raises any other unexpected exceptions.
    """
    try:
        client.delete_notebook_engine(
            name=f"workspaces/{workspace_id}/notebookEngines/{engine_id}"
        )
    except CustomApiException as exc:
        if exc.status != http.HTTPStatus.NOT_FOUND:
            # Unexpected exception, re-raise
            raise


@pytest.mark.timeout(180)
def test_workspace_no_resources(
    notebook_engine_client_super_admin,
    notebook_engine_profile_p6,
    notebook_engine_image_i7,
    postgres_connection,
):
    """
    Test creating engine in workspace with no resource labels/annotations.
    Pod should not have workspace-specific labels/annotations.
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_NO_RESOURCES
    engine_id = "ntbk-no-resources"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = notebook_engine_client_super_admin.create_notebook_engine(
            parent=f"workspaces/{workspace_id}",
            notebook_engine=NotebookEngine(
                profile=notebook_engine_profile_p6.name,
                notebook_image=notebook_engine_image_i7.name,
                display_name="Notebook with no workspace resources",
            ),
            notebook_engine_id=engine_id,
        )

        # Wait for operator to create pod
        time.sleep(POD_CREATION_WAIT_SECONDS)

        pod = get_notebook_pod(postgres_connection=postgres_connection, namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace labels/annotations are not present
        assert "lbl1" not in pod.metadata.labels
        assert "lbl2" not in pod.metadata.labels
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

    finally:
        delete_notebook_engine_if_exists(notebook_engine_client_super_admin, workspace_id, engine_id)


@pytest.mark.timeout(180)
def test_workspace_only_labels(
    notebook_engine_client_super_admin,
    notebook_engine_profile_p7,
    notebook_engine_image_i8,
    postgres_connection,
):
    """
    Test creating engine in workspace with only resource labels.
    Since labels mode is ENABLED, pod should have workspace labels applied.
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_ONLY_LABELS
    engine_id = "ntbk-only-labels"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = notebook_engine_client_super_admin.create_notebook_engine(
            parent=f"workspaces/{workspace_id}",
            notebook_engine=NotebookEngine(
                profile=notebook_engine_profile_p7.name,
                notebook_image=notebook_engine_image_i8.name,
                display_name="Notebook with workspace labels",
            ),
            notebook_engine_id=engine_id,
        )

        # Wait for operator to create pod
        time.sleep(POD_CREATION_WAIT_SECONDS)

        pod = get_notebook_pod(postgres_connection=postgres_connection, namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace labels are applied (labels mode is ENABLED)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        # Verify workspace annotations are not present (workspace has no annotations)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

    finally:
        delete_notebook_engine_if_exists(notebook_engine_client_super_admin, workspace_id, engine_id)


@pytest.mark.timeout(180)
def test_workspace_only_annotations(
    notebook_engine_client_super_admin,
    notebook_engine_profile_p8,
    notebook_engine_image_i9,
    postgres_connection,
):
    """
    Test creating engine in workspace with only resource annotations.
    Since annotations mode is DISABLED, pod should NOT have workspace annotations applied.
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_ONLY_ANNOTATIONS
    engine_id = "ntbk-only-annotations"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = notebook_engine_client_super_admin.create_notebook_engine(
            parent=f"workspaces/{workspace_id}",
            notebook_engine=NotebookEngine(
                profile=notebook_engine_profile_p8.name,
                notebook_image=notebook_engine_image_i9.name,
                display_name="Notebook with workspace annotations",
            ),
            notebook_engine_id=engine_id,
        )

        # Wait for operator to create pod
        time.sleep(POD_CREATION_WAIT_SECONDS)

        pod = get_notebook_pod(postgres_connection=postgres_connection, namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace annotations are NOT applied (annotations mode is DISABLED)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

        # Verify workspace labels are not present (workspace has no labels)
        assert "lbl1" not in pod.metadata.labels
        assert "lbl2" not in pod.metadata.labels

    finally:
        delete_notebook_engine_if_exists(notebook_engine_client_super_admin, workspace_id, engine_id)


@pytest.mark.timeout(180)
def test_workspace_both_labels_and_annotations_with_pod_template(
    notebook_engine_client_super_admin,
    notebook_engine_profile_p9,
    notebook_engine_image_i10,
    postgres_connection,
):
    """
    Test creating engine in workspace with both labels and annotations.
    Profile also has yaml_pod_template_spec with non-conflicting labels/annotations.
    Since labels mode is ENABLED and annotations mode is DISABLED:
    - Pod should have workspace labels applied
    - Pod should have profile labels applied
    - Pod should NOT have workspace annotations applied (mode disabled)
    - Pod should have profile annotations applied
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_BOTH_RESOURCES
    engine_id = "ntbk-both-resources"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = notebook_engine_client_super_admin.create_notebook_engine(
            parent=f"workspaces/{workspace_id}",
            notebook_engine=NotebookEngine(
                profile=notebook_engine_profile_p9.name,
                notebook_image=notebook_engine_image_i10.name,
                display_name="Notebook with both workspace resources",
            ),
            notebook_engine_id=engine_id,
        )

        # Wait for operator to create pod
        time.sleep(POD_CREATION_WAIT_SECONDS)

        pod = get_notebook_pod(postgres_connection=postgres_connection, namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace labels are applied (labels mode is ENABLED)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        # Verify profile labels are also present (non-conflicting)
        assert pod.metadata.labels["profile-label"] == "profile-value"

        # Verify workspace annotations are NOT applied (annotations mode is DISABLED)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

        # Verify profile annotations are still present (from yaml_pod_template_spec)
        assert pod.metadata.annotations["profile-annotation"] == "profile-value"

    finally:
        delete_notebook_engine_if_exists(notebook_engine_client_super_admin, workspace_id, engine_id)


@pytest.mark.timeout(30)
def test_workspace_conflict_with_pod_template_returns_400(
    notebook_engine_client_super_admin,
    notebook_engine_profile_p10,
    notebook_engine_image_i11,
):
    """
    Test creating engine where profile's yaml_pod_template_spec conflicts with workspace resource labels.
    Since labels mode is ENABLED, should return 400 BadRequest immediately without creating the engine.
    Note: annotations mode is DISABLED, so annotation conflicts are not checked.
    """
    workspace_id = WORKSPACE_BOTH_RESOURCES
    engine_id = "ntbk-conflict-test"

    with pytest.raises(CustomApiException) as exc_info:
        notebook_engine_client_super_admin.create_notebook_engine(
            parent=f"workspaces/{workspace_id}",
            notebook_engine=NotebookEngine(
                profile=notebook_engine_profile_p10.name,
                notebook_image=notebook_engine_image_i11.name,
                display_name="Notebook with conflicting resources",
            ),
            notebook_engine_id=engine_id,
        )

    # Verify error message contains the expected conflict message
    error_body = json.loads(exc_info.value.body)
    error_message = error_body["message"]
    expected_message = 'validation error: workspace resource labels conflict: label "lbl1" from workspace ("val1") conflicts with podTemplateSpec label ("conflict-value")'
    assert expected_message in error_message

    # Verify engine was not created
    try:
        notebook_engine_client_super_admin.get_notebook_engine(
            name=f"workspaces/{workspace_id}/notebookEngines/{engine_id}"
        )
        # If we get here, engine was created (should not happen)
        pytest.fail("Engine should not have been created due to conflict")
    except CustomApiException as exc:
        # Expected - engine should not exist
        if exc.status != http.HTTPStatus.NOT_FOUND:
            # Unexpected exception, re-raise
            raise


@pytest.mark.timeout(180)
def test_resume_workspace_labels_non_conflicting_profile(
    notebook_engine_client_super_admin,
    notebook_engine_profile_p11,
    notebook_engine_profile_p12,
    notebook_engine_image_i12,
    postgres_connection,
):
    config.load_config()

    workspace_id = WORKSPACE_ONLY_LABELS
    engine_id = "ntbk-resume-non-conflict"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = notebook_engine_client_super_admin.create_notebook_engine(
            parent=f"workspaces/{workspace_id}",
            notebook_engine=NotebookEngine(
                profile=notebook_engine_profile_p11.name,
                notebook_image=notebook_engine_image_i12.name,
                display_name="Notebook for resume test non-conflicting",
            ),
            notebook_engine_id=engine_id,
        )

        # Wait for operator to create pod
        time.sleep(POD_CREATION_WAIT_SECONDS)

        # Verify workspace labels are applied after creation
        pod = get_notebook_pod(postgres_connection=postgres_connection, namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        engine = notebook_engine_client_super_admin.pause_notebook_engine(name=f"workspaces/{workspace_id}/notebookEngines/{engine_id}")
        notebook_engine_client_super_admin.wait(name=engine.name, timeout_seconds=60)
        engine = notebook_engine_client_super_admin.get_notebook_engine(name=engine.name)
        assert engine.state == NotebookEngineState.STATE_PAUSED

        engine.profile = notebook_engine_profile_p12.name
        notebook_engine_client_super_admin.update_notebook_engine(notebook_engine=engine)

        engine = notebook_engine_client_super_admin.resume_notebook_engine(name=engine.name)

        # Wait for operator to recreate pod
        time.sleep(POD_CREATION_WAIT_SECONDS)

        # Verify workspace labels and new profile labels/annotations after resume
        pod = get_notebook_pod(postgres_connection=postgres_connection, namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"
        assert pod.metadata.labels["resume-profile-label"] == "resume-value"
        assert pod.metadata.annotations["resume-profile-annotation"] == "resume-value"

    finally:
        delete_notebook_engine_if_exists(notebook_engine_client_super_admin, workspace_id, engine_id)


@pytest.mark.timeout(180)
def test_resume_workspace_labels_conflicting_profile_returns_400(
    notebook_engine_client_super_admin,
    notebook_engine_profile_p13,
    notebook_engine_profile_p14,
    notebook_engine_image_i13,
    postgres_connection,
):
    config.load_config()

    workspace_id = WORKSPACE_BOTH_RESOURCES
    engine_id = "ntbk-resume-conflict"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = notebook_engine_client_super_admin.create_notebook_engine(
            parent=f"workspaces/{workspace_id}",
            notebook_engine=NotebookEngine(
                profile=notebook_engine_profile_p13.name,
                notebook_image=notebook_engine_image_i13.name,
                display_name="Notebook for resume conflict test",
            ),
            notebook_engine_id=engine_id,
        )

        # Wait for operator to create pod
        time.sleep(POD_CREATION_WAIT_SECONDS)

        # Verify workspace labels are applied after creation
        pod = get_notebook_pod(postgres_connection=postgres_connection, namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        engine = notebook_engine_client_super_admin.pause_notebook_engine(name=f"workspaces/{workspace_id}/notebookEngines/{engine_id}")
        notebook_engine_client_super_admin.wait(name=engine.name, timeout_seconds=60)
        engine = notebook_engine_client_super_admin.get_notebook_engine(name=engine.name)
        assert engine.state == NotebookEngineState.STATE_PAUSED

        engine.profile = notebook_engine_profile_p14.name
        notebook_engine_client_super_admin.update_notebook_engine(notebook_engine=engine)

        with pytest.raises(CustomApiException) as exc_info:
            notebook_engine_client_super_admin.resume_notebook_engine(name=engine.name)

        error_body = json.loads(exc_info.value.body)
        error_message = error_body["message"]
        expected_message = 'validation error: workspace resource labels conflict: label "lbl1" from workspace ("val1") conflicts with podTemplateSpec label ("resume-conflict-value")'
        assert expected_message in error_message

        # Verify engine is still paused after failed resume
        engine = notebook_engine_client_super_admin.get_notebook_engine(name=engine.name)
        assert engine.state == NotebookEngineState.STATE_PAUSED

    finally:
        delete_notebook_engine_if_exists(notebook_engine_client_super_admin, workspace_id, engine_id)


def get_notebook_pod(postgres_connection, namespace: str, workspace_id: str, engine_id: str):
    """Get the Notebook pod for the specified engine."""
    # Query the notebook_engine table to get the UID
    cursor = postgres_connection.cursor()
    try:
        cursor.execute(
            "SELECT uid FROM notebook_engine WHERE workspace_id = %s AND notebook_engine_id = %s",
            (workspace_id, engine_id),
        )
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"NotebookEngine not found: workspace_id={workspace_id}, engine_id={engine_id}")
        uid = result[0]
    finally:
        cursor.close()

    # Get the pod using the UID
    return client.CoreV1Api().read_namespaced_pod(
        namespace=namespace, name=f"engine-{uid}"
    )