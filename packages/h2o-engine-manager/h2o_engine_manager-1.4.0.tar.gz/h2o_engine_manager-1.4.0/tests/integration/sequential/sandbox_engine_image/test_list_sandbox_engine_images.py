from h2o_engine_manager.clients.base.image_pull_policy import ImagePullPolicy
from h2o_engine_manager.clients.sandbox_engine_image.image import SandboxEngineImage
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_list_sandbox_engine_images(
    sandbox_engine_image_client_super_admin,
    sandbox_engine_image_client_admin,
    sandbox_engine_image_client,
    delete_all_sandbox_engine_images_before_after,
):
    sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_image=SandboxEngineImage(
            image = "my-image-1",
            display_name = "display my image",
            image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_ALWAYS,
        ),
        sandbox_engine_image_id="img1",
    )
    sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_image=SandboxEngineImage(
            image = "my-image-2",
            image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_NEVER,
        ),
        sandbox_engine_image_id="img2",
    )
    sandbox_engine_image_client_super_admin.create_sandbox_engine_image(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_image=SandboxEngineImage(
            image = "my-image-3",
            image_pull_policy = ImagePullPolicy.IMAGE_PULL_POLICY_IF_NOT_PRESENT,
        ),
        sandbox_engine_image_id="img3",
    )

    images: list[SandboxEngineImage] = sandbox_engine_image_client.list_all_sandbox_engine_images(parent=GLOBAL_WORKSPACE)
    assert len(images) == 3
    assert images[0].name == "workspaces/global/sandboxEngineImages/img3"
    assert images[1].name == "workspaces/global/sandboxEngineImages/img2"
    assert images[2].name == "workspaces/global/sandboxEngineImages/img1"

    # test pagination
    page = sandbox_engine_image_client_super_admin.list_sandbox_engine_images(parent=GLOBAL_WORKSPACE, page_size=1)
    assert len(page.sandbox_engine_images) == 1
    assert page.sandbox_engine_images[0].name == "workspaces/global/sandboxEngineImages/img3"
    assert page.next_page_token != ""

    page = sandbox_engine_image_client_super_admin.list_sandbox_engine_images(
        parent=GLOBAL_WORKSPACE,
        page_size=1,
        page_token=page.next_page_token
    )
    assert len(page.sandbox_engine_images) == 1
    assert page.sandbox_engine_images[0].name == "workspaces/global/sandboxEngineImages/img2"
    assert page.next_page_token != ""

    page = sandbox_engine_image_client_super_admin.list_sandbox_engine_images(
        parent=GLOBAL_WORKSPACE,
        page_size=1,
        page_token=page.next_page_token
    )
    assert len(page.sandbox_engine_images) == 1
    assert page.sandbox_engine_images[0].name == "workspaces/global/sandboxEngineImages/img1"
    assert page.next_page_token == ""
