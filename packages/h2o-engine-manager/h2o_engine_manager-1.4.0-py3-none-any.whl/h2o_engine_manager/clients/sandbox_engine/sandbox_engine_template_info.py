import pprint
from datetime import datetime
from typing import Dict
from typing import Optional

from h2o_engine_manager.clients.convert import duration_convertor
from h2o_engine_manager.clients.convert import quantity_convertor
from h2o_engine_manager.gen.model.v1_sandbox_engine_template_info import (
    V1SandboxEngineTemplateInfo,
)


class SandboxEngineTemplateInfo:
    """
    The original SandboxEngineTemplate data used by SandboxEngine when using the SandboxEngineTemplate.
    """

    def __init__(
        self,
        name: str = "",
        display_name: str = "",
        milli_cpu_request: int = 0,
        milli_cpu_limit: int = 0,
        gpu_resource: str = "",
        gpu: int = 0,
        memory_bytes_request: str = "0",
        memory_bytes_limit: str = "0",
        storage_bytes: str = "0",
        storage_class_name: str = "",
        environmental_variables: Optional[Dict[str, str]] = None,
        yaml_pod_template_spec: str = "",
        enabled: bool = True,
        max_idle_duration: str = "0s",
        create_time: Optional[datetime] = None,
        update_time: Optional[datetime] = None,
        creator: str = "",
        updater: str = "",
        creator_display_name: str = "",
        updater_display_name: str = "",
    ):
        """
        SandboxEngineTemplateInfo represents the original SandboxEngineTemplate data.

        Args:
            name: Resource name.
            display_name: Human-readable name.
            milli_cpu_request: CPU request in milli-cpu units.
            milli_cpu_limit: CPU limit in milli-cpu units.
            gpu_resource: GPU resource type.
            gpu: Number of GPUs.
            memory_bytes_request: Memory request.
            memory_bytes_limit: Memory limit.
            storage_bytes: Storage size.
            storage_class_name: Storage class name.
            environmental_variables: Environment variables.
            yaml_pod_template_spec: YAML pod template spec.
            enabled: Whether the template is enabled.
            max_idle_duration: Maximum idle duration.
            create_time: Creation timestamp.
            update_time: Last update timestamp.
            creator: Creator identifier.
            updater: Last updater identifier.
            creator_display_name: Creator display name.
            updater_display_name: Last updater display name.
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
        self.storage_class_name = storage_class_name
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


def sandbox_engine_template_info_from_api_object(
    api_object: Optional[V1SandboxEngineTemplateInfo],
) -> Optional[SandboxEngineTemplateInfo]:
    if api_object is None:
        return None

    return SandboxEngineTemplateInfo(
        name=api_object.name,
        display_name=api_object.display_name,
        milli_cpu_request=api_object.milli_cpu_request,
        milli_cpu_limit=api_object.milli_cpu_limit,
        gpu_resource=api_object.gpu_resource,
        gpu=api_object.gpu,
        memory_bytes_request=quantity_convertor.number_str_to_quantity(
            api_object.memory_bytes_request
        ),
        memory_bytes_limit=quantity_convertor.number_str_to_quantity(
            api_object.memory_bytes_limit
        ),
        storage_bytes=quantity_convertor.number_str_to_quantity(
            api_object.storage_bytes
        ),
        storage_class_name=api_object.storage_class_name,
        environmental_variables=api_object.environmental_variables,
        yaml_pod_template_spec=api_object.yaml_pod_template_spec,
        enabled=api_object.enabled,
        max_idle_duration=duration_convertor.seconds_to_duration(
            api_object.max_idle_duration
        ),
        create_time=api_object.create_time,
        update_time=api_object.update_time,
        creator=api_object.creator,
        updater=api_object.updater,
        creator_display_name=api_object.creator_display_name,
        updater_display_name=api_object.updater_display_name,
    )