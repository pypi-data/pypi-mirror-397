import http

import pytest

from h2o_engine_manager.clients.exception import CustomApiException
from h2o_engine_manager.clients.notebook_engine_image.image import NotebookEngineImage


@pytest.fixture(scope="function")
def notebook_engine_image_i1(notebook_engine_image_client_super_admin):
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img1",
        ),
        notebook_engine_image_id="img1",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i2(notebook_engine_image_client_super_admin):
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img2",
        ),
        notebook_engine_image_id="img2",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i3(notebook_engine_image_client_super_admin):
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img3",
        ),
        notebook_engine_image_id="img3",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i4(notebook_engine_image_client_super_admin):
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img4",
        ),
        notebook_engine_image_id="img4",
    )
    name = created_image.name

    yield created_image

    # Image should be deleted during its usage in test case.
    # Check that image no longer exists.
    try:
        notebook_engine_image_client_super_admin.get_notebook_engine_image(name=name)
    except CustomApiException as exc:
        if exc.status == http.HTTPStatus.NOT_FOUND:
            return
        else:
            # Unexpected exception, re-raise.
            raise

    # In case version was found (test failed before it was deleted), delete it.
    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i5(notebook_engine_image_client_super_admin):
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img5",
        ),
        notebook_engine_image_id="img5",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i6(notebook_engine_image_client_super_admin):
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img5",
        ),
        notebook_engine_image_id="img5",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


# Workspace resource labels/annotations test fixtures
# Each test needs unique image following the Python test isolation principle

@pytest.fixture(scope="function")
def notebook_engine_image_i7(notebook_engine_image_client_super_admin):
    """Image for workspace no resources test."""
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img7",
        ),
        notebook_engine_image_id="img7",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i8(notebook_engine_image_client_super_admin):
    """Image for workspace only labels test."""
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img8",
        ),
        notebook_engine_image_id="img8",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i9(notebook_engine_image_client_super_admin):
    """Image for workspace only annotations test."""
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img9",
        ),
        notebook_engine_image_id="img9",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i10(notebook_engine_image_client_super_admin):
    """Image for workspace both labels and annotations with pod template test."""
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img10",
        ),
        notebook_engine_image_id="img10",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i11(notebook_engine_image_client_super_admin):
    """Image for workspace conflict test."""
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img11",
        ),
        notebook_engine_image_id="img11",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i12(notebook_engine_image_client_super_admin):
    """Image for resume non-conflicting test."""
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img12",
        ),
        notebook_engine_image_id="img12",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)


@pytest.fixture(scope="function")
def notebook_engine_image_i13(notebook_engine_image_client_super_admin):
    """Image for resume conflicting test."""
    created_image = notebook_engine_image_client_super_admin.create_notebook_engine_image(
        parent="workspaces/global",
        notebook_engine_image=NotebookEngineImage(
            image="img13",
        ),
        notebook_engine_image_id="img13",
    )
    name = created_image.name

    yield created_image

    notebook_engine_image_client_super_admin.delete_notebook_engine_image(name=name)

