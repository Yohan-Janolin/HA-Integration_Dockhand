"""Base entities shared by the platforms.

Every per-container and per-stack entity on the fast coordinator has the same
identity (environment, name), the same lookup of its current data, and the
same device; the platform modules add only what's specific to them.
"""

from typing import Any, override

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import DockhandFastCoordinator
from .helpers import (
    _compose_project,
    _container_device,
    _find_container,
    _find_stack,
    _stack_device,
)


class DockhandEnvScopedEntity(CoordinatorEntity[DockhandFastCoordinator]):
    """An entity belonging to one Dockhand environment."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DockhandFastCoordinator,
        entry_id: str,
        env_id: int,
        env_name: str,
        base_url: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._env_id = env_id
        self._env_name = env_name
        self._base_url = base_url


class DockhandContainerEntity(DockhandEnvScopedEntity):
    """An entity on a container's device, identified by the container's name
    (which, unlike its ID, survives the container being recreated)."""

    def __init__(
        self,
        coordinator: DockhandFastCoordinator,
        entry_id: str,
        env_id: int,
        env_name: str,
        base_url: str,
        container: dict[str, Any],
    ) -> None:
        super().__init__(coordinator, entry_id, env_id, env_name, base_url)
        self._container_name: str = container.get("name", "")

    def _container(self) -> dict[str, Any] | None:
        return _find_container(
            self.coordinator.data, self._env_id, self._container_name
        )

    @property
    @override
    def device_info(self) -> DeviceInfo:
        return _container_device(
            getattr(self, "hass", None),
            self._entry_id,
            self._container_name,
            self._env_id,
            self._env_name,
            self._base_url,
            _compose_project(self._container()),
        )


class DockhandStackEntity(DockhandEnvScopedEntity):
    """An entity on a stack's device, identified by the stack's name."""

    def __init__(
        self,
        coordinator: DockhandFastCoordinator,
        entry_id: str,
        env_id: int,
        env_name: str,
        base_url: str,
        stack: dict[str, Any],
    ) -> None:
        super().__init__(coordinator, entry_id, env_id, env_name, base_url)
        self._stack_name: str = stack.get("name", "")

    def _stack(self) -> dict[str, Any] | None:
        return _find_stack(self.coordinator.data, self._env_id, self._stack_name)

    @property
    @override
    def device_info(self) -> DeviceInfo:
        return _stack_device(
            getattr(self, "hass", None),
            self._entry_id,
            self._stack_name,
            self._env_id,
            self._env_name,
            self._base_url,
            source_type=(self._stack() or {}).get("sourceType"),
        )
