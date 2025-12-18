from enum import Enum

from h2o_engine_manager.gen.model.v1_port_state import V1PortState


class PortState(Enum):
    """Port state."""

    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    STATE_PENDING = "STATE_PENDING"
    STATE_READY = "STATE_READY"
    STATE_FAILED = "STATE_FAILED"
    STATE_DELETING = "STATE_DELETING"

    def to_api_object(self) -> V1PortState:
        return V1PortState(self.value)


def port_state_from_api_object(api_object: V1PortState) -> PortState:
    return PortState(api_object.value)
