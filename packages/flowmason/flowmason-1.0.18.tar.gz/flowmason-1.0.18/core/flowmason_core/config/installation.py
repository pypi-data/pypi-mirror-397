"""
Installation Configuration for FlowMason.

Manages installation paths and server state for the VSCode extension
and other tools to discover and manage FlowMason instances.

Config is stored in ~/.flowmason/installation.json
"""

import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Optional

# Default config directory
DEFAULT_CONFIG_DIR = Path.home() / ".flowmason"
INSTALLATION_FILE_NAME = "installation.json"


@dataclass
class InstallationInfo:
    """Information about the FlowMason installation."""

    # Installation paths
    install_path: str  # Path to flowmason installation
    python_path: str  # Path to Python executable used
    version: str  # FlowMason version

    # Server state
    studio_pid: Optional[int] = None  # PID of running studio server
    studio_port: int = 8999  # Port studio is running on
    studio_host: str = "127.0.0.1"  # Host studio is bound to
    studio_started_at: Optional[str] = None  # ISO timestamp

    # Frontend state (for development)
    frontend_pid: Optional[int] = None
    frontend_port: int = 5173
    frontend_started_at: Optional[str] = None

    # Additional metadata
    last_updated: Optional[str] = None


class InstallationConfig:
    """
    Manages FlowMason installation configuration.

    Stores installation paths and running server state in ~/.flowmason/installation.json
    so external tools (like VSCode extension) can discover and manage FlowMason.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self._config_dir = config_dir or DEFAULT_CONFIG_DIR
        self._config_file = self._config_dir / INSTALLATION_FILE_NAME
        self._lock = RLock()

        # Ensure config directory exists
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def _load(self) -> Optional[InstallationInfo]:
        """Load installation info from file."""
        if self._config_file.exists():
            try:
                with open(self._config_file, "r") as f:
                    data = json.load(f)
                return InstallationInfo(
                    install_path=data.get("install_path", ""),
                    python_path=data.get("python_path", ""),
                    version=data.get("version", "0.0.0"),
                    studio_pid=data.get("studio_pid"),
                    studio_port=data.get("studio_port", 8999),
                    studio_host=data.get("studio_host", "127.0.0.1"),
                    studio_started_at=data.get("studio_started_at"),
                    frontend_pid=data.get("frontend_pid"),
                    frontend_port=data.get("frontend_port", 5173),
                    frontend_started_at=data.get("frontend_started_at"),
                    last_updated=data.get("last_updated"),
                )
            except Exception:
                return None
        return None

    def _save(self, info: InstallationInfo) -> None:
        """Save installation info to file."""
        info.last_updated = datetime.now().isoformat()
        with open(self._config_file, "w") as f:
            json.dump(asdict(info), f, indent=2)

    def get_info(self) -> Optional[InstallationInfo]:
        """Get current installation info."""
        with self._lock:
            return self._load()

    def register_installation(
        self,
        install_path: Optional[str] = None,
        version: Optional[str] = None,
    ) -> InstallationInfo:
        """
        Register this FlowMason installation.

        Called during pip install or first run to record installation paths.
        """
        with self._lock:
            existing = self._load()

            # Detect installation path if not provided
            if install_path is None:
                # Try to find the flowmason package location
                try:
                    import flowmason_core

                    install_path = str(Path(flowmason_core.__file__).parent.parent.parent)
                except ImportError:
                    install_path = str(Path(__file__).parent.parent.parent.parent)

            # Detect version if not provided
            if version is None:
                try:
                    from flowmason_core import __version__

                    version = __version__
                except (ImportError, AttributeError):
                    version = "0.1.0"

            info = InstallationInfo(
                install_path=install_path,
                python_path=sys.executable,
                version=version,
                # Preserve server state if exists
                studio_pid=existing.studio_pid if existing else None,
                studio_port=existing.studio_port if existing else 8999,
                studio_host=existing.studio_host if existing else "127.0.0.1",
                studio_started_at=existing.studio_started_at if existing else None,
                frontend_pid=existing.frontend_pid if existing else None,
                frontend_port=existing.frontend_port if existing else 5173,
                frontend_started_at=existing.frontend_started_at if existing else None,
            )

            self._save(info)
            return info

    def update_studio_state(
        self,
        pid: Optional[int] = None,
        port: Optional[int] = None,
        host: Optional[str] = None,
        running: bool = True,
    ) -> Optional[InstallationInfo]:
        """
        Update studio server state.

        Called when studio starts/stops to track the running instance.
        """
        with self._lock:
            info = self._load()
            if info is None:
                # Auto-register if not already registered
                info = self.register_installation()

            if running:
                info.studio_pid = pid or os.getpid()
                if port is not None:
                    info.studio_port = port
                if host is not None:
                    info.studio_host = host
                info.studio_started_at = datetime.now().isoformat()
            else:
                info.studio_pid = None
                info.studio_started_at = None

            self._save(info)
            return info

    def update_frontend_state(
        self,
        pid: Optional[int] = None,
        port: Optional[int] = None,
        running: bool = True,
    ) -> Optional[InstallationInfo]:
        """Update frontend dev server state."""
        with self._lock:
            info = self._load()
            if info is None:
                info = self.register_installation()

            if running:
                info.frontend_pid = pid
                if port is not None:
                    info.frontend_port = port
                info.frontend_started_at = datetime.now().isoformat()
            else:
                info.frontend_pid = None
                info.frontend_started_at = None

            self._save(info)
            return info

    def is_studio_running(self) -> bool:
        """Check if studio server is marked as running."""
        info = self.get_info()
        if info is None or info.studio_pid is None:
            return False

        # Verify PID is actually running
        try:
            os.kill(info.studio_pid, 0)
            return True
        except (OSError, ProcessLookupError):
            # Process not running, clear stale state
            self.update_studio_state(running=False)
            return False

    def get_studio_url(self) -> Optional[str]:
        """Get the URL for the running studio server."""
        info = self.get_info()
        if info is None or not self.is_studio_running():
            return None
        return f"http://{info.studio_host}:{info.studio_port}"

    def clear_state(self) -> None:
        """Clear all server state (for shutdown)."""
        with self._lock:
            info = self._load()
            if info:
                info.studio_pid = None
                info.studio_started_at = None
                info.frontend_pid = None
                info.frontend_started_at = None
                self._save(info)


# Global singleton instance
_installation_config: Optional[InstallationConfig] = None
_config_lock = RLock()


def get_installation_config() -> InstallationConfig:
    """Get the global installation config instance."""
    global _installation_config
    with _config_lock:
        if _installation_config is None:
            _installation_config = InstallationConfig()
        return _installation_config
