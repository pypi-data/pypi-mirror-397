import pprint
from datetime import datetime
from typing import Optional

from h2o_engine_manager.clients.sandbox.port.state import PortState
from h2o_engine_manager.clients.sandbox.port.state import port_state_from_api_object
from h2o_engine_manager.gen.model.v1_port import V1Port


class Port:
    """
    Port represents a network port exposed from a SandboxEngine.
    """

    def __init__(
        self,
        name: str = "",
        display_name: str = "",
        public: bool = False,
        internal_url: str = "",
        public_url: str = "",
        create_time: Optional[datetime] = None,
        creator: str = "",
        creator_display_name: str = "",
        update_time: Optional[datetime] = None,
        updater: str = "",
        updater_display_name: str = "",
        state: PortState = PortState.STATE_UNSPECIFIED,
        failure_reason: str = "",
    ):
        """
        Port represents a network port exposed from a SandboxEngine.

        Args:
            name: The resource name of the port.
                Format: "workspaces/*/sandboxEngines/*/ports/*"
            display_name: Optional human-readable display name for this port.
            public: Whether this port should be publicly accessible.
                If False, the port is only accessible within the cluster.
            internal_url: Output only. URL for accessing this port from within the Kubernetes cluster.
            public_url: Output only. URL for accessing this port from outside the cluster.
                Only set when public is True.
            create_time: Output only. Time when this port was created.
            creator: Output only. Name of an entity that created this port.
            creator_display_name: Output only. Display name of the entity that created this port.
            update_time: Output only. Time when this port was last updated.
            updater: Output only. Name of an entity that last updated this port.
            updater_display_name: Output only. Display name of the entity that last updated this port.
            state: Output only. The current state of the port.
            failure_reason: Output only. Failure reason during port creation.
                Only set when state is STATE_FAILED.
        """
        self.name = name
        self.display_name = display_name
        self.public = public
        self.internal_url = internal_url
        self.public_url = public_url
        self.create_time = create_time
        self.creator = creator
        self.creator_display_name = creator_display_name
        self.update_time = update_time
        self.updater = updater
        self.updater_display_name = updater_display_name
        self.state = state
        self.failure_reason = failure_reason

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def port_from_api_object(api_object: V1Port) -> Port:
    """
    Convert V1Port API object to Port.

    Args:
        api_object: The V1Port API object to convert.

    Returns:
        Port: The Port object.
    """
    state = PortState.STATE_UNSPECIFIED
    if api_object.state:
        state = port_state_from_api_object(api_object.state)

    return Port(
        name=api_object.name if api_object.name else "",
        display_name=api_object.display_name if api_object.display_name else "",
        public=api_object.public if api_object.public is not None else False,
        internal_url=api_object.internal_url if api_object.internal_url else "",
        public_url=api_object.public_url if api_object.public_url else "",
        create_time=api_object.create_time,
        creator=api_object.creator if api_object.creator else "",
        creator_display_name=(
            api_object.creator_display_name if api_object.creator_display_name else ""
        ),
        update_time=api_object.update_time,
        updater=api_object.updater if api_object.updater else "",
        updater_display_name=(
            api_object.updater_display_name if api_object.updater_display_name else ""
        ),
        state=state,
        failure_reason=(
            api_object.failure_reason if api_object.failure_reason else ""
        ),
    )


def port_to_api_object(port: Port) -> V1Port:
    """
    Convert Port to V1Port API object.

    Args:
        port: The Port object to convert.

    Returns:
        V1Port: The API object ready to be sent to the server.
    """
    return V1Port(
        display_name=port.display_name,
        public=port.public,
    )
