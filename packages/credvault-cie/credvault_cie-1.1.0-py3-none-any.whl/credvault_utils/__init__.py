"""
CredVault Utilities - Python utilities and helpers for development

Includes:
- Device SDK for IoT/Robot telemetry to CredVault platform
"""

__version__ = "1.1.0"
__author__ = "Samuel Mbugua"
__email__ = "samuelmbuguacredvault@zohomail.com"

from .device import Device, DeviceConnectionError, TelemetryError

__all__ = [
    "get_version",
    "Device",
    "DeviceConnectionError",
    "TelemetryError",
]

def get_version():
    """Get the version of CredVault-Utils"""
    return __version__

