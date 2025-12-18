import pprint
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

from h2o_engine_manager.clients.convert import duration_convertor
from h2o_engine_manager.clients.convert import quantity_convertor
from h2o_engine_manager.gen.model.required_sandbox_engine_template_resource import (
    RequiredSandboxEngineTemplateResource,
)
from h2o_engine_manager.gen.model.v1_sandbox_engine_template import (
    V1SandboxEngineTemplate,
)


class SandboxEngineTemplate:
    """
    SandboxEngineTemplate represents a compute template for SandboxEngine.
    """

    def __init__(
        self,
        memory_bytes_limit: str,
        max_idle_duration: str,
        name: str = "",
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
        create_time: Optional[datetime] = None,
        update_time: Optional[datetime] = None,
        creator: str = "",
        updater: str = "",
        creator_display_name: str = "",
        updater_display_name: str = "",
    ):
        """
        SandboxEngineTemplate represents a compute template for SandboxEngine.

        Args:
            memory_bytes_limit: Max memory in bytes a SandboxEngine is allowed to use.
            max_idle_duration: Maximum time a SandboxEngine can be idle before it is automatically terminated.
            name: Resource name. Format "workspaces/*/sandboxEngineTemplates/*".
            display_name: Human-readable name of the SandboxEngineTemplate.
            milli_cpu_request: MilliCPU units that will be reserved for the SandboxEngine.
            milli_cpu_limit: Maximum MilliCPU units a SandboxEngine is allowed to use.
            gpu_resource: Kubernetes GPU resource name (e.g., "nvidia.com/gpu").
            gpu: The amount of GPU units requested by this SandboxEngine.
            memory_bytes_request: Memory in bytes that will be reserved for the SandboxEngine.
            storage_bytes: External ephemeral storage in bytes.
            environmental_variables: Map of environmental variables.
            yaml_pod_template_spec: YAML representation of custom PodTemplateSpec.
            enabled: Whether the SandboxEngineTemplate is enabled.
            create_time: Time when the SandboxEngineTemplate was created.
            update_time: Time when the SandboxEngineTemplate was last updated.
            creator: Name of entity that created the SandboxEngineTemplate.
            updater: Name of entity that last updated the SandboxEngineTemplate.
            creator_display_name: Human-readable name of entity that created the SandboxEngineTemplate.
            updater_display_name: Human-readable name of entity that last updated the SandboxEngineTemplate.
        """
        if environmental_variables is None:
            environmental_variables = {}

        self.name = name
        self.display_name = display_name
        self.milli_cpu_request = milli_cpu_request
        self.milli_cpu_limit = milli_cpu_limit
        self.gpu_resource = gpu_resource
        self.gpu = gpu
        self.memory_bytes_request = memory_bytes_request
        self.memory_bytes_limit = memory_bytes_limit
        self.storage_bytes = storage_bytes
        self.environmental_variables = environmental_variables
        self.yaml_pod_template_spec = yaml_pod_template_spec
        self.enabled = enabled
        self.max_idle_duration = max_idle_duration
        self.create_time = create_time
        self.update_time = update_time
        self.creator = creator
        self.updater = updater
        self.creator_display_name = creator_display_name
        self.updater_display_name = updater_display_name

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def to_api_object(self) -> V1SandboxEngineTemplate:
        memory_bytes_request = quantity_convertor.quantity_to_number_str(
            self.memory_bytes_request
        )
        memory_bytes_limit = quantity_convertor.quantity_to_number_str(
            self.memory_bytes_limit
        )
        storage_bytes = quantity_convertor.quantity_to_number_str(self.storage_bytes)
        max_idle_duration = duration_convertor.duration_to_seconds(
            self.max_idle_duration
        )

        return V1SandboxEngineTemplate(
            display_name=self.display_name,
            milli_cpu_request=self.milli_cpu_request,
            milli_cpu_limit=self.milli_cpu_limit,
            gpu_resource=self.gpu_resource,
            gpu=self.gpu,
            memory_bytes_request=memory_bytes_request,
            memory_bytes_limit=memory_bytes_limit,
            storage_bytes=storage_bytes,
            environmental_variables=self.environmental_variables,
            yaml_pod_template_spec=self.yaml_pod_template_spec,
            enabled=self.enabled,
            max_idle_duration=max_idle_duration,
        )

    def to_resource(self) -> RequiredSandboxEngineTemplateResource:
        memory_bytes_request = quantity_convertor.quantity_to_number_str(
            self.memory_bytes_request
        )
        memory_bytes_limit = quantity_convertor.quantity_to_number_str(
            self.memory_bytes_limit
        )
        storage_bytes = quantity_convertor.quantity_to_number_str(self.storage_bytes)
        max_idle_duration = duration_convertor.duration_to_seconds(
            self.max_idle_duration
        )

        return RequiredSandboxEngineTemplateResource(
            display_name=self.display_name,
            milli_cpu_request=self.milli_cpu_request,
            milli_cpu_limit=self.milli_cpu_limit,
            gpu_resource=self.gpu_resource,
            gpu=self.gpu,
            memory_bytes_request=memory_bytes_request,
            memory_bytes_limit=memory_bytes_limit,
            storage_bytes=storage_bytes,
            environmental_variables=self.environmental_variables,
            yaml_pod_template_spec=self.yaml_pod_template_spec,
            enabled=self.enabled,
            max_idle_duration=max_idle_duration,
        )


def from_api_object(api_object: V1SandboxEngineTemplate) -> SandboxEngineTemplate:
    return SandboxEngineTemplate(
        memory_bytes_limit=quantity_convertor.number_str_to_quantity(
            api_object.memory_bytes_limit
        ),
        max_idle_duration=duration_convertor.seconds_to_duration(
            api_object.max_idle_duration
        ),
        name=api_object.name,
        display_name=api_object.display_name,
        milli_cpu_request=api_object.milli_cpu_request,
        milli_cpu_limit=api_object.milli_cpu_limit,
        gpu_resource=api_object.gpu_resource,
        gpu=api_object.gpu,
        memory_bytes_request=quantity_convertor.number_str_to_quantity(
            api_object.memory_bytes_request
        ),
        storage_bytes=quantity_convertor.number_str_to_quantity(
            api_object.storage_bytes
        ),
        environmental_variables=api_object.environmental_variables,
        yaml_pod_template_spec=api_object.yaml_pod_template_spec,
        enabled=api_object.enabled,
        create_time=api_object.create_time,
        update_time=api_object.update_time,
        creator=api_object.creator,
        updater=api_object.updater,
        creator_display_name=api_object.creator_display_name,
        updater_display_name=api_object.updater_display_name,
    )


def from_api_objects(
    api_objects: List[V1SandboxEngineTemplate],
) -> List[SandboxEngineTemplate]:
    return [from_api_object(api_object) for api_object in api_objects]