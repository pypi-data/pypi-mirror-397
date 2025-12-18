import pprint
from datetime import datetime
from typing import Dict
from typing import Optional

from h2o_engine_manager.clients.convert.duration_convertor import (
    optional_seconds_to_duration,
)
from h2o_engine_manager.clients.sandbox_engine.sandbox_engine_image_info import (
    SandboxEngineImageInfo,
)
from h2o_engine_manager.clients.sandbox_engine.sandbox_engine_image_info import (
    sandbox_engine_image_info_from_api_object,
)
from h2o_engine_manager.clients.sandbox_engine.sandbox_engine_template_info import (
    SandboxEngineTemplateInfo,
)
from h2o_engine_manager.clients.sandbox_engine.sandbox_engine_template_info import (
    sandbox_engine_template_info_from_api_object,
)
from h2o_engine_manager.clients.sandbox_engine.state import SandboxEngineState
from h2o_engine_manager.clients.sandbox_engine.state import (
    sandbox_engine_state_from_api_object,
)
from h2o_engine_manager.gen.model.v1_sandbox_engine import V1SandboxEngine


class SandboxEngine:
    """
    SandboxEngine represents a sandbox environment for running custom code.
    """

    def __init__(
        self,
        sandbox_engine_image: str,
        sandbox_engine_template: str,
        name: str = "",
        display_name: str = "",
        uid: str = "",
        state: SandboxEngineState = SandboxEngineState.STATE_UNSPECIFIED,
        creator: str = "",
        creator_display_name: str = "",
        create_time: Optional[datetime] = None,
        sandbox_engine_image_info: Optional[SandboxEngineImageInfo] = None,
        sandbox_engine_template_info: Optional[SandboxEngineTemplateInfo] = None,
        current_idle_duration: Optional[str] = None,
        annotations: Optional[Dict[str, str]] = None,
    ):
        """
        SandboxEngine represents a sandbox environment.

        Args:
            sandbox_engine_image: The resource name of the SandboxEngineImage.
                Format is `workspaces/*/sandboxEngineImages/*`.
            sandbox_engine_template: The resource name of the SandboxEngineTemplate.
                Format is `workspaces/*/sandboxEngineTemplates/*`.
            name: The resource name of the SandboxEngine.
                Format: `workspaces/*/sandboxEngines/*`.
            display_name: Human-readable name.
            uid: Globally unique identifier of the resource.
            state: The current state of the SandboxEngine.
            creator: Name of entity that created the SandboxEngine.
            creator_display_name: Human-readable name of entity that created the SandboxEngine.
            create_time: Time when the SandboxEngine creation was requested.
            sandbox_engine_image_info: SandboxEngineImage data used when the SandboxEngine
                was created from the assigned sandbox_engine_image.
            sandbox_engine_template_info: SandboxEngineTemplate data used when the SandboxEngine
                was created from the assigned sandbox_engine_template.
            current_idle_duration: Current time the SandboxEngine is idle.
            annotations: Additional arbitrary metadata associated with the SandboxEngine.
        """
        if annotations is None:
            annotations = {}

        self.name = name
        self.display_name = display_name
        self.uid = uid
        self.state = state
        self.creator = creator
        self.creator_display_name = creator_display_name
        self.create_time = create_time
        self.sandbox_engine_image = sandbox_engine_image
        self.sandbox_engine_image_info = sandbox_engine_image_info
        self.sandbox_engine_template = sandbox_engine_template
        self.sandbox_engine_template_info = sandbox_engine_template_info
        self.current_idle_duration = current_idle_duration
        self.annotations = annotations

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def sandbox_engine_to_api_object(sandbox_engine: SandboxEngine) -> V1SandboxEngine:
    return V1SandboxEngine(
        display_name=sandbox_engine.display_name,
        sandbox_engine_image=sandbox_engine.sandbox_engine_image,
        sandbox_engine_template=sandbox_engine.sandbox_engine_template,
        annotations=sandbox_engine.annotations,
    )


def sandbox_engine_from_api_object(api_object: V1SandboxEngine) -> SandboxEngine:
    return SandboxEngine(
        name=api_object.name,
        display_name=api_object.display_name,
        uid=api_object.uid,
        state=sandbox_engine_state_from_api_object(api_object=api_object.state),
        creator=api_object.creator,
        creator_display_name=api_object.creator_display_name,
        create_time=api_object.create_time,
        sandbox_engine_image=api_object.sandbox_engine_image,
        sandbox_engine_image_info=sandbox_engine_image_info_from_api_object(
            api_object=api_object.sandbox_engine_image_info
        ),
        sandbox_engine_template=api_object.sandbox_engine_template,
        sandbox_engine_template_info=sandbox_engine_template_info_from_api_object(
            api_object=api_object.sandbox_engine_template_info
        ),
        current_idle_duration=optional_seconds_to_duration(
            seconds=api_object.current_idle_duration
        ),
        annotations=api_object.annotations if api_object.annotations else {},
    )