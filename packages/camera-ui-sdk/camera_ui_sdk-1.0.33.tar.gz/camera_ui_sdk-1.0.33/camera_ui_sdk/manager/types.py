"""Manager types and interfaces."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, Protocol, overload, runtime_checkable

if TYPE_CHECKING:
    from ..camera.config import CameraConfig
    from ..camera.device import Camera, CameraDevice
    from ..discovery.provider import DiscoveryProvider
    from ..discovery.types import DiscoveredCamera
    from ..plugin.types import CuiPlugin, PluginInfo


class DEVICE_MANAGER_EVENT(Enum):
    CAMERA_SELECTED = "cameraSelected"
    CAMERA_DESELECTED = "cameraDeselected"


# Listener types for DeviceManager events
DeviceManagerSelectedListener = Callable[["CameraDevice"], None] | Callable[["CameraDevice"], Awaitable[None]]
DeviceManagerDeselectedListener = Callable[[str], None] | Callable[[str], Awaitable[None]]
DeviceManagerListener = DeviceManagerSelectedListener | DeviceManagerDeselectedListener


# RPC interface for DeviceManager
class DeviceManagerRPC(Protocol):
    """RPC interface for DeviceManager calls from plugins."""

    async def createCamera(self, cameraConfig: CameraConfig, pluginId: str) -> Camera:
        """Create a new camera."""
        ...

    async def updateCamera(self, cameraIdOrName: str, cameraConfig: dict[str, Any], pluginId: str) -> Camera:
        """Update a camera configuration."""
        ...

    async def getCamera(self, cameraIdOrName: str, pluginId: str) -> Camera | None:
        """Get a camera by ID or name."""
        ...

    async def removeCamera(self, cameraIdOrName: str, pluginId: str) -> None:
        """Remove a camera."""
        ...


# RPC interface for CoreManager
class CoreManagerRPC(Protocol):
    """RPC interface for CoreManager calls from plugins."""

    async def getPlugin(self, pluginName: str) -> PluginInfo | None:
        """Get plugin info by name."""
        ...

    async def getFFmpegPath(self) -> str:
        """Get FFmpeg executable path."""
        ...

    async def getServerAddresses(self) -> list[str]:
        """Get server addresses."""
        ...


class LoggerService(Protocol):
    """Logger service interface."""

    def log(self, *args: Any) -> None:
        """Log a message."""
        ...

    def error(self, *args: Any) -> None:
        """Log an error."""
        ...

    def warn(self, *args: Any) -> None:
        """Log a warning."""
        ...

    def success(self, *args: Any) -> None:
        """Log a success message."""
        ...

    def debug(self, *args: Any) -> None:
        """Log a debug message."""
        ...

    def trace(self, *args: Any) -> None:
        """Log a trace message."""
        ...

    def attention(self, *args: Any) -> None:
        """Log an attention message."""
        ...


@runtime_checkable
class DeviceManager(Protocol):
    """Device manager for camera operations."""

    async def createCamera(self, cameraConfig: CameraConfig) -> CameraDevice:
        """
        Create a new camera.

        Args:
            cameraConfig: Camera configuration

        Returns:
            The created camera device
        """
        ...

    async def updateCamera(self, cameraIdOrName: str, cameraConfig: dict[str, Any]) -> CameraDevice:
        """
        Update a camera configuration.

        Args:
            cameraIdOrName: Camera ID or name
            cameraConfig: Partial camera configuration to update

        Returns:
            The updated camera device
        """
        ...

    async def getCamera(self, cameraIdOrName: str) -> CameraDevice | None:
        """
        Get a camera by ID or name.

        Args:
            cameraIdOrName: Camera ID or name

        Returns:
            The camera device or None if not found
        """
        ...

    async def removeCamera(self, cameraIdOrName: str) -> None:
        """
        Remove a camera.

        Args:
            cameraIdOrName: Camera ID or name
        """
        ...

    @overload
    def on(
        self,
        event: Literal[DEVICE_MANAGER_EVENT.CAMERA_DESELECTED],
        listener: DeviceManagerDeselectedListener,
    ) -> Any: ...
    @overload
    def on(
        self, event: Literal[DEVICE_MANAGER_EVENT.CAMERA_SELECTED], listener: DeviceManagerSelectedListener
    ) -> Any: ...
    def on(self, event: DEVICE_MANAGER_EVENT, listener: DeviceManagerListener) -> Any: ...

    @overload
    def once(
        self,
        event: Literal[DEVICE_MANAGER_EVENT.CAMERA_DESELECTED],
        listener: DeviceManagerDeselectedListener,
    ) -> Any: ...
    @overload
    def once(
        self, event: Literal[DEVICE_MANAGER_EVENT.CAMERA_SELECTED], listener: DeviceManagerSelectedListener
    ) -> Any: ...
    def once(self, event: DEVICE_MANAGER_EVENT, listener: DeviceManagerListener) -> Any: ...

    @overload
    def off(
        self,
        event: Literal[DEVICE_MANAGER_EVENT.CAMERA_DESELECTED],
        listener: DeviceManagerDeselectedListener,
    ) -> Any: ...
    @overload
    def off(
        self, event: Literal[DEVICE_MANAGER_EVENT.CAMERA_SELECTED], listener: DeviceManagerSelectedListener
    ) -> Any: ...
    def off(self, event: DEVICE_MANAGER_EVENT, listener: DeviceManagerListener) -> None: ...

    @overload
    def removeListener(
        self,
        event: Literal[DEVICE_MANAGER_EVENT.CAMERA_DESELECTED],
        listener: DeviceManagerDeselectedListener,
    ) -> Any: ...
    @overload
    def removeListener(
        self, event: Literal[DEVICE_MANAGER_EVENT.CAMERA_SELECTED], listener: DeviceManagerSelectedListener
    ) -> Any: ...
    def removeListener(self, event: DEVICE_MANAGER_EVENT, listener: DeviceManagerListener) -> None: ...

    def removeAllListeners(self, event: DEVICE_MANAGER_EVENT | None = None) -> None: ...


@runtime_checkable
class CoreManager(Protocol):
    """Core manager for system operations."""

    async def connectToPlugin(self, pluginName: str) -> CuiPlugin | None:
        """
        Connect to another plugin.

        Args:
            pluginName: Name of the plugin to connect to

        Returns:
            The plugin instance or None if not found
        """
        ...

    async def getFFmpegPath(self) -> str:
        """
        Get the FFmpeg executable path.

        Returns:
            Path to FFmpeg
        """
        ...

    async def getServerAddresses(self) -> list[str]:
        """
        Get server addresses.

        Returns:
            List of server addresses
        """
        ...


# RPC interface for DiscoveryManager
class DiscoveryManagerRPC(Protocol):
    """RPC interface for DiscoveryManager calls from plugins."""

    async def registerProvider(self, pluginId: str) -> None:
        """Register a discovery provider."""
        ...

    async def unregisterProvider(self, pluginId: str) -> None:
        """Unregister the discovery provider."""
        ...


@runtime_checkable
class DiscoveryManager(Protocol):
    """Discovery manager for camera discovery operations.

    Manages camera discovery providers from cameraController plugins.
    Accessed via `api.discoveryManager` in plugins.

    The backend controls polling - plugins just need to register their provider
    and implement the DiscoveryProvider interface.

    Example:
        ```python
        # Register a discovery provider (cameraController plugins only)
        provider = MyDiscoveryProvider()
        await api.discoveryManager.registerProvider(provider)
        ```
    """

    async def registerProvider(self, provider: DiscoveryProvider) -> None:
        """
        Register a discovery provider (cameraController plugins only).
        The backend will poll getDiscoveredCameras() and call connect()
        when users want to add a camera.

        Args:
            provider: The discovery provider implementation
        """
        ...

    async def unregisterProvider(self) -> None:
        """Unregister the discovery provider."""
        ...
