"""
Evoke Schema - System information for endpoint identification
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


@dataclass
class ContainerInfo:
    """Container environment detection"""
    is_container: bool = False
    runtime: Optional[str] = None  # "docker", "kubernetes", "containerd", etc.
    container_id: Optional[str] = None
    pod_name: Optional[str] = None
    namespace: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"is_container": self.is_container}
        if self.runtime:
            result["runtime"] = self.runtime
        if self.container_id:
            result["container_id"] = self.container_id
        if self.pod_name:
            result["pod_name"] = self.pod_name
        if self.namespace:
            result["namespace"] = self.namespace
        return result


@dataclass
class SystemInfo:
    """
    Comprehensive system information for endpoint identification.
    Collected once at SDK init and cached for all events.
    """
    # Basic identification
    hostname: str
    platform: str
    sdk_name: str = "evoke"
    sdk_version: str = ""

    # OS details
    os_version: Optional[str] = None
    architecture: Optional[str] = None
    python_version: Optional[str] = None

    # Network
    ip_address: Optional[str] = None  # Primary private IP
    public_ip: Optional[str] = None

    # Hardware
    cpu_count: Optional[int] = None
    memory_total_mb: Optional[int] = None

    # Container
    container: Optional[ContainerInfo] = None

    # Timestamp when info was collected
    collected_at: Optional[str] = None  # ISO format

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "hostname": self.hostname,
            "platform": self.platform,
            "sdk_name": self.sdk_name,
            "sdk_version": self.sdk_version,
        }

        if self.os_version:
            result["os_version"] = self.os_version
        if self.architecture:
            result["architecture"] = self.architecture
        if self.python_version:
            result["python_version"] = self.python_version
        if self.ip_address:
            result["ip_address"] = self.ip_address
        if self.public_ip:
            result["public_ip"] = self.public_ip
        if self.cpu_count is not None:
            result["cpu_count"] = self.cpu_count
        if self.memory_total_mb is not None:
            result["memory_total_mb"] = self.memory_total_mb
        if self.container:
            result["container"] = self.container.to_dict()
        if self.collected_at:
            result["collected_at"] = self.collected_at

        return result
