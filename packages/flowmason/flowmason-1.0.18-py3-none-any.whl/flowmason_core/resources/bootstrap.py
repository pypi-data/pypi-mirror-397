"""
FlowMason extra assets bootstrap.

This module is responsible for downloading and unpacking larger, non-Python
assets (frontend bundles, demos, examples, etc.) from the FlowMason website
after the core package is installed.

We intentionally keep the PyPI package small and fetch these extras on demand.
"""

from __future__ import annotations

import os
import tarfile
import tempfile
from pathlib import Path
from typing import Optional

import httpx
from rich.console import Console

from flowmason_core import __version__ as CORE_VERSION

# Environment variable overrides
ASSETS_URL_ENV = "FLOWMASON_ASSETS_URL"
ASSETS_DIR_ENV = "FLOWMASON_ASSETS_DIR"
FLOWMASON_HOME_ENV = "FLOWMASON_HOME"

# Default location under user home: ~/.flowmason/assets/<version>
DEFAULT_HOME = Path(os.getenv(FLOWMASON_HOME_ENV, Path.home() / ".flowmason"))
DEFAULT_ASSETS_ROOT = DEFAULT_HOME / "assets"

# Default URL template on the website.
# The website should host a tarball at, for example:
#   https://flowmason.com/downloads/flowmason-extra-assets-<version>.tar.gz
DEFAULT_ASSETS_URL_TEMPLATE = (
    "https://flowmason.com/downloads/flowmason-extra-assets-{version}.tar.gz"
)


def _get_assets_root() -> Path:
    """Return the root directory where assets will be installed."""
    custom = os.getenv(ASSETS_DIR_ENV)
    if custom:
        return Path(custom).expanduser()
    return DEFAULT_ASSETS_ROOT


def _get_assets_url() -> str:
    """Return the URL to download the assets tarball from."""
    env_url = os.getenv(ASSETS_URL_ENV)
    if env_url:
        return env_url
    return DEFAULT_ASSETS_URL_TEMPLATE.format(version=CORE_VERSION)


def ensure_extra_assets(console: Optional[Console] = None) -> Path:
    """
    Ensure that extra FlowMason assets are downloaded and unpacked locally.

    This function is safe to call multiple times; it uses a marker file
    to avoid re-downloading if the current version is already installed.

    Returns:
        Path to the version-specific assets directory.
    """
    assets_root = _get_assets_root()
    version_dir = assets_root / CORE_VERSION
    marker = version_dir / ".installed"

    # Fast path: already installed
    if marker.exists():
        return version_dir

    assets_url = _get_assets_url()

    # Ensure directories exist
    assets_root.mkdir(parents=True, exist_ok=True)
    version_dir.mkdir(parents=True, exist_ok=True)

    if console is not None:
        console.print(
            f"[cyan]FlowMason[/cyan] downloading extra assets "
            f"for v{CORE_VERSION} from:\n  [blue]{assets_url}[/blue]"
        )

    # Download tarball to a temporary file
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)

        with httpx.stream("GET", assets_url, follow_redirects=True, timeout=None) as resp:
            resp.raise_for_status()
            with tmp_path.open("wb") as f:
                for chunk in resp.iter_bytes():
                    if chunk:
                        f.write(chunk)

        # Extract into version directory
        with tarfile.open(tmp_path, "r:gz") as tf:
            tf.extractall(path=version_dir)

        marker.write_text("ok\n", encoding="utf-8")

        if console is not None:
            console.print(
                f"[green]FlowMason[/green] extra assets installed at: "
                f"{str(version_dir)}"
            )

    except Exception as exc:  # pragma: no cover - defensive
        # On failure, we log a warning but do not prevent the backend from running.
        if console is not None:
            console.print(
                "[yellow]Warning:[/yellow] Failed to download extra assets.\n"
                f"  URL: {assets_url}\n"
                f"  Error: {exc}"
            )
        # Leave directory as-is; caller may choose to continue without extras.
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass

    return version_dir

