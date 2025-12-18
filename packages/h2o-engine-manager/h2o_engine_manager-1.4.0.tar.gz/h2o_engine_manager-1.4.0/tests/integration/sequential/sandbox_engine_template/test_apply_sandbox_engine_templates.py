from typing import List

from h2o_engine_manager.clients.sandbox_engine_template.template import (
    SandboxEngineTemplate,
)
from h2o_engine_manager.clients.sandbox_engine_template.template_config import (
    SandboxEngineTemplateConfig,
)
from tests.integration.conftest import GLOBAL_WORKSPACE


def test_apply_sandbox_engine_templates_super_admin(
    sandbox_engine_template_client_super_admin,
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
    templates = (
        sandbox_engine_template_client_super_admin.list_all_sandbox_engine_templates(
            parent=GLOBAL_WORKSPACE
        )
    )
    assert len(templates) == 2
    assert templates[0].name == "workspaces/global/sandboxEngineTemplates/tmpl2"
    assert templates[1].name == "workspaces/global/sandboxEngineTemplates/tmpl1"
    assert templates[1].display_name == "template 1"

    configs: List[SandboxEngineTemplateConfig] = [
        SandboxEngineTemplateConfig(
            sandbox_engine_template_id="t1",
            memory_bytes_limit="2Gi",
            max_idle_duration="1h",
            display_name="config template 1",
            milli_cpu_request=500,
            milli_cpu_limit=1000,
        ),
        SandboxEngineTemplateConfig(
            sandbox_engine_template_id="t2",
            memory_bytes_limit="4Gi",
            max_idle_duration="2h",
            display_name="config template 2",
            milli_cpu_request=1000,
            milli_cpu_limit=2000,
        ),
        SandboxEngineTemplateConfig(
            sandbox_engine_template_id="t3",
            memory_bytes_limit="8Gi",
            max_idle_duration="3h",
            display_name="config template 3",
            milli_cpu_request=2000,
            milli_cpu_limit=4000,
        ),
    ]

    # When applying SandboxEngineTemplate configs.
    applied_templates: list[
        SandboxEngineTemplate
    ] = sandbox_engine_template_client_super_admin.apply_sandbox_engine_template_configs(
        configs=configs
    )

    # Then only applied templates exist with specified params.
    assert len(applied_templates) == 3
    assert applied_templates[0].name == "workspaces/global/sandboxEngineTemplates/t3"
    assert applied_templates[0].display_name == "config template 3"
    assert applied_templates[0].memory_bytes_limit == "8Gi"
    assert applied_templates[0].max_idle_duration == "3h"
    assert applied_templates[0].milli_cpu_request == 2000
    assert applied_templates[0].milli_cpu_limit == 4000
    assert applied_templates[0].enabled is True

    assert applied_templates[1].name == "workspaces/global/sandboxEngineTemplates/t2"
    assert applied_templates[1].display_name == "config template 2"
    assert applied_templates[1].memory_bytes_limit == "4Gi"
    assert applied_templates[1].max_idle_duration == "2h"
    assert applied_templates[1].milli_cpu_request == 1000
    assert applied_templates[1].milli_cpu_limit == 2000

    assert applied_templates[2].name == "workspaces/global/sandboxEngineTemplates/t1"
    assert applied_templates[2].display_name == "config template 1"
    assert applied_templates[2].memory_bytes_limit == "2Gi"
    assert applied_templates[2].max_idle_duration == "1h"
    assert applied_templates[2].milli_cpu_request == 500
    assert applied_templates[2].milli_cpu_limit == 1000