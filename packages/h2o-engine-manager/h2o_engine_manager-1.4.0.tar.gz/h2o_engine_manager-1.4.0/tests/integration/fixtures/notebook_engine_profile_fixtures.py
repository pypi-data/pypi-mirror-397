import pytest

from h2o_engine_manager.clients.constraint.profile_constraint_duration import (
    ProfileConstraintDuration,
)
from h2o_engine_manager.clients.constraint.profile_constraint_numeric import (
    ProfileConstraintNumeric,
)
from h2o_engine_manager.clients.notebook_engine_profile.profile import (
    NotebookEngineProfile,
)


@pytest.fixture(scope="function")
def notebook_engine_profile_p1(notebook_engine_profile_client_super_admin):
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0", maximum="10", cumulative_maximum="100"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h", maximum="200h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
            storage_class_name="sc1",
            gpu_resource_name="amd.com/gpu",
        ),
        notebook_engine_profile_id="p1",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p2(notebook_engine_profile_client_super_admin):
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0", maximum="10", cumulative_maximum="100"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h", maximum="200h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
        ),
        notebook_engine_profile_id="p2",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p3(notebook_engine_profile_client_super_admin):
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1", maximum="3"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0", maximum="3", cumulative_maximum="100"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi", maximum="2Gi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi", maximum="2Gi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h", maximum="8h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h", maximum="8h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
            storage_class_name="sc3",
        ),
        notebook_engine_profile_id="p3",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p4(notebook_engine_profile_client_super_admin):
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1", maximum="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0", maximum="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi", maximum="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi", maximum="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="4h", default="4h", maximum="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="4h", default="4h", maximum="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
            storage_class_name="sc4",
        ),
        notebook_engine_profile_id="p4",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p5(notebook_engine_profile_client_super_admin):
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1", maximum="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0", maximum="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi", maximum="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="40Mi", maximum="80Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="4h", default="4h", maximum="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="4h", default="4h", maximum="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
            storage_class_name="sc4",
        ),
        notebook_engine_profile_id="p4",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


# Workspace resource labels/annotations test fixtures

@pytest.fixture(scope="function")
def notebook_engine_profile_p6(notebook_engine_profile_client_super_admin):
    """Profile without yaml_pod_template_spec for workspace resource labels test."""
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
        ),
        notebook_engine_profile_id="p6",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p7(notebook_engine_profile_client_super_admin):
    """Profile without yaml_pod_template_spec for workspace only labels test."""
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
        ),
        notebook_engine_profile_id="p7",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p8(notebook_engine_profile_client_super_admin):
    """Profile without yaml_pod_template_spec for workspace only annotations test."""
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
        ),
        notebook_engine_profile_id="p8",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p9(notebook_engine_profile_client_super_admin):
    """Profile with yaml_pod_template_spec (non-conflicting) for workspace labels+annotations test."""
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
            yaml_pod_template_spec="""
                metadata:
                  labels:
                    profile-label: profile-value
                  annotations:
                    profile-annotation: profile-value
                spec:
                  containers:
                    - name: notebook
            """,
        ),
        notebook_engine_profile_id="p9",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p10(notebook_engine_profile_client_super_admin):
    """Profile with yaml_pod_template_spec that conflicts with workspace resources."""
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
            yaml_pod_template_spec="""
                metadata:
                  labels:
                    lbl1: conflict-value
                spec:
                  containers:
                    - name: notebook
            """,
        ),
        notebook_engine_profile_id="p10",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p11(notebook_engine_profile_client_super_admin):
    """Profile for resume test (non-conflicting)."""
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
        ),
        notebook_engine_profile_id="p11",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p12(notebook_engine_profile_client_super_admin):
    """Profile for resume test with non-conflicting yaml_pod_template_spec."""
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
            yaml_pod_template_spec="""
                metadata:
                  labels:
                    resume-profile-label: resume-value
                  annotations:
                    resume-profile-annotation: resume-value
                spec:
                  containers:
                    - name: notebook
            """,
        ),
        notebook_engine_profile_id="p12",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p13(notebook_engine_profile_client_super_admin):
    """Profile for resume conflict test (initial profile without conflict)."""
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
        ),
        notebook_engine_profile_id="p13",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)


@pytest.fixture(scope="function")
def notebook_engine_profile_p14(notebook_engine_profile_client_super_admin):
    """Profile for resume conflict test with conflicting yaml_pod_template_spec."""
    created_profile = notebook_engine_profile_client_super_admin.create_notebook_engine_profile(
        parent="workspaces/global",
        notebook_engine_profile=NotebookEngineProfile(
            cpu_constraint=ProfileConstraintNumeric(minimum="1", default="1"),
            gpu_constraint=ProfileConstraintNumeric(minimum="0", default="0"),
            memory_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            storage_bytes_constraint=ProfileConstraintNumeric(minimum="20Mi", default="20Mi"),
            max_idle_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            max_running_duration_constraint=ProfileConstraintDuration(minimum="5m", default="4h"),
            enabled=True,
            assigned_oidc_roles_enabled=False,
            yaml_pod_template_spec="""
                metadata:
                  labels:
                    lbl1: resume-conflict-value
                spec:
                  containers:
                    - name: notebook
            """,
        ),
        notebook_engine_profile_id="p14",
    )
    name = created_profile.name

    yield created_profile

    notebook_engine_profile_client_super_admin.delete_notebook_engine_profile(name=name)
