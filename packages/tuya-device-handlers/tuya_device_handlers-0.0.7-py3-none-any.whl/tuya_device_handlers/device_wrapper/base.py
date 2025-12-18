"""Tuya device wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


class DeviceWrapper:
    """Base device wrapper."""

    native_unit: str | None = None
    options: list[str] | None = None
    suggested_unit: str | None = None

    def read_device_status(self, device: CustomerDevice) -> Any | None:
        """Read device status and convert to a Home Assistant value."""
        raise NotImplementedError

    def get_update_commands(
        self, device: CustomerDevice, value: Any
    ) -> list[dict[str, Any]]:
        """Generate update commands for a Home Assistant action."""
        raise NotImplementedError
