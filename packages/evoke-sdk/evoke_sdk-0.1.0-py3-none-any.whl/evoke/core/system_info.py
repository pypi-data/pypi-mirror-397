"""
Evoke Core - System information collection with caching

Collects comprehensive endpoint data once at SDK init and caches it
for attachment to all events.
"""
from typing import Optional
from datetime import datetime
import socket
import platform
import os
import logging
import re
from threading import Thread, Lock

from evoke._version import SDK_VERSION
from evoke.schema.system_info import SystemInfo, ContainerInfo

logger = logging.getLogger(__name__)

# Cached system info (collected once at init)
_cached_system_info: Optional[SystemInfo] = None
_cache_lock = Lock()


def _get_public_ip() -> Optional[str]:
    """
    Fetch public IP address from an external service.
    Uses multiple fallback services.
    """
    services = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
        "https://checkip.amazonaws.com",
    ]

    try:
        import requests
        for service in services:
            try:
                response = requests.get(service, timeout=2)
                if response.status_code == 200:
                    ip = response.text.strip()
                    # Validate it looks like an IP
                    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                        return ip
            except Exception:
                continue
    except ImportError:
        logger.debug("requests not installed, cannot fetch public IP")

    return None


def _detect_container() -> ContainerInfo:
    """Detect if running in a container environment."""
    info = ContainerInfo()

    # Check for Docker
    if os.path.exists('/.dockerenv'):
        info.is_container = True
        info.runtime = "docker"

        # Try to get container ID from cgroup
        try:
            with open('/proc/self/cgroup', 'r') as f:
                for line in f:
                    if 'docker' in line:
                        parts = line.strip().split('/')
                        if parts:
                            info.container_id = parts[-1][:12]
                        break
        except Exception:
            pass

    # Check for Kubernetes
    if os.environ.get('KUBERNETES_SERVICE_HOST'):
        info.is_container = True
        info.runtime = "kubernetes"
        info.pod_name = os.environ.get('HOSTNAME') or os.environ.get('POD_NAME')
        info.namespace = os.environ.get('POD_NAMESPACE')

    # Check for containerd/cri-o via cgroup
    if not info.is_container:
        try:
            with open('/proc/1/cgroup', 'r') as f:
                content = f.read()
                if 'containerd' in content:
                    info.is_container = True
                    info.runtime = "containerd"
                elif 'cri-o' in content:
                    info.is_container = True
                    info.runtime = "cri-o"
        except Exception:
            pass

    return info


def _get_memory_info() -> Optional[int]:
    """Get total system memory in MB."""
    try:
        import psutil
        return psutil.virtual_memory().total // (1024 * 1024)
    except ImportError:
        pass

    # Fallback for Linux
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    kb = int(line.split()[1])
                    return kb // 1024
    except Exception:
        pass

    return None


def collect_system_info(fetch_public_ip: bool = True) -> SystemInfo:
    """
    Collect comprehensive system information.

    Args:
        fetch_public_ip: Whether to fetch public IP (may add latency)

    Returns:
        SystemInfo dataclass with all collected information
    """
    # Basic info
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "unknown"

    try:
        primary_ip = socket.gethostbyname(hostname)
    except Exception:
        primary_ip = None

    # Collect all components
    container_info = _detect_container()

    info = SystemInfo(
        hostname=hostname,
        platform=platform.system(),
        sdk_name="evoke",
        sdk_version=SDK_VERSION,
        os_version=platform.version(),
        architecture=platform.machine(),
        python_version=platform.python_version(),
        ip_address=primary_ip,
        cpu_count=os.cpu_count(),
        memory_total_mb=_get_memory_info(),
        container=container_info,
        collected_at=datetime.utcnow().isoformat(),
    )

    # Fetch public IP asynchronously to avoid blocking
    if fetch_public_ip:
        def fetch_and_update():
            try:
                public_ip = _get_public_ip()
                if public_ip:
                    info.public_ip = public_ip
                    logger.debug(f"Public IP fetched: {public_ip}")
            except Exception as e:
                logger.debug(f"Failed to fetch public IP: {e}")

        thread = Thread(target=fetch_and_update, daemon=True)
        thread.start()
        # Give it a short time to complete (non-blocking for init)
        thread.join(timeout=0.5)

    return info


def get_cached_system_info() -> Optional[SystemInfo]:
    """Get the cached system info (None if not yet collected)."""
    return _cached_system_info


def init_system_info(fetch_public_ip: bool = True) -> SystemInfo:
    """
    Initialize and cache system info. Called once during SDK init.

    Args:
        fetch_public_ip: Whether to fetch public IP

    Returns:
        The collected SystemInfo
    """
    global _cached_system_info

    with _cache_lock:
        if _cached_system_info is None:
            _cached_system_info = collect_system_info(fetch_public_ip)
            logger.debug(f"System info collected: hostname={_cached_system_info.hostname}")
        return _cached_system_info


def reset_system_info() -> None:
    """Reset cached system info (for testing)."""
    global _cached_system_info
    with _cache_lock:
        _cached_system_info = None
