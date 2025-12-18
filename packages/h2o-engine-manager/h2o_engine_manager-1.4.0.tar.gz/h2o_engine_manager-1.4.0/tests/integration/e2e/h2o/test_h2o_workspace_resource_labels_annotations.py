import json
import os

import pytest
from kubernetes import client
from kubernetes import config

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.h2o_engine.state import H2OEngineState
from tests.integration.conftest import WORKSPACE_BOTH_RESOURCES
from tests.integration.conftest import WORKSPACE_NO_RESOURCES
from tests.integration.conftest import WORKSPACE_ONLY_ANNOTATIONS
from tests.integration.conftest import WORKSPACE_ONLY_LABELS


@pytest.mark.timeout(180)
def test_workspace_no_resources(
    h2o_engine_client,
    h2o_engine_profile_p10,
    h2o_engine_version_v8,
):
    """
    Test creating engine in workspace with no resource labels/annotations.
    Pod should not have workspace-specific labels/annotations.
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_NO_RESOURCES
    engine_id = "engine-no-resources"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = h2o_engine_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            node_count=1,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine with no workspace resources",
            profile=h2o_engine_profile_p10.name,
            h2o_engine_version=h2o_engine_version_v8.name,
        )

        engine.wait()
        assert engine.state.name == H2OEngineState.STATE_RUNNING.name

        pod = get_h2o_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace labels/annotations are not present
        assert "lbl1" not in pod.metadata.labels
        assert "lbl2" not in pod.metadata.labels
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

    finally:
        h2o_engine_client.client_info.api_instance.h2_o_engine_service_delete_h2_o_engine(
            name_5=f"workspaces/{workspace_id}/h2oEngines/{engine_id}", allow_missing=True
        )


@pytest.mark.timeout(180)
def test_workspace_only_labels_with_pod_template(
    h2o_engine_client,
    h2o_engine_profile_p12,
    h2o_engine_version_v10,
):
    """
    Test creating engine in workspace with only resource labels.
    Profile has yaml_pod_template_spec with non-conflicting labels/annotations.
    Since labels mode is ENABLED:
    - Pod should have workspace labels applied
    - Pod should have profile labels applied (non-conflicting)
    - Pod should have profile annotations applied
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_ONLY_LABELS
    engine_id = "engine-only-labels-with-template"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = h2o_engine_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            node_count=1,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine with workspace labels and pod template",
            profile=h2o_engine_profile_p12.name,
            h2o_engine_version=h2o_engine_version_v10.name,
        )

        engine.wait()
        assert engine.state.name == H2OEngineState.STATE_RUNNING.name

        pod = get_h2o_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace labels are applied (labels mode is ENABLED)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        # Verify profile labels are also present (non-conflicting)
        assert pod.metadata.labels["profile-label"] == "profile-value"

        # Verify workspace annotations are not present (workspace has no annotations)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

        # Verify profile annotations are present (from yaml_pod_template_spec)
        assert pod.metadata.annotations["profile-annotation"] == "profile-value"

    finally:
        h2o_engine_client.client_info.api_instance.h2_o_engine_service_delete_h2_o_engine(
            name_5=f"workspaces/{workspace_id}/h2oEngines/{engine_id}", allow_missing=True
        )


@pytest.mark.timeout(180)
def test_workspace_only_annotations(
    h2o_engine_client,
    h2o_engine_profile_p11,
    h2o_engine_version_v9,
):
    """
    Test creating engine in workspace with only resource annotations.
    Since annotations mode is DISABLED, pod should NOT have workspace annotations applied.
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_ONLY_ANNOTATIONS
    engine_id = "engine-only-annotations"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = h2o_engine_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            node_count=1,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine with workspace annotations",
            profile=h2o_engine_profile_p11.name,
            h2o_engine_version=h2o_engine_version_v9.name,
        )

        engine.wait()
        assert engine.state.name == H2OEngineState.STATE_RUNNING.name

        pod = get_h2o_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace annotations are NOT applied (annotations mode is DISABLED)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

        # Verify workspace labels are not present (workspace has no labels)
        assert "lbl1" not in pod.metadata.labels
        assert "lbl2" not in pod.metadata.labels

    finally:
        h2o_engine_client.client_info.api_instance.h2_o_engine_service_delete_h2_o_engine(
            name_5=f"workspaces/{workspace_id}/h2oEngines/{engine_id}", allow_missing=True
        )


@pytest.mark.timeout(180)
def test_workspace_both_resources_no_pod_template(
    h2o_engine_client,
    h2o_engine_profile_p14,
    h2o_engine_version_v12,
):
    """
    Test creating engine in workspace with both labels and annotations.
    Profile does NOT have yaml_pod_template_spec.
    Since labels mode is ENABLED and annotations mode is DISABLED:
    - Pod should have workspace labels applied
    - Pod should NOT have workspace annotations applied (mode disabled)
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_BOTH_RESOURCES
    engine_id = "engine-both-resources-no-template"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = h2o_engine_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            node_count=1,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine with both workspace resources, no pod template",
            profile=h2o_engine_profile_p14.name,
            h2o_engine_version=h2o_engine_version_v12.name,
        )

        engine.wait()
        assert engine.state.name == H2OEngineState.STATE_RUNNING.name

        pod = get_h2o_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace labels are applied (labels mode is ENABLED)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        # Verify workspace annotations are NOT applied (annotations mode is DISABLED)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

        # Verify no profile labels/annotations (profile has no yaml_pod_template_spec)
        assert "profile-label" not in pod.metadata.labels
        assert "profile-annotation" not in pod.metadata.annotations

    finally:
        h2o_engine_client.client_info.api_instance.h2_o_engine_service_delete_h2_o_engine(
            name_5=f"workspaces/{workspace_id}/h2oEngines/{engine_id}", allow_missing=True
        )


@pytest.mark.timeout(30)
def test_workspace_labels_conflict_with_pod_template_returns_400(
    h2o_engine_client,
    h2o_engine_profile_p13,
    h2o_engine_version_v11,
):
    """
    Test creating engine in workspace with only labels where profile's yaml_pod_template_spec conflicts.
    Since labels mode is ENABLED, should return 400 BadRequest immediately without creating the engine.
    This tests conflict detection with WORKSPACE_ONLY_LABELS (different from DAI which uses WORKSPACE_BOTH_RESOURCES).
    """
    workspace_id = WORKSPACE_ONLY_LABELS
    engine_id = "engine-labels-conflict"

    with pytest.raises(CustomApiException) as exc_info:
        h2o_engine_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            node_count=1,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine with conflicting labels",
            profile=h2o_engine_profile_p13.name,
            h2o_engine_version=h2o_engine_version_v11.name,
        )

    # Verify error message contains the expected conflict message
    error_body = json.loads(exc_info.value.body)
    error_message = error_body["message"]
    expected_message = 'validation error: workspace resource labels conflict: label "lbl1" from workspace ("val1") conflicts with podTemplateSpec label ("conflict-value")'
    assert expected_message in error_message

    # Verify engine was not created
    try:
        h2o_engine_client.client_info.api_instance.h2_o_engine_service_get_h2_o_engine(
            name=f"workspaces/{workspace_id}/h2oEngines/{engine_id}"
        )
        # If we get here, engine was created (should not happen)
        pytest.fail("Engine should not have been created due to conflict")
    except Exception:
        # Expected - engine should not exist
        pass


def get_h2o_pod(namespace: str, workspace_id: str, engine_id: str, pod_number: int = 0):
    """Get the H2O pod for the specified engine."""
    # Get the H2O CRD to find the pod name
    h2o = client.CustomObjectsApi().get_namespaced_custom_object(
        group="engine.h2o.ai",
        version="v1",
        namespace=namespace,
        plural="h2os",
        name=f"{workspace_id}.{engine_id}",
    )

    return client.CoreV1Api().read_namespaced_pod(
        namespace=namespace, name=f"engine-{h2o['spec']['managedUID']}-{pod_number}"
    )