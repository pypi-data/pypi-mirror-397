from enum import Enum

from h2o_engine_manager.gen.model.v1_process_state import V1ProcessState


class ProcessState(Enum):
    """ProcessState indicates the state of a process."""

    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    STATE_PENDING = "STATE_PENDING"
    STATE_RUNNING = "STATE_RUNNING"
    STATE_SUCCEEDED = "STATE_SUCCEEDED"
    STATE_FAILED = "STATE_FAILED"

    def to_api_object(self) -> V1ProcessState:
        return V1ProcessState(self.value)


def process_state_from_api_object(api_object: V1ProcessState) -> ProcessState:
    return ProcessState(api_object.value)