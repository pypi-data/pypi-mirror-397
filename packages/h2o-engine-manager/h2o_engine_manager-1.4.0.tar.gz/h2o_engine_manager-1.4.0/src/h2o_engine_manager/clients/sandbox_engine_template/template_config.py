from typing import Dict
from typing import Optional

from h2o_engine_manager.clients.sandbox_engine_template.template import (
    SandboxEngineTemplate,
)


class SandboxEngineTemplateConfig:
    """
    SandboxEngineTemplate configuration used as input for apply method.
    """

    def __init__(
        self,
        sandbox_engine_template_id: str,
        memory_bytes_limit: str,
        max_idle_duration: str,
        display_name: str = "",
        milli_cpu_request: int = 0,
        milli_cpu_limit: int = 0,
        gpu_resource: str = "",
        gpu: int = 0,
        memory_bytes_request: str = "0",
        storage_bytes: str = "0",
        environmental_variables: Optional[Dict[str, str]] = None,
        yaml_pod_template_spec: str = "",
        enabled: bool = True,
    ):
        self.sandbox_engine_template_id = sandbox_engine_template_id
        self.memory_bytes_limit = memory_bytes_limit
        self.max_idle_duration = max_idle_duration
        self.display_name = display_name
        self.milli_cpu_request = milli_cpu_request
        self.milli_cpu_limit = milli_cpu_limit
        self.gpu_resource = gpu_resource
        self.gpu = gpu
        self.memory_bytes_request = memory_bytes_request
        self.storage_bytes = storage_bytes
        self.environmental_variables = environmental_variables
        self.yaml_pod_template_spec = yaml_pod_template_spec
        self.enabled = enabled

    def to_sandbox_engine_template(self):
        return SandboxEngineTemplate(
            memory_bytes_limit=self.memory_bytes_limit,
            max_idle_duration=self.max_idle_duration,
            display_name=self.display_name,
            milli_cpu_request=self.milli_cpu_request,
            milli_cpu_limit=self.milli_cpu_limit,
            gpu_resource=self.gpu_resource,
            gpu=self.gpu,
            memory_bytes_request=self.memory_bytes_request,
            storage_bytes=self.storage_bytes,
            environmental_variables=self.environmental_variables,
            yaml_pod_template_spec=self.yaml_pod_template_spec,
            enabled=self.enabled,
        )