import json
import os

import pytest
from kubernetes import client
from kubernetes import config

from h2o_engine_manager.clients.dai_engine.dai_engine_state import DAIEngineState
from h2o_engine_manager.clients.exception import CustomApiException
from tests.integration.conftest import WORKSPACE_BOTH_RESOURCES
from tests.integration.conftest import WORKSPACE_NO_RESOURCES
from tests.integration.conftest import WORKSPACE_ONLY_ANNOTATIONS
from tests.integration.conftest import WORKSPACE_ONLY_LABELS


@pytest.mark.timeout(180)
def test_workspace_no_resources(
    dai_client,
    dai_engine_profile_34,
    dai_engine_version_v1_11_27,
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
        engine = dai_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            storage_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine with no workspace resources",
            profile=dai_engine_profile_34.name,
            dai_engine_version=dai_engine_version_v1_11_27.name,
        )

        engine.wait()
        assert engine.state.name == DAIEngineState.STATE_RUNNING.name

        pod = get_dai_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace labels/annotations are not present
        assert "lbl1" not in pod.metadata.labels
        assert "lbl2" not in pod.metadata.labels
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

    finally:
        dai_client.client_info.api_instance.d_ai_engine_service_delete_dai_engine(
            name_2=f"workspaces/{workspace_id}/daiEngines/{engine_id}", allow_missing=True
        )


@pytest.mark.timeout(180)
def test_workspace_only_labels(
    dai_client,
    dai_engine_profile_38,
    dai_engine_version_v1_11_28,
):
    """
    Test creating engine in workspace with only resource labels.
    Since labels mode is ENABLED, pod should have workspace labels applied.
    Whitebox testing! (Pod spec is not accessible via API)
    """
    config.load_config()

    workspace_id = WORKSPACE_ONLY_LABELS
    engine_id = "engine-only-labels"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = dai_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            storage_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine with workspace labels",
            profile=dai_engine_profile_38.name,
            dai_engine_version=dai_engine_version_v1_11_28.name,
        )

        engine.wait()
        assert engine.state.name == DAIEngineState.STATE_RUNNING.name

        pod = get_dai_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace labels are applied (labels mode is ENABLED)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        # Verify workspace annotations are not present (workspace has no annotations)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

    finally:
        dai_client.client_info.api_instance.d_ai_engine_service_delete_dai_engine(
            name_2=f"workspaces/{workspace_id}/daiEngines/{engine_id}", allow_missing=True
        )


@pytest.mark.timeout(180)
def test_workspace_only_annotations(
    dai_client,
    dai_engine_profile_35,
    dai_engine_version_v1_11_29,
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
        engine = dai_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            storage_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine with workspace annotations",
            profile=dai_engine_profile_35.name,
            dai_engine_version=dai_engine_version_v1_11_29.name,
        )

        engine.wait()
        assert engine.state.name == DAIEngineState.STATE_RUNNING.name

        pod = get_dai_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

        # Verify workspace annotations are NOT applied (annotations mode is DISABLED)
        assert "ann1" not in pod.metadata.annotations
        assert "ann2" not in pod.metadata.annotations

        # Verify workspace labels are not present (workspace has no labels)
        assert "lbl1" not in pod.metadata.labels
        assert "lbl2" not in pod.metadata.labels

    finally:
        dai_client.client_info.api_instance.d_ai_engine_service_delete_dai_engine(
            name_2=f"workspaces/{workspace_id}/daiEngines/{engine_id}", allow_missing=True
        )


@pytest.mark.timeout(180)
def test_workspace_both_labels_and_annotations_with_pod_template(
    dai_client,
    dai_engine_profile_36,
    dai_engine_version_v1_11_30,
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
    engine_id = "engine-both-resources"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = dai_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            storage_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine with both workspace resources",
            profile=dai_engine_profile_36.name,
            dai_engine_version=dai_engine_version_v1_11_30.name,
        )

        engine.wait()
        assert engine.state.name == DAIEngineState.STATE_RUNNING.name

        pod = get_dai_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)

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
        dai_client.client_info.api_instance.d_ai_engine_service_delete_dai_engine(
            name_2=f"workspaces/{workspace_id}/daiEngines/{engine_id}", allow_missing=True
        )


@pytest.mark.timeout(30)
def test_workspace_conflict_with_pod_template_returns_400(
    dai_client,
    dai_engine_profile_37,
    dai_engine_version_v1_11_31,
):
    """
    Test creating engine where profile's yaml_pod_template_spec conflicts with workspace resource labels.
    Since labels mode is ENABLED, should return 400 BadRequest immediately without creating the engine.
    Note: annotations mode is DISABLED, so annotation conflicts are not checked.
    """
    workspace_id = WORKSPACE_BOTH_RESOURCES
    engine_id = "engine-conflict-test"

    with pytest.raises(CustomApiException) as exc_info:
        dai_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            storage_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine with conflicting resources",
            profile=dai_engine_profile_37.name,
            dai_engine_version=dai_engine_version_v1_11_31.name,
        )

    # Verify error message contains the expected conflict message
    error_body = json.loads(exc_info.value.body)
    error_message = error_body["message"]
    expected_message = 'validation error: workspace resource labels conflict: label "lbl1" from workspace ("val1") conflicts with podTemplateSpec label ("conflict-value")'
    assert expected_message in error_message

    # Verify engine was not created
    try:
        dai_client.client_info.api_instance.d_ai_engine_service_get_dai_engine(
            name=f"workspaces/{workspace_id}/daiEngines/{engine_id}"
        )
        # If we get here, engine was created (should not happen)
        pytest.fail("Engine should not have been created due to conflict")
    except Exception:
        # Expected - engine should not exist
        pass


@pytest.mark.timeout(180)
def test_resume_workspace_labels_non_conflicting_profile(
    dai_client,
    dai_engine_profile_40,
    dai_engine_profile_41,
    dai_engine_version_v1_11_32,
):
    config.load_config()

    workspace_id = WORKSPACE_ONLY_LABELS
    engine_id = "engine-resume-non-conflict"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = dai_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            storage_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine for resume test non-conflicting",
            profile=dai_engine_profile_40.name,
            dai_engine_version=dai_engine_version_v1_11_32.name,
        )

        engine.wait()
        assert engine.state.name == DAIEngineState.STATE_RUNNING.name

        # Verify workspace labels are applied after creation
        pod = get_dai_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        engine.pause()
        engine.wait()
        assert engine.state.name == DAIEngineState.STATE_PAUSED.name

        engine.profile = dai_engine_profile_41.name
        engine.update()

        engine.resume()
        engine.wait()
        assert engine.state.name == DAIEngineState.STATE_RUNNING.name

        # Verify workspace labels and new profile labels/annotations after resume
        pod = get_dai_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"
        assert pod.metadata.labels["resume-profile-label"] == "resume-value"
        assert pod.metadata.annotations["resume-profile-annotation"] == "resume-value"

    finally:
        dai_client.client_info.api_instance.d_ai_engine_service_delete_dai_engine(
            name_2=f"workspaces/{workspace_id}/daiEngines/{engine_id}", allow_missing=True
        )


@pytest.mark.timeout(180)
def test_resume_workspace_labels_conflicting_profile_returns_400(
    dai_client,
    dai_engine_profile_42,
    dai_engine_profile_43,
    dai_engine_version_v1_11_33,
):
    config.load_config()

    workspace_id = WORKSPACE_BOTH_RESOURCES
    engine_id = "engine-resume-conflict"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        engine = dai_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            cpu=1,
            gpu=0,
            memory_bytes="1Gi",
            storage_bytes="1Gi",
            max_idle_duration="15m",
            max_running_duration="2h",
            display_name="Engine for resume conflict test",
            profile=dai_engine_profile_42.name,
            dai_engine_version=dai_engine_version_v1_11_33.name,
        )

        engine.wait()
        assert engine.state.name == DAIEngineState.STATE_RUNNING.name

        # Verify workspace labels are applied after creation
        pod = get_dai_pod(namespace=namespace, workspace_id=workspace_id, engine_id=engine_id)
        assert pod.metadata.labels["lbl1"] == "val1"
        assert pod.metadata.labels["lbl2"] == "val2"

        engine.pause()
        engine.wait()
        assert engine.state.name == DAIEngineState.STATE_PAUSED.name

        engine.profile = dai_engine_profile_43.name
        engine.update()

        with pytest.raises(CustomApiException) as exc_info:
            engine.resume()

        error_body = json.loads(exc_info.value.body)
        error_message = error_body["message"]
        expected_message = 'validation error: workspace resource labels conflict: label "lbl1" from workspace ("val1") conflicts with podTemplateSpec label ("resume-conflict-value")'
        assert expected_message in error_message

        # Verify engine is still paused after failed resume
        engine = dai_client.get_engine(workspace_id=workspace_id, engine_id=engine.engine_id)
        assert engine.state.name == DAIEngineState.STATE_PAUSED.name

    finally:
        dai_client.client_info.api_instance.d_ai_engine_service_delete_dai_engine(
            name_2=f"workspaces/{workspace_id}/daiEngines/{engine_id}", allow_missing=True
        )


def get_dai_pod(namespace: str, workspace_id: str, engine_id: str):
    """Get the DAI pod for the specified engine."""
    # Get the DriverlessAI CRD to find the pod name
    dai = client.CustomObjectsApi().get_namespaced_custom_object(
        group="engine.h2o.ai",
        version="v1",
        namespace=namespace,
        plural="driverlessais",
        name=f"{workspace_id}.{engine_id}",
    )

    return client.CoreV1Api().read_namespaced_pod(
        namespace=namespace, name=f"engine-{dai['spec']['managedUID']}"
    )