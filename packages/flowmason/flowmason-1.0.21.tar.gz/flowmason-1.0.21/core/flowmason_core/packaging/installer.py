"""
FlowMason Package Installer.

Installs .fmpkg packages locally or deploys to orgs.
"""

import shutil
import zipfile
from pathlib import Path
from typing import List, Optional, Union

from flowmason_core.packaging.manifest import PackageManifest

# Default installation directory
PACKAGES_DIR = Path.home() / ".flowmason" / "packages"


class PackageInstaller:
    """
    Installs .fmpkg packages locally.

    Usage:
        installer = PackageInstaller()
        installer.install("my-package-1.0.0.fmpkg")
    """

    def __init__(self, packages_dir: Optional[Union[str, Path]] = None):
        """
        Initialize package installer.

        Args:
            packages_dir: Directory to install packages to (default: ~/.flowmason/packages)
        """
        self.packages_dir = Path(packages_dir) if packages_dir else PACKAGES_DIR
        self.packages_dir.mkdir(parents=True, exist_ok=True)

    def install(
        self,
        package_path: Union[str, Path],
        force: bool = False,
    ) -> PackageManifest:
        """
        Install a .fmpkg package.

        Args:
            package_path: Path to .fmpkg file
            force: Overwrite existing installation

        Returns:
            Package manifest
        """
        package_path = Path(package_path)
        if not package_path.exists():
            raise FileNotFoundError(f"Package not found: {package_path}")

        # Read manifest from package
        with zipfile.ZipFile(package_path, "r") as zf:
            manifest_content = zf.read("manifest.json").decode("utf-8")
            manifest = PackageManifest.from_json(manifest_content)

        # Determine installation directory
        install_dir = self.packages_dir / manifest.name / manifest.version

        # Check if already installed
        if install_dir.exists():
            if not force:
                raise ValueError(
                    f"Package {manifest.name}@{manifest.version} already installed. "
                    "Use force=True to overwrite."
                )
            shutil.rmtree(install_dir)

        # Extract package
        install_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(package_path, "r") as zf:
            zf.extractall(install_dir)

        # Create symlink for latest version
        latest_link = self.packages_dir / manifest.name / "latest"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(manifest.version)

        return manifest

    def uninstall(
        self,
        name: str,
        version: Optional[str] = None,
    ) -> bool:
        """
        Uninstall a package.

        Args:
            name: Package name
            version: Specific version to uninstall (default: all versions)

        Returns:
            True if package was uninstalled
        """
        package_dir = self.packages_dir / name

        if not package_dir.exists():
            return False

        if version:
            version_dir = package_dir / version
            if version_dir.exists():
                shutil.rmtree(version_dir)
                # Update latest symlink if needed
                latest_link = package_dir / "latest"
                if latest_link.is_symlink() and latest_link.resolve() == version_dir:
                    latest_link.unlink()
                    # Point to another version if available
                    versions = [d for d in package_dir.iterdir() if d.is_dir() and d.name != "latest"]
                    if versions:
                        latest_link.symlink_to(versions[0].name)
                return True
            return False
        else:
            shutil.rmtree(package_dir)
            return True

    def list_installed(self) -> List[dict]:
        """
        List all installed packages.

        Returns:
            List of package info dicts
        """
        packages: List[dict] = []

        if not self.packages_dir.exists():
            return packages

        for pkg_dir in self.packages_dir.iterdir():
            if not pkg_dir.is_dir():
                continue

            for version_dir in pkg_dir.iterdir():
                if version_dir.name == "latest" or version_dir.is_symlink():
                    continue

                manifest_path = version_dir / "manifest.json"
                if manifest_path.exists():
                    manifest = PackageManifest.from_file(manifest_path)
                    packages.append({
                        "name": manifest.name,
                        "version": manifest.version,
                        "description": manifest.description,
                        "path": str(version_dir),
                    })

        return packages

    def get_package(
        self,
        name: str,
        version: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Get path to an installed package.

        Args:
            name: Package name
            version: Specific version (default: latest)

        Returns:
            Path to package directory, or None if not found
        """
        package_dir = self.packages_dir / name

        if not package_dir.exists():
            return None

        if version:
            version_dir = package_dir / version
            return version_dir if version_dir.exists() else None
        else:
            latest_link = package_dir / "latest"
            if latest_link.exists():
                return latest_link.resolve()
            return None


def install_package(
    package_path: Union[str, Path],
    packages_dir: Optional[Union[str, Path]] = None,
    force: bool = False,
) -> PackageManifest:
    """
    Install a .fmpkg package.

    Args:
        package_path: Path to .fmpkg file
        packages_dir: Installation directory (optional)
        force: Overwrite existing installation

    Returns:
        Package manifest
    """
    installer = PackageInstaller(packages_dir)
    return installer.install(package_path, force=force)
