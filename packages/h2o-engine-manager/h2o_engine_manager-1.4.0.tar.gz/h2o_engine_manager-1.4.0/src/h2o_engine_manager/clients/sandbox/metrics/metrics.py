import pprint
from datetime import datetime
from typing import Optional

from h2o_engine_manager.gen.model.v1_metrics import V1Metrics


class MemoryMetrics:
    """Memory usage statistics for the sandbox environment."""

    def __init__(
        self,
        current_bytes: int = 0,
        limit_bytes: Optional[int] = None,
    ):
        """
        Args:
            current_bytes: Current memory usage in bytes.
            limit_bytes: Maximum allowed memory in bytes. None if unlimited.
        """
        self.current_bytes = current_bytes
        self.limit_bytes = limit_bytes

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class DiskMetrics:
    """Disk usage statistics for the sandbox filesystem."""

    def __init__(
        self,
        total_bytes: int = 0,
        available_bytes: int = 0,
    ):
        """
        Args:
            total_bytes: Total disk space in bytes.
            available_bytes: Available disk space in bytes.
        """
        self.total_bytes = total_bytes
        self.available_bytes = available_bytes

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def used_bytes(self) -> int:
        """Used disk space in bytes."""
        return self.total_bytes - self.available_bytes

    @property
    def usage_ratio(self) -> float:
        """Disk usage as a ratio (0.0-1.0)."""
        if self.total_bytes == 0:
            return 0.0
        return self.used_bytes / self.total_bytes


class CpuMetrics:
    """CPU usage statistics for the sandbox environment."""

    def __init__(
        self,
        usage_ratio: float = 0.0,
    ):
        """
        Args:
            usage_ratio: CPU usage as a ratio (0.0-1.0) of available CPU resources.
        """
        self.usage_ratio = usage_ratio

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Metrics:
    """Resource usage metrics snapshot for the sandbox environment."""

    def __init__(
        self,
        memory: Optional[MemoryMetrics] = None,
        disk: Optional[DiskMetrics] = None,
        cpu: Optional[CpuMetrics] = None,
        collect_time: Optional[datetime] = None,
    ):
        """
        Args:
            memory: Memory usage statistics.
            disk: Disk usage statistics.
            cpu: CPU usage statistics.
            collect_time: Time when these metrics were collected.
        """
        self.memory = memory
        self.disk = disk
        self.cpu = cpu
        self.collect_time = collect_time

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def _parse_int64(value: Optional[str]) -> int:
    """Parse an int64 string value to int, returning 0 if None or empty."""
    if value is None or value == "":
        return 0
    return int(value)


def _parse_optional_int64(value) -> Optional[int]:
    """Parse an optional int64 string value to Optional[int]."""
    if value is None or value == "":
        return None
    return int(value)


def metrics_from_api_object(api_object: V1Metrics) -> Metrics:
    """Convert a V1Metrics API object to a Metrics instance."""
    memory = None
    if api_object.memory:
        memory = MemoryMetrics(
            current_bytes=_parse_int64(api_object.memory.current_bytes),
            limit_bytes=_parse_optional_int64(api_object.memory.limit_bytes),
        )

    disk = None
    if api_object.disk:
        disk = DiskMetrics(
            total_bytes=_parse_int64(api_object.disk.total_bytes),
            available_bytes=_parse_int64(api_object.disk.available_bytes),
        )

    cpu = None
    if api_object.cpu:
        cpu = CpuMetrics(
            usage_ratio=api_object.cpu.usage_ratio or 0.0,
        )

    return Metrics(
        memory=memory,
        disk=disk,
        cpu=cpu,
        collect_time=api_object.collect_time,
    )