"""Discovery types and interfaces."""

from __future__ import annotations

from typing import Literal, TypedDict


class DiscoveredCamera(TypedDict, total=False):
    """Discovered camera from network scan (minimal)."""

    # Required fields
    id: str
    """Unique discovery ID (plugin-generated, stable across rescans)."""
    name: str
    """Camera name (from device or auto-generated)."""

    # Optional fields
    address: str
    """IP address or hostname (optional - some cameras may not have IP)."""


ConnectionStatus = Literal["idle", "connecting", "connected", "error"]
"""Connection status for discovered cameras."""


class DiscoveredCameraWithState(TypedDict, total=False):
    """Discovered camera with state (for backend/UI)."""

    # From DiscoveredCamera
    id: str
    """Unique discovery ID."""
    name: str
    """Camera name."""
    address: str
    """IP address or hostname."""

    # State fields
    provider: str
    """Provider identifier (pluginId or 'go2rtc')."""
    connectionStatus: ConnectionStatus
    """Current connection status."""
    errorMessage: str
    """Error message (when connectionStatus is 'error')."""


class ConnectResult(TypedDict):
    """Connect result from provider."""

    cameraId: str
    """Created camera ID."""
    cameraName: str
    """Created camera name."""
