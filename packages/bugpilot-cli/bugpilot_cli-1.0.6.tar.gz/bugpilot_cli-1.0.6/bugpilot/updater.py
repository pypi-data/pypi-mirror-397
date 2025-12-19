"""
Auto-Update Module - Check and update from PyPI
"""

import subprocess
import sys
import requests
from typing import Tuple, Optional
from packaging import version as pkg_version # Renamed to avoid conflict with local 'version' variable
import importlib.metadata


class AutoUpdater:
    """Handles automatic updates from PyPI"""
    
    PACKAGE_NAME = "bugpilot-cli"
    PYPI_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
    
    def __init__(self):
        self.current_version = self._get_current_version()
        self.latest_version = None
        self.update_available = False
    
    def _get_current_version(self) -> str:
        """Get currently installed version from package metadata"""
        try:
            # Use importlib.metadata to get the actual installed version
            return importlib.metadata.version(self.PACKAGE_NAME)
        except importlib.metadata.PackageNotFoundError:
            # Fallback if package metadata is not found (e.g., running from source without install)
            try:
                # Attempt to get from __version__ if available (common for CLI tools)
                from . import __version__
                return __version__
            except (ImportError, AttributeError):
                return "0.0.0" # Default fallback for development or unknown state
        except Exception:
            # Catch any other unexpected errors
            return "0.0.0" # Default fallback
    
    def check_for_updates(self) -> Tuple[bool, Optional[str]]:
        """Check if updates are available on PyPI"""
        try:
            response = requests.get(self.PYPI_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.latest_version = data['info']['version']
                
                # Compare versions
                if pkg_version.parse(self.latest_version) > pkg_version.parse(self.current_version):
                    self.update_available = True
                    return True, self.latest_version
                else:
                    return False, self.latest_version
            else:
                return False, None
        except Exception as e:
            # Silently fail if PyPI is unreachable
            return False, None
    
    def get_update_info(self) -> str:
        """Get formatted update information"""
        if self.update_available and self.latest_version:
            return f"""
╔════════════════════════════════════════════════════╗
║          UPDATE AVAILABLE!                         ║
╠════════════════════════════════════════════════════╣
║ Current Version: {self.current_version:<31}   ║
║ Latest Version:  {self.latest_version:<31}   ║
╠════════════════════════════════════════════════════╣
║ Run /update to install the latest version          ║
╚════════════════════════════════════════════════════╝
"""
        else:
            return f"""
╔════════════════════════════════════════════════════╗
║ You're running the latest version: {self.current_version:<16} ║
╚════════════════════════════════════════════════════╝
"""
    
    def perform_update(self) -> Tuple[bool, str]:
        """Perform the actual update via pip"""
        try:
            # Upgrade pip first
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Try normal upgrade first
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", self.PACKAGE_NAME],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # If failed with externally-managed environment error, try with --break-system-packages
            if result.returncode != 0 and "externally-managed-environment" in result.stderr.lower():
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "--break-system-packages", self.PACKAGE_NAME],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            
            if result.returncode == 0:
                return True, f"Successfully updated to version {self.latest_version}"
            else:
                return False, f"Update failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Update timed out. Please try again."
        except Exception as e:
            return False, f"Update error: {str(e)}"
    
    def auto_check_and_notify(self) -> Optional[str]:
        """
        Check for updates and return notification message if available.
        This is called on startup if auto_update_check is enabled.
        """
        has_update, latest = self.check_for_updates()
        if has_update:
            return f"""
[!] Update available: v{self.current_version} → v{latest}
[*] Run /update to install or enable auto-update in /configure
"""
        return None
    
    def get_changelog(self) -> str:
        """Fetch changelog from PyPI (if available)"""
        try:
            response = requests.get(self.PYPI_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                description = data['info'].get('description', 'No changelog available')
                # Truncate if too long
                if len(description) > 500:
                    description = description[:500] + "..."
                return description
            return "Changelog unavailable"
        except:
            return "Could not fetch changelog"


def check_update_on_startup(current_version: str = None, auto_check: bool = True) -> Optional[str]:
    """
    Convenience function to check for updates on startup.
    Returns notification message if update is available.
    Note: current_version parameter is deprecated but kept for compatibility.
    """
    if not auto_check:
        return None
    
    updater = AutoUpdater()  # AutoUpdater now gets version automatically
    return updater.auto_check_and_notify()
