from enum import Enum

from h2o_engine_manager.gen.model.v1_sandbox_engine_state import V1SandboxEngineState


class SandboxEngineState(Enum):
    """SandboxEngine state."""

    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    STATE_STARTING = "STATE_STARTING"
    STATE_RUNNING = "STATE_RUNNING"
    STATE_TERMINATING = "STATE_TERMINATING"
    STATE_TERMINATED = "STATE_TERMINATED"
    STATE_FAILED = "STATE_FAILED"
    STATE_DELETING = "STATE_DELETING"

    def to_api_object(self) -> V1SandboxEngineState:
        return V1SandboxEngineState(self.value)


def sandbox_engine_state_from_api_object(
    api_object: V1SandboxEngineState,
) -> SandboxEngineState:
    return SandboxEngineState(api_object.value)