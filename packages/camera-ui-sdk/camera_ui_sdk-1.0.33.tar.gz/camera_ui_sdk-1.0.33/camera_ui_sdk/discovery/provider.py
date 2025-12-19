"""Discovery provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .types import ConnectResult, DiscoveredCamera

if TYPE_CHECKING:
    from ..storage.schema import JsonSchemaWithoutCallbacks


class DiscoveryProvider(ABC):
    """Discovery provider interface for plugins.

    Implement this class to provide camera discovery functionality.
    The backend calls scan() when users are on the /devices page.

    Example:
        ```python
        class OnvifDiscoveryProvider(DiscoveryProvider):
            async def scan(self) -> list[DiscoveredCamera]:
                # Scan network for cameras
                devices = await self.discover_devices()
                return [{"id": d.id, "name": d.name, "address": d.address} for d in devices]

            async def getConnectionSchema(
                self, camera: DiscoveredCamera
            ) -> list[JsonSchemaWithoutCallbacks]:
                return [
                    {"key": "username", "type": "string", "title": "Username", "required": True},
                    {"key": "password", "type": "string", "title": "Password", "format": "password", "required": True},
                ]

            async def connect(
                self, camera: DiscoveredCamera, credentials: dict
            ) -> ConnectResult:
                # Probe device, build config, create camera via api.deviceManager.createCamera()
                camera_id = await api.deviceManager.createCamera(config)
                return {"cameraId": camera_id, "cameraName": camera["name"]}
        ```
    """

    @abstractmethod
    async def scan(self) -> list[DiscoveredCamera]:
        """Scan for cameras and return discovered devices.

        Called by backend when polling or when user triggers manual rescan.

        Returns:
            List of discovered cameras
        """
        ...

    @abstractmethod
    async def getConnectionSchema(
        self, camera: DiscoveredCamera
    ) -> list[JsonSchemaWithoutCallbacks]:
        """Get connection schema for a specific discovered camera.

        Returns JsonSchema array for dynamic form generation (credentials only, NO name field).

        Args:
            camera: The discovered camera

        Returns:
            List of schema fields for connection configuration
        """
        ...

    @abstractmethod
    async def connect(
        self, camera: DiscoveredCamera, credentials: dict[str, object]
    ) -> ConnectResult:
        """Connect to a discovered camera and create it.

        Provider is responsible for creating the camera via api.deviceManager.createCamera().

        Args:
            camera: The discovered camera
            credentials: User-provided credentials from schema form

        Returns:
            ConnectResult with cameraId and cameraName
        """
        ...
