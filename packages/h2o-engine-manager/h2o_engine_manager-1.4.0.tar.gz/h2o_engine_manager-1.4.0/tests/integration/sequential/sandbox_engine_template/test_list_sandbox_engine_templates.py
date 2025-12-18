from h2o_engine_manager.clients.sandbox_engine_template.template import (
    SandboxEngineTemplate,
)
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_list_sandbox_engine_templates(
    sandbox_engine_template_client_super_admin,
    sandbox_engine_template_client_admin,
    sandbox_engine_template_client,
    delete_all_sandbox_engine_templates_before_after,
):
    sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_template=SandboxEngineTemplate(
            memory_bytes_limit="2Gi",
            max_idle_duration="1h",
            display_name="template 1",
            milli_cpu_request=500,
            milli_cpu_limit=1000,
        ),
        sandbox_engine_template_id="tmpl1",
    )
    sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_template=SandboxEngineTemplate(
            memory_bytes_limit="4Gi",
            max_idle_duration="2h",
            display_name="template 2",
            milli_cpu_request=1000,
            milli_cpu_limit=2000,
        ),
        sandbox_engine_template_id="tmpl2",
    )
    sandbox_engine_template_client_super_admin.create_sandbox_engine_template(
        parent=GLOBAL_WORKSPACE,
        sandbox_engine_template=SandboxEngineTemplate(
            memory_bytes_limit="8Gi",
            max_idle_duration="3h",
            display_name="template 3",
            milli_cpu_request=2000,
            milli_cpu_limit=4000,
        ),
        sandbox_engine_template_id="tmpl3",
    )

    templates: list[SandboxEngineTemplate] = (
        sandbox_engine_template_client.list_all_sandbox_engine_templates(
            parent=GLOBAL_WORKSPACE
        )
    )
    assert len(templates) == 3
    assert templates[0].name == "workspaces/global/sandboxEngineTemplates/tmpl3"
    assert templates[1].name == "workspaces/global/sandboxEngineTemplates/tmpl2"
    assert templates[2].name == "workspaces/global/sandboxEngineTemplates/tmpl1"

    # test pagination
    page = sandbox_engine_template_client_super_admin.list_sandbox_engine_templates(
        parent=GLOBAL_WORKSPACE, page_size=1
    )
    assert len(page.sandbox_engine_templates) == 1
    assert (
        page.sandbox_engine_templates[0].name
        == "workspaces/global/sandboxEngineTemplates/tmpl3"
    )
    assert page.next_page_token != ""

    page = sandbox_engine_template_client_super_admin.list_sandbox_engine_templates(
        parent=GLOBAL_WORKSPACE, page_size=1, page_token=page.next_page_token
    )
    assert len(page.sandbox_engine_templates) == 1
    assert (
        page.sandbox_engine_templates[0].name
        == "workspaces/global/sandboxEngineTemplates/tmpl2"
    )
    assert page.next_page_token != ""

    page = sandbox_engine_template_client_super_admin.list_sandbox_engine_templates(
        parent=GLOBAL_WORKSPACE, page_size=1, page_token=page.next_page_token
    )
    assert len(page.sandbox_engine_templates) == 1
    assert (
        page.sandbox_engine_templates[0].name
        == "workspaces/global/sandboxEngineTemplates/tmpl1"
    )
    assert page.next_page_token == ""