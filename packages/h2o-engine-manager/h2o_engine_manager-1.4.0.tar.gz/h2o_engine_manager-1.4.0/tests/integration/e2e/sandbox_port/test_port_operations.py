"""
Consolidated port tests that verify both API behavior and Kubernetes infrastructure.

Each test validates:
1. API responses (CreatePort, GetPort, ListPorts, UpdatePort, DeletePort)
2. Kubernetes resources (Services, HTTPRoutes, Endpoints)
"""
import os
import subprocess
import time
import urllib.error
import urllib.request
import uuid

import pytest
from kubernetes import client
from kubernetes import config
from kubernetes.client.models.v1_service import V1Service

from h2o_engine_manager.clients.sandbox.port.port import Port
from h2o_engine_manager.clients.sandbox.port.state import PortState
from h2o_engine_manager.clients.sandbox.process.ps import Process
from h2o_engine_manager.clients.sandbox_engine.engine import SandboxEngine
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState

# ============================================================================
# Helper functions for K8s verification
# ============================================================================


def get_port_service(namespace: str, engine_uid: str, port_id: str) -> V1Service:
    """Get the Service for a port by engine UID and port ID."""
    service_name = f"engine-{engine_uid}-port-{port_id}"
    return client.CoreV1Api().read_namespaced_service(
        namespace=namespace, name=service_name
    )


def get_port_httproute(namespace: str, engine_uid: str, port_id: str) -> dict:
    """Get the HTTPRoute for a port by engine UID and port ID."""
    route_name = f"engine-{engine_uid}-port-{port_id}"
    custom_api = client.CustomObjectsApi()
    return custom_api.get_namespaced_custom_object(
        group="gateway.networking.k8s.io",
        version="v1",
        namespace=namespace,
        plural="httproutes",
        name=route_name,
    )


def wait_for_port_service(
    namespace: str, engine_uid: str, port_id: str, timeout_seconds: int
) -> V1Service:
    """Wait for the port Service to be created and return it."""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            return get_port_service(namespace, engine_uid, port_id)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                time.sleep(1)
                continue
            raise
    raise TimeoutError(
        f"Service engine-{engine_uid}-port-{port_id} not created within {timeout_seconds} seconds"
    )


def wait_for_port_httproute(
    namespace: str, engine_uid: str, port_id: str, timeout_seconds: int
) -> dict:
    """Wait for the port HTTPRoute to be created and return it."""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            return get_port_httproute(namespace, engine_uid, port_id)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                time.sleep(1)
                continue
            raise
    raise TimeoutError(
        f"HTTPRoute engine-{engine_uid}-port-{port_id} not created within {timeout_seconds} seconds"
    )


def wait_for_port_service_deleted(
    namespace: str, engine_uid: str, port_id: str, timeout_seconds: int
) -> None:
    """Wait for the port Service to be deleted."""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            get_port_service(namespace, engine_uid, port_id)
            time.sleep(1)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                return
            raise
    raise TimeoutError(
        f"Service engine-{engine_uid}-port-{port_id} not deleted within {timeout_seconds} seconds"
    )


def wait_for_port_httproute_deleted(
    namespace: str, engine_uid: str, port_id: str, timeout_seconds: int
) -> None:
    """Wait for the port HTTPRoute to be deleted."""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            get_port_httproute(namespace, engine_uid, port_id)
            time.sleep(1)
        except client.exceptions.ApiException as e:
            if e.status == 404:
                return
            raise
    raise TimeoutError(
        f"HTTPRoute engine-{engine_uid}-port-{port_id} not deleted within {timeout_seconds} seconds"
    )


def wait_for_endpoints_ready(namespace: str, service_name: str, timeout_seconds: int):
    """Wait for Endpoints to have at least one ready address."""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            endpoints = client.CoreV1Api().read_namespaced_endpoints(
                namespace=namespace, name=service_name
            )
            if endpoints.subsets and len(endpoints.subsets) > 0:
                subset = endpoints.subsets[0]
                if subset.addresses and len(subset.addresses) > 0:
                    return endpoints
        except client.exceptions.ApiException as e:
            if e.status == 404:
                pass
            else:
                raise
        time.sleep(1)
    raise TimeoutError(
        f"Endpoints {service_name} not ready within {timeout_seconds} seconds"
    )


# ============================================================================
# Tests
# ============================================================================


@pytest.mark.timeout(300)
def test_create_private_port(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_port_test1,
    sandbox_engine_image_port_test1,
):
    """
    Test creating a private port:
    - API: CreatePort returns correct response, GetPort retrieves it
    - K8s: Service is created with correct labels and selector
    """
    config.load_config()

    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    engine_id = f"port-private-{uuid.uuid4().hex[:8]}"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_port_test1.name,
            sandbox_engine_image=sandbox_engine_image_port_test1.name,
            display_name="Private Port Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        port_client = super_admin_clients.sandbox_clients.port_client

        # === API: Create port ===
        port = port_client.create_port(
            parent=engine.name,
            port=Port(display_name="Private Port 8080", public=False),
            port_id="8080",
        )

        # Verify API response
        assert port.name is not None
        assert port.name.endswith("/ports/8080")
        assert port.display_name == "Private Port 8080"
        assert port.public is False
        assert port.internal_url != ""
        assert port.public_url == ""  # Private port has no public URL
        # Initial state should be PENDING
        assert port.state == PortState.STATE_PENDING

        # === Wait for port to become READY using client.wait() ===
        port = port_client.wait(name=port.name, timeout_seconds=30)
        assert port is not None
        assert port.state == PortState.STATE_READY
        assert port.failure_reason == ""

        # === API: Get port ===
        fetched_port = port_client.get_port(name=port.name)
        assert fetched_port.name == port.name
        assert fetched_port.display_name == port.display_name
        assert fetched_port.public == port.public
        assert fetched_port.state == PortState.STATE_READY

        # === K8s: Verify Service ===
        service = wait_for_port_service(
            namespace=namespace,
            engine_uid=engine.uid,
            port_id="8080",
            timeout_seconds=30,
        )

        expected_service_name = f"engine-{engine.uid}-port-8080"
        assert service.metadata.name == expected_service_name
        assert service.metadata.namespace == namespace

        # Verify labels
        assert service.metadata.labels["app.kubernetes.io/created-by"] == "engine-operator"
        assert service.metadata.labels["app.kubernetes.io/instance"] == engine.uid
        assert service.metadata.labels["app.kubernetes.io/managed-by"] == "engine-operator"
        assert service.metadata.labels["app.kubernetes.io/name"] == "sandbox-engine"
        assert service.metadata.labels["engine.h2o.ai/port-id"] == "8080"

        # Verify Service spec
        assert service.spec.type == "ClusterIP"
        assert len(service.spec.ports) == 1
        assert service.spec.ports[0].port == 8080
        assert service.spec.ports[0].target_port == 8080
        assert service.spec.ports[0].protocol == "TCP"
        assert service.spec.selector["app.kubernetes.io/instance"] == engine.uid

        # === API: Delete port ===
        port_client.delete_port(name=port.name)

        # === K8s: Verify Service deleted ===
        wait_for_port_service_deleted(
            namespace=namespace,
            engine_uid=engine.uid,
            port_id="8080",
            timeout_seconds=30,
        )

    finally:
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_create_public_port(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_port_test2,
    sandbox_engine_image_port_test2,
):
    """
    Test creating a public port:
    - API: CreatePort returns public_url, GetPort retrieves it
    - K8s: Both Service and HTTPRoute are created
    """
    config.load_config()

    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    engine_id = f"port-public-{uuid.uuid4().hex[:8]}"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_port_test2.name,
            sandbox_engine_image=sandbox_engine_image_port_test2.name,
            display_name="Public Port Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        port_client = super_admin_clients.sandbox_clients.port_client

        # === API: Create public port ===
        port = port_client.create_port(
            parent=engine.name,
            port=Port(display_name="Public Port 9090", public=True),
            port_id="9090",
        )

        # Verify API response
        assert port.name is not None
        assert port.public is True
        assert port.internal_url != ""
        assert port.public_url != ""
        # Initial state should be PENDING
        assert port.state == PortState.STATE_PENDING

        # === Wait for port to become READY using client.wait() ===
        port = port_client.wait(name=port.name, timeout_seconds=30)
        assert port is not None
        assert port.state == PortState.STATE_READY
        assert port.failure_reason == ""

        # === K8s: Verify Service ===
        service = wait_for_port_service(
            namespace=namespace,
            engine_uid=engine.uid,
            port_id="9090",
            timeout_seconds=30,
        )
        assert service is not None

        # === K8s: Verify HTTPRoute ===
        route = wait_for_port_httproute(
            namespace=namespace,
            engine_uid=engine.uid,
            port_id="9090",
            timeout_seconds=30,
        )

        expected_route_name = f"engine-{engine.uid}-port-9090"
        assert route["metadata"]["name"] == expected_route_name
        assert route["metadata"]["namespace"] == namespace

        # Verify HTTPRoute labels
        assert route["metadata"]["labels"]["app.kubernetes.io/created-by"] == "engine-operator"
        assert route["metadata"]["labels"]["app.kubernetes.io/instance"] == engine.uid
        assert route["metadata"]["labels"]["engine.h2o.ai/port-id"] == "9090"

        # Verify HTTPRoute spec
        spec = route["spec"]
        assert "rules" in spec
        assert len(spec["rules"]) > 0

        rule = spec["rules"][0]
        assert "backendRefs" in rule
        assert rule["backendRefs"][0]["name"] == expected_route_name
        assert rule["backendRefs"][0]["port"] == 9090

        # Verify URL rewrite filter
        assert "filters" in rule
        has_url_rewrite = any(f.get("type") == "URLRewrite" for f in rule["filters"])
        assert has_url_rewrite

        url_rewrite_filter = next(f for f in rule["filters"] if f.get("type") == "URLRewrite")
        assert url_rewrite_filter["urlRewrite"]["path"]["type"] == "ReplacePrefixMatch"
        assert url_rewrite_filter["urlRewrite"]["path"]["replacePrefixMatch"] == ""

        # === API: Delete port ===
        port_client.delete_port(name=port.name)

        # === K8s: Verify HTTPRoute deleted ===
        wait_for_port_httproute_deleted(
            namespace=namespace,
            engine_uid=engine.uid,
            port_id="9090",
            timeout_seconds=30,
        )

    finally:
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_list_ports(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_port_test3,
    sandbox_engine_image_port_test3,
):
    """
    Test listing ports:
    - API: ListPorts returns all created ports
    - K8s: Multiple Services are created for multiple ports
    """
    config.load_config()

    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    engine_id = f"port-list-{uuid.uuid4().hex[:8]}"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_port_test3.name,
            sandbox_engine_image=sandbox_engine_image_port_test3.name,
            display_name="List Ports Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        port_client = super_admin_clients.sandbox_clients.port_client

        # === API: Create multiple ports ===
        port1 = port_client.create_port(
            parent=engine.name,
            port=Port(display_name="Port 8081", public=False),
            port_id="8081",
        )
        port2 = port_client.create_port(
            parent=engine.name,
            port=Port(display_name="Port 8082", public=True),
            port_id="8082",
        )
        port3 = port_client.create_port(
            parent=engine.name,
            port=Port(display_name="Port 8083", public=False),
            port_id="8083",
        )

        # === API: List ports ===
        ports, next_page_token = port_client.list_ports(parent=engine.name, page_size=10)

        assert len(ports) >= 3
        port_names = {p.name for p in ports}
        assert port1.name in port_names
        assert port2.name in port_names
        assert port3.name in port_names

        # === K8s: Verify all Services created ===
        svc1 = wait_for_port_service(namespace, engine.uid, "8081", 30)
        svc2 = wait_for_port_service(namespace, engine.uid, "8082", 30)
        svc3 = wait_for_port_service(namespace, engine.uid, "8083", 30)

        assert svc1.spec.ports[0].port == 8081
        assert svc2.spec.ports[0].port == 8082
        assert svc3.spec.ports[0].port == 8083

        # Port 8082 is public, should have HTTPRoute
        route2 = wait_for_port_httproute(namespace, engine.uid, "8082", 30)
        assert route2 is not None

        # === Cleanup ===
        port_client.delete_port(name=port1.name)
        port_client.delete_port(name=port2.name)
        port_client.delete_port(name=port3.name)

    finally:
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_update_port(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_port_test4,
    sandbox_engine_image_port_test4,
):
    """
    Test updating a port:
    - API: UpdatePort changes display_name and public flag
    - K8s: HTTPRoute is created when port becomes public
    """
    config.load_config()

    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    engine_id = f"port-update-{uuid.uuid4().hex[:8]}"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_port_test4.name,
            sandbox_engine_image=sandbox_engine_image_port_test4.name,
            display_name="Update Port Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        port_client = super_admin_clients.sandbox_clients.port_client

        # === API: Create private port ===
        port = port_client.create_port(
            parent=engine.name,
            port=Port(display_name="Original Name", public=False),
            port_id="7070",
        )

        assert port.display_name == "Original Name"
        assert port.public is False

        # === K8s: Verify Service exists ===
        service = wait_for_port_service(namespace, engine.uid, "7070", 30)
        assert service is not None

        # === API: Update display_name ===
        port.display_name = "Updated Name"
        updated_port = port_client.update_port(port=port, update_mask=["display_name"])

        assert updated_port.display_name == "Updated Name"
        assert updated_port.public is False

        # === API: Update public flag to True ===
        updated_port.public = True
        updated_port = port_client.update_port(port=updated_port, update_mask=["public"])

        assert updated_port.display_name == "Updated Name"
        assert updated_port.public is True

        # === K8s: Verify HTTPRoute is now created ===
        route = wait_for_port_httproute(namespace, engine.uid, "7070", 30)
        assert route is not None

        # === Cleanup ===
        port_client.delete_port(name=port.name)

    finally:
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_port_service_has_endpoints(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_port_conn_test,
    sandbox_engine_image_port_conn_test,
):
    """
    Test that port Service has correct endpoints:
    - K8s: Endpoints contain the pod IP and correct port
    """
    config.load_config()

    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    engine_id = f"port-endpoints-{uuid.uuid4().hex[:8]}"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_port_conn_test.name,
            sandbox_engine_image=sandbox_engine_image_port_conn_test.name,
            display_name="Port Endpoints Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    try:
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        port_client = super_admin_clients.sandbox_clients.port_client

        # Create a port
        port = port_client.create_port(
            parent=engine.name,
            port=Port(display_name="Endpoints Test Port", public=False),
            port_id="8888",
        )

        # Wait for Service
        service = wait_for_port_service(namespace, engine.uid, "8888", 30)
        assert service is not None

        # Get Endpoints
        endpoints = wait_for_endpoints_ready(
            namespace=namespace,
            service_name=f"engine-{engine.uid}-port-8888",
            timeout_seconds=30,
        )

        assert endpoints is not None
        assert len(endpoints.subsets) > 0

        subset = endpoints.subsets[0]
        assert len(subset.addresses) > 0

        # Verify endpoint address matches pod IP
        pod = client.CoreV1Api().read_namespaced_pod(
            namespace=namespace,
            name=f"engine-{engine.uid}",
        )
        pod_ip = pod.status.pod_ip

        endpoint_ips = [addr.ip for addr in subset.addresses]
        assert pod_ip in endpoint_ips

        # Verify endpoint port
        assert len(subset.ports) > 0
        assert subset.ports[0].port == 8888

        # Cleanup
        port_client.delete_port(name=port.name)

    finally:
        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@pytest.mark.timeout(300)
def test_port_server_reachable_via_service(
    super_admin_clients,
    sandbox_engine_client_super_admin,
    sandbox_engine_template_port_server_test,
    sandbox_engine_image_port_server_test,
):
    """
    End-to-end connectivity test:
    - Start HTTP server in sandbox using process service
    - Create port for the server
    - Verify server is reachable via kubectl port-forward
    """
    config.load_config()

    workspace_id = "8cf6b17d-c018-48f0-8d05-cdd5fba22893"
    engine_id = f"port-server-{uuid.uuid4().hex[:8]}"
    namespace = os.getenv("TEST_K8S_WORKLOADS_NAMESPACE")

    engine = sandbox_engine_client_super_admin.create_sandbox_engine(
        parent=f"workspaces/{workspace_id}",
        sandbox_engine=SandboxEngine(
            sandbox_engine_template=sandbox_engine_template_port_server_test.name,
            sandbox_engine_image=sandbox_engine_image_port_server_test.name,
            display_name="Port Server Test Engine",
        ),
        sandbox_engine_id=engine_id,
    )

    port_forward_proc = None
    try:
        sandbox_engine_client_super_admin.wait(name=engine.name, timeout_seconds=120)
        engine = sandbox_engine_client_super_admin.get_sandbox_engine(name=engine.name)
        assert engine.state == SandboxEngineState.STATE_RUNNING

        process_client = super_admin_clients.sandbox_clients.process_client
        port_client = super_admin_clients.sandbox_clients.port_client

        # Start HTTP server using netcat
        server_script = (
            'while true; do '
            'printf "HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\n'
            'Hello from port 8765!" | nc -l -N 8765; '
            'done'
        )

        server_process = process_client.create_process(
            parent=engine.name,
            process=Process(command="sh", args=["-c", server_script]),
            process_id="http-server",
            auto_run=True,
        )

        time.sleep(2)

        # Verify process is running
        server_process = process_client.get_process(name=server_process.name)
        assert server_process.state.name == "STATE_RUNNING"

        # Create port for server
        port = port_client.create_port(
            parent=engine.name,
            port=Port(display_name="HTTP Server Port", public=False),
            port_id="8765",
        )

        # Wait for Service and Endpoints
        service = wait_for_port_service(namespace, engine.uid, "8765", 30)
        assert service is not None

        endpoints = wait_for_endpoints_ready(
            namespace=namespace,
            service_name=f"engine-{engine.uid}-port-8765",
            timeout_seconds=30,
        )
        assert endpoints is not None

        # Use kubectl port-forward
        local_port = 18765
        service_name = f"engine-{engine.uid}-port-8765"

        port_forward_proc = subprocess.Popen(
            [
                "kubectl", "port-forward",
                "-n", namespace,
                f"svc/{service_name}",
                f"{local_port}:8765",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        time.sleep(3)

        # Make HTTP request
        try:
            response = urllib.request.urlopen(
                f"http://localhost:{local_port}/",
                timeout=10,
            )
            body = response.read().decode("utf-8")
            assert "Hello from port 8765!" in body
        except urllib.error.URLError as e:
            pytest.fail(
                f"Failed to connect to server through port-forward: {e}. "
                f"Service: {service_name}, Endpoints: {endpoints}"
            )

        # Cleanup
        port_client.delete_port(name=port.name)
        process_client.send_signal(name=server_process.name, signal=15)

    finally:
        if port_forward_proc:
            port_forward_proc.terminate()
            port_forward_proc.wait(timeout=5)

        try:
            sandbox_engine_client_super_admin.delete_sandbox_engine(name=engine.name)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")
