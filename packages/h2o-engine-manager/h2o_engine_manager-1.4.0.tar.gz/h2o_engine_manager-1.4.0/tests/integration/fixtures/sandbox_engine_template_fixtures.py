import pytest

from h2o_engine_manager.clients.sandbox_engine_template.template import (
    SandboxEngineTemplate,
)


@pytest.fixture(scope="function")
def sandbox_engine_template_t1(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Template T1",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-t1",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_t2(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Template T2",
            milli_cpu_request=200,
            milli_cpu_limit=400,
            memory_bytes_request="20Mi",
            memory_bytes_limit="40Mi",
            storage_bytes="20Mi",
            max_idle_duration="2h",
            gpu_resource="amd.com/gpu",
            gpu=1,
            enabled=True,
        ),
        sandbox_engine_template_id="template-t2",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_k8s_test1(sandbox_engine_template_client_super_admin):
    yaml_pod_template_spec = """
spec:
  containers:
  - name: sandbox
    env:
    - name: POD_TEMPLATE_TEST_VAR
      value: "custom-test-value"
"""
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="K8s Test Template 1",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
            yaml_pod_template_spec=yaml_pod_template_spec,
        ),
        sandbox_engine_template_id="template-k8s-test1",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_k8s_test2(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="K8s Test Template 2",
            milli_cpu_request=200,
            milli_cpu_limit=400,
            memory_bytes_request="20Mi",
            memory_bytes_limit="40Mi",
            storage_bytes="20Mi",
            max_idle_duration="2h",
            gpu_resource="amd.com/gpu",
            gpu=1,
            enabled=True,
        ),
        sandbox_engine_template_id="template-k8s-test2",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_k8s_test3(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="K8s Test Template 3",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-k8s-test3",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_k8s_test4(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="K8s Test Template 4",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-k8s-test4",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_test1(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem Test Template 1",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-test1",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_test2(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem Test Template 2",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-test2",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_test3(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem Test Template 3",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-test3",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_test4(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem Test Template 4",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-test4",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_test5(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem Test Template 5",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-test5",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_test6(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem Test Template 6",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-test6",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_test7(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem Test Template 7",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-test7",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_test8(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem Test Template 8",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-test8",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_auth_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem Auth Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-auth-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_state_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem State Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-state-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_fs_validation_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Filesystem Validation Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-fs-validation-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_process_test1(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Process Test Template 1",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="100Mi",
            memory_bytes_limit="200Mi",
            storage_bytes="100Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-process-test1",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_process_test2(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Process Test Template 2",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-process-test2",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_process_test3(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Process Test Template 3",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-process-test3",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_process_test4(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Process Test Template 4",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-process-test4",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_process_test5(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Process Test Template 5",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-process-test5",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_process_auth_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Process Auth Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-process-auth-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_process_state_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Process State Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-process-state-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_process_validation_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Process Validation Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-process-validation-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_ws_resource1(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Workspace Resource Template 1",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-ws-resource1",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_ws_resource2(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Workspace Resource Template 2",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-ws-resource2",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_ws_resource3(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Workspace Resource Template 3",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-ws-resource3",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_ws_resource4(sandbox_engine_template_client_super_admin):
    yaml_pod_template_spec = """
metadata:
  labels:
    profile-label: "profile-value"
  annotations:
    profile-annotation: "profile-value"
"""
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Workspace Resource Template 4",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
            yaml_pod_template_spec=yaml_pod_template_spec,
        ),
        sandbox_engine_template_id="template-ws-resource4",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_ws_resource5(sandbox_engine_template_client_super_admin):
    yaml_pod_template_spec = """
metadata:
  labels:
    lbl1: "conflict-value"
"""
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Workspace Resource Template 5",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
            yaml_pod_template_spec=yaml_pod_template_spec,
        ),
        sandbox_engine_template_id="template-ws-resource5",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_process_test6(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Process Test Template 6",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-process-test6",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_secure_store_test1(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Secure Store Test Template 1",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-secure-store-test1",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_secure_store_test2(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Secure Store Test Template 2",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-secure-store-test2",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_secure_store_test3(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Secure Store Test Template 3",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-secure-store-test3",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_port_test1(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Port Test Template 1",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-port-test1",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_port_test2(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Port Test Template 2",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-port-test2",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_port_test3(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Port Test Template 3",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-port-test3",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_port_test4(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Port Test Template 4",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-port-test4",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_port_auth_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Port Auth Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-port-auth-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_port_state_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Port State Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-port-state-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_port_validation_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Port Validation Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-port-validation-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_port_num_validation_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Port Number Validation Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-port-num-validation-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_port_conn_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Port Connectivity Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-port-conn-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_port_server_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Port Server Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-port-server-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_metrics_test1(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Metrics Test Template 1",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-metrics-test1",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_drive_test1(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Drive Test Template 1",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-drive-test1",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_drive_test2(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Drive Test Template 2",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-drive-test2",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_drive_auth_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Drive Auth Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-drive-auth-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_drive_state_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Drive State Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-drive-state-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_template_drive_validation_test(sandbox_engine_template_client_super_admin):
    created_template = sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent="workspaces/global",
        sandbox_engine_template=SandboxEngineTemplate(
            display_name="Drive Validation Test Template",
            milli_cpu_request=100,
            milli_cpu_limit=200,
            memory_bytes_request="10Mi",
            memory_bytes_limit="20Mi",
            storage_bytes="10Mi",
            max_idle_duration="4h",
            gpu_resource="nvidia.com/gpu",
            gpu=0,
            enabled=True,
        ),
        sandbox_engine_template_id="template-drive-validation-test",
    )
    name = created_template.name

    yield created_template

    sandbox_engine_template_client_super_admin.delete_sandbox_engine_template(name=name)