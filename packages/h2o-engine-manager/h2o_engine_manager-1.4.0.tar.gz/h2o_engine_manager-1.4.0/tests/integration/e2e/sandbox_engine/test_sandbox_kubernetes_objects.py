import os
import time
import uuid

import pytest
from kubernetes import client
from kubernetes import config
from kubernetes.client.models.v1_pod import V1Pod
from kubernetes.client.models.v1_service import V1Service

from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState


@pytest.mark.timeout(180)
def test_sandbox_kubernetes_pod_and_service_created(
    sandbox_engine_client_super_admin,
    sandbox_engine_template_k8s_test4,
    sandbox_engine_image_k8s_test4,
):
    """
    Verify that the Kubernetes Pod and Service are created correctly for a sandbox engine.
    Whitebox testing - verifies K8s objects directly from the cluster.
    """
    config.load_config()

    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    # Generate unique engine ID to allow test reruns
    engine_id = f"sandbox-k8s-test-{uuid.uuid4().hex[:8]}"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        # Create sandbox engine
        engine = sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_k8s_test4.name,
                sandbox_engine_image=sandbox_engine_image_k8s_test4.name,
                display_name="K8s Test Engine",
            ),
            sandbox_engine_id=engine_id,
        )

        # Wait until engine is running - pod must be created
        engine = sandbox_engine_client_super_admin.wait(
            name=engine.name, timeout_seconds=60
        )
        assert engine.state == SandboxEngineState.STATE_RUNNING

        # Get Pod from Kubernetes
        pod = get_sandbox_pod(
            namespace=namespace,
            engine_uid=engine.uid,
        )

        # Verify Pod basic properties
        assert pod.metadata.name == f"engine-{engine.uid}"
        assert pod.metadata.namespace == namespace

        # Verify Pod labels
        assert pod.metadata.labels["app.kubernetes.io/created-by"] == "engine-operator"
        assert pod.metadata.labels["app.kubernetes.io/instance"] == engine.uid
        assert pod.metadata.labels["app.kubernetes.io/managed-by"] == "engine-operator"
        assert pod.metadata.labels["app.kubernetes.io/name"] == "sandbox-engine"
        assert "cloud.h2o.ai/creator" in pod.metadata.labels
        assert "cloud.h2o.ai/owner" in pod.metadata.labels

        # Verify Pod annotations
        assert (
            pod.metadata.annotations["cloud.h2o.ai/resource"]
            == f"//engine-manager/workspaces/{workspace_id}/sandboxEngines/{engine_id}"
        )
        assert pod.metadata.annotations["cloud.h2o.ai/workspace-id"] == workspace_id
        assert "cloud.h2o.ai/creator" in pod.metadata.annotations
        assert "cloud.h2o.ai/creator-display-name" in pod.metadata.annotations

        # Verify Pod spec
        assert pod.spec.restart_policy == "Never"
        assert len(pod.spec.containers) == 1

        # Verify container
        container = pod.spec.containers[0]
        assert container.name == "sandbox"
        assert (
            container.image
            == "353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot"
        )

        # Verify container ports
        assert len(container.ports) == 1
        assert container.ports[0].name == "grpc"
        assert container.ports[0].container_port == 50051
        assert container.ports[0].protocol == "TCP"

        # Verify container resources (from template_t1: 100m/200m CPU, 10Mi/20Mi memory, 10Mi storage)
        assert container.resources.requests["cpu"] == "100m"
        assert container.resources.limits["cpu"] == "200m"
        assert container.resources.requests["memory"] == "10485760"  # 10Mi in bytes
        assert container.resources.limits["memory"] == "20971520"  # 20Mi in bytes
        assert container.resources.limits["ephemeral-storage"] == "10485760"  # 10Mi in bytes
        # No GPU requested in template_t1
        assert "nvidia.com/gpu" not in container.resources.limits

        # Verify environment variables
        env_names = {e.name for e in container.env}
        assert "H2O_CLOUD_CLIENT_PLATFORM_TOKEN" in env_names
        assert "H2O_CLOUD_DISCOVERY" in env_names
        assert "H2O_CLOUD_ENVIRONMENT" in env_names
        assert "H2O_CLOUD_TOKEN_ENDPOINT_URL" in env_names

        # Verify security context
        assert pod.spec.security_context.run_as_non_root is True
        assert pod.spec.security_context.fs_group == 1000
        assert (
            pod.spec.security_context.seccomp_profile.type
            == "RuntimeDefault"
        )

        # Get Service from Kubernetes
        service = get_sandbox_service(
            namespace=namespace,
            engine_uid=engine.uid,
        )

        # Verify Service basic properties
        assert service.metadata.name == f"engine-{engine.uid}"
        assert service.metadata.namespace == namespace

        # Verify Service labels
        assert service.metadata.labels["app.kubernetes.io/created-by"] == "engine-operator"
        assert service.metadata.labels["app.kubernetes.io/instance"] == engine.uid
        assert service.metadata.labels["app.kubernetes.io/managed-by"] == "engine-operator"
        assert service.metadata.labels["app.kubernetes.io/name"] == "sandbox-engine"

        # Verify Service spec
        assert service.spec.type == "ClusterIP"
        assert len(service.spec.ports) == 1
        assert service.spec.ports[0].name == "grpc"
        assert service.spec.ports[0].port == 80
        assert service.spec.ports[0].protocol == "TCP"

        # Verify Service selector
        assert service.spec.selector["app.kubernetes.io/instance"] == engine.uid

    finally:
        # Clean up
        sandbox_engine_client_super_admin.delete_sandbox_engine(
            name=f"workspaces/{workspace_id}/sandboxEngines/{engine_id}"
        )


@pytest.mark.timeout(180)
def test_sandbox_kubernetes_pod_with_gpu(
    sandbox_engine_client_super_admin,
    sandbox_engine_template_k8s_test2,
    sandbox_engine_image_k8s_test2,
):
    """
    Verify that GPU resources are correctly set in the Pod when GPU is requested.
    """
    config.load_config()

    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    # Generate unique engine ID to allow test reruns
    engine_id = f"sandbox-k8s-gpu-test-{uuid.uuid4().hex[:8]}"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        # Create sandbox engine with GPU (template_k8s_test2 has gpu=1)
        engine = sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_k8s_test2.name,
                sandbox_engine_image=sandbox_engine_image_k8s_test2.name,
                display_name="K8s GPU Test Engine",
            ),
            sandbox_engine_id=engine_id,
        )

        # Wait for pod to be created (may not reach running state if no GPU available)
        pod = wait_until_get_sandbox_pod(
            namespace=namespace,
            engine_uid=engine.uid,
            timeout_seconds=60,
        )

        # Verify GPU resource is set
        container = pod.spec.containers[0]
        assert "amd.com/gpu" in container.resources.limits
        assert container.resources.limits["amd.com/gpu"] == "1"

        # Verify other resources from template_t2
        assert container.resources.requests["cpu"] == "200m"
        assert container.resources.limits["cpu"] == "400m"
        assert container.resources.requests["memory"] == "20971520"  # 20Mi in bytes
        assert container.resources.limits["memory"] == "41943040"  # 40Mi in bytes
        assert container.resources.limits["ephemeral-storage"] == "20971520"  # 20Mi in bytes

    finally:
        # Clean up
        sandbox_engine_client_super_admin.delete_sandbox_engine(
            name=f"workspaces/{workspace_id}/sandboxEngines/{engine_id}"
        )


@pytest.mark.timeout(180)
def test_sandbox_kubernetes_objects_deleted(
    sandbox_engine_client_super_admin,
    sandbox_engine_template_k8s_test3,
    sandbox_engine_image_k8s_test3,
):
    """
    Verify that Kubernetes objects (Pod and Service) are deleted when sandbox engine is deleted.
    """
    config.load_config()

    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    # Generate unique engine ID to allow test reruns
    engine_id = f"sandbox-k8s-delete-test-{uuid.uuid4().hex[:8]}"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    # Create sandbox engine
    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_k8s_test3.name,
            sandbox_engine_image=sandbox_engine_image_k8s_test3.name,
            display_name="K8s Delete Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    # Wait until engine is running
    engine = sandbox_engine_client_super_admin.wait(
        name=engine.name, timeout_seconds=60
    )
    assert engine.state == SandboxEngineState.STATE_RUNNING

    # Verify objects exist
    pod = get_sandbox_pod(namespace=namespace, engine_uid=engine.uid)
    assert pod is not None
    service = get_sandbox_service(namespace=namespace, engine_uid=engine.uid)
    assert service is not None

    # Delete the engine
    sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)

    # Wait for deletion to complete
    sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=60)

    # Verify Pod is deleted
    with pytest.raises(client.exceptions.ApiException) as exc:
        get_sandbox_pod(namespace=namespace, engine_uid=engine.uid)
    assert exc.value.status == 404

    # Verify Service is deleted
    with pytest.raises(client.exceptions.ApiException) as exc:
        get_sandbox_service(namespace=namespace, engine_uid=engine.uid)
    assert exc.value.status == 404


def get_sandbox_pod(namespace: str, engine_uid: str) -> V1Pod:
    """Get the Pod for a sandbox engine by its UID."""
    return client.CoreV1Api().read_namespaced_pod(
        namespace=namespace, name=f"engine-{engine_uid}"
    )


def get_sandbox_service(namespace: str, engine_uid: str) -> V1Service:
    """Get the Service for a sandbox engine by its UID."""
    return client.CoreV1Api().read_namespaced_service(
        namespace=namespace, name=f"engine-{engine_uid}"
    )


def wait_until_get_sandbox_pod(
    namespace: str, engine_uid: str, timeout_seconds: int = 60
) -> V1Pod:
    """
    Wait until the Pod is created and return it.
    Useful when testing GPU engines that may not reach running state.
    """
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            return get_sandbox_pod(namespace=namespace, engine_uid=engine_uid)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                time.sleep(2)
                continue
            raise
    raise TimeoutError(
        f"Pod engine-{engine_uid} not created within {timeout_seconds} seconds"
    )


@pytest.mark.timeout(180)
def test_sandbox_pod_template_spec_applied(
    sandbox_engine_client_super_admin,
    sandbox_engine_template_k8s_test1,
    sandbox_engine_image_k8s_test1,
):
    """
    Verify that yaml_pod_template_spec from the template is correctly applied to the pod.
    """
    config.load_config()

    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    # Generate unique engine ID to allow test reruns
    engine_id = f"sandbox-podspec-test-{uuid.uuid4().hex[:8]}"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    try:
        # Create sandbox engine with template that has yaml_pod_template_spec
        engine = sandbox_engine_client_super_admin.create_sandbox_engine(
            parent=f"workspaces/{workspace_id}",
            sandbox_engine=SandboxEngine(
                sandbox_engine_template=sandbox_engine_template_k8s_test1.name,
                sandbox_engine_image=sandbox_engine_image_k8s_test1.name,
                display_name="Pod Template Spec Test Engine",
            ),
            sandbox_engine_id=engine_id,
        )

        # Wait for pod to be created
        pod = wait_until_get_sandbox_pod(
            namespace=namespace,
            engine_uid=engine.uid,
            timeout_seconds=60,
        )

        # Verify the pod template spec was applied
        # The template has yaml_pod_template_spec with POD_TEMPLATE_TEST_VAR
        container = pod.spec.containers[0]
        env_dict = {e.name: e.value for e in container.env}

        assert "POD_TEMPLATE_TEST_VAR" in env_dict
        assert env_dict["POD_TEMPLATE_TEST_VAR"] == "custom-test-value"

        # Also verify that the base env vars are still present (not overridden)
        assert "H2O_CLOUD_CLIENT_PLATFORM_TOKEN" in env_dict
        assert "H2O_CLOUD_DISCOVERY" in env_dict
        assert "H2O_CLOUD_ENVIRONMENT" in env_dict
        assert "H2O_CLOUD_TOKEN_ENDPOINT_URL" in env_dict

    finally:
        # Clean up
        sandbox_engine_client_super_admin.delete_sandbox_engine(
            name=f"workspaces/{workspace_id}/sandboxEngines/{engine_id}"
        )