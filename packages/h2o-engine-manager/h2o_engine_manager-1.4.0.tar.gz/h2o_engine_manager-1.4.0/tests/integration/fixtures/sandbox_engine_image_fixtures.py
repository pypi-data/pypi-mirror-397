import http

import pytest

from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.sandbox_engine_image.image import SandboxEngineImage


@pytest.fixture(scope="function")
def sandbox_engine_image_i1(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="sandbox-img1",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_i2(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
        ),
        sandbox_engine_image_id="sandbox-img2",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_k8s_test1(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-k8s-test1",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_k8s_test2(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-k8s-test2",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_k8s_test3(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-k8s-test3",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_k8s_test4(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-k8s-test4",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_test1(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-test1",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_test2(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-test2",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_test3(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-test3",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_test4(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-test4",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_test5(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-test5",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_test6(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-test6",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_test7(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-test7",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_test8(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-test8",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_auth_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-auth-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_state_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-state-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_fs_validation_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-fs-validation-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_process_test1(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-process-test1",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_process_test2(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-process-test2",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_process_test3(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-process-test3",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_process_test4(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-process-test4",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_process_test5(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-process-test5",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_process_test6(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-process-test6",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_process_auth_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-process-auth-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_process_state_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-process-state-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_process_validation_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-process-validation-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_ws_resource1(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-ws-resource1",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_ws_resource2(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-ws-resource2",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_ws_resource3(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-ws-resource3",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_ws_resource4(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-ws-resource4",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_ws_resource5(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-ws-resource5",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_secure_store_test1(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-secure-store-test1",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_secure_store_test2(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-secure-store-test2",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_secure_store_test3(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-secure-store-test3",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_port_test1(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-port-test1",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_port_test2(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-port-test2",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_port_test3(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-port-test3",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_port_test4(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-port-test4",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_port_auth_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-port-auth-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_port_state_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-port-state-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_port_validation_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-port-validation-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_port_num_validation_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-port-num-validation-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_port_conn_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-port-conn-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_port_server_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-port-server-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_metrics_test1(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-metrics-test1",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_drive_test1(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-drive-test1",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_drive_test2(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-drive-test2",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_drive_auth_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-drive-auth-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_drive_state_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-drive-state-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)


@pytest.fixture(scope="function")
def sandbox_engine_image_drive_validation_test(sandbox_engine_image_client_super_admin):
    created_image = sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent="workspaces/global",
        sandbox_engine_image=SandboxEngineImage(
            image="353750902984.dkr.ecr.us-east-1.amazonaws.com/h2oai-sandbox-mock:latest-snapshot",
            image_pull_secrets=["regcred"],
            image_pull_policy=ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="image-drive-validation-test",
    )
    name = created_image.name

    yield created_image

    sandbox_engine_image_client_super_admin.delete_sandbox_engine_image(name=name)