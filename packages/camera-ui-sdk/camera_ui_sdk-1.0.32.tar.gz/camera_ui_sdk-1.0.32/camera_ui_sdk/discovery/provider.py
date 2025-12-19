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
    The backend polls getDiscoveredCameras() when users are on the discovery page.

    Example:
        ```python
        class OnvifDiscoveryProvider(DiscoveryProvider):
            def __init__(self):
                self._cameras: dict[str, DiscoveredCamera] = {}

            def getDiscoveredCameras(self) -> list[DiscoveredCamera]:
                return list(self._cameras.values())

            async def getConnectionSchema(
                self, camera: DiscoveredCamera
            ) -> list[JsonSchemaWithoutCallbacks]:
                return [
                    {"key": "username", "type": "string", "title": "Username"},
                    {"key": "password", "type": "string", "title": "Password", "format": "password"},
                ]

            async def connect(
                self, camera: DiscoveredCamera, credentials: dict
            ) -> ConnectResult:
                # Probe ONVIF device, build config, create camera via api.deviceManager.createCamera()
                camera_id = await api.deviceManager.createCamera(config)
                return {"cameraId": camera_id, "cameraName": camera["name"]}
        ```
    """

    @abstractmethod
    def getDiscoveredCameras(self) -> list[DiscoveredCamera]:
        """Get all currently discovered cameras.

        Backend polls this method when users are on the discovery page.
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

    async def rescan(self) -> None:
        """Trigger a manual rescan (optional).

        Returns when scan is complete. Override this method if your
        provider supports manual rescan.
        """
        pass
