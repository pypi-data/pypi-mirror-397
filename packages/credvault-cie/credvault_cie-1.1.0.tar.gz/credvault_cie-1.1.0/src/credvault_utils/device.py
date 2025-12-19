"""
CredVault CIE Device SDK

This module provides a Python SDK for IoT devices and robots to communicate with
the CredVault platform. Devices can send telemetry, receive commands, and report status.

Example usage:
    from zoomly_utils.device import Device
    
    device = Device(api_key="cvd_your_api_key", endpoint="https://api.credvault.io")
    device.connect()
    device.send_telemetry(temperature=25.3, battery=85, cpu_usage=45.2)
"""

import requests
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime


class Device:
    """
    CredVault IoT Device SDK
    
    Provides methods for devices to interact with the CredVault platform.
    """
    
    def __init__(
        self,
        api_key: str,
        endpoint: str = "http://localhost:5000",
        device_id: Optional[str] = None
    ):
        """
        Initialize a CredVault device connection.
        
        Args:
            api_key: Device API key (format: cvd_xxxxx)
            endpoint: CredVault API endpoint URL
            device_id: Optional device ID (extracted from API key if not provided)
        """
        self.api_key = api_key
        self.endpoint = endpoint.rstrip('/')
        self.device_id = device_id
        self.connected = False
        self._session = requests.Session()
        self._session.headers.update({
            'X-Device-API-Key': api_key,
            'Content-Type': 'application/json'
        })
    
    def connect(self) -> Dict[str, Any]:
        """
        Connect the device to the CredVault platform.
        
        Returns:
            Connection status and device information
        """
        try:
            response = self._session.post(
                f"{self.endpoint}/api/devices/{self.device_id}/heartbeat",
                json={"action": "connect"}
            )
            response.raise_for_status()
            self.connected = True
            return response.json()
        except requests.RequestException as e:
            raise DeviceConnectionError(f"Failed to connect: {e}")
    
    def disconnect(self) -> bool:
        """
        Disconnect the device from the platform.
        
        Returns:
            True if disconnected successfully
        """
        self.connected = False
        return True
    
    def send_telemetry(
        self,
        temperature: Optional[float] = None,
        battery: Optional[float] = None,
        cpu_usage: Optional[float] = None,
        memory: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        status: str = "operational",
        custom_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send telemetry data to the CredVault platform.
        
        Args:
            temperature: Device/environment temperature in Celsius
            battery: Battery level percentage (0-100)
            cpu_usage: CPU usage percentage (0-100)
            memory: Memory usage percentage (0-100)
            latitude: GPS latitude
            longitude: GPS longitude
            status: Device status ("operational", "warning", "error", "maintenance")
            custom_data: Additional custom telemetry data
            
        Returns:
            Server response with telemetry ID and any triggered alerts
        """
        payload = {
            "metrics": {},
            "status": status,
            "customData": custom_data or {}
        }
        
        # Add metrics that are provided
        if temperature is not None:
            payload["metrics"]["temperature"] = temperature
        if battery is not None:
            payload["metrics"]["battery"] = battery
        if cpu_usage is not None:
            payload["metrics"]["cpuUsage"] = cpu_usage
        if memory is not None:
            payload["metrics"]["memory"] = memory
            
        # Add location if provided
        if latitude is not None and longitude is not None:
            payload["location"] = {
                "latitude": latitude,
                "longitude": longitude
            }
        
        try:
            response = self._session.post(
                f"{self.endpoint}/api/devices/{self.device_id}/telemetry",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise TelemetryError(f"Failed to send telemetry: {e}")
    
    def heartbeat(self) -> Dict[str, Any]:
        """
        Send a heartbeat to the platform to indicate device is alive.
        
        Returns:
            Server response with acknowledgment
        """
        try:
            response = self._session.post(
                f"{self.endpoint}/api/devices/{self.device_id}/heartbeat"
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise DeviceConnectionError(f"Heartbeat failed: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get device configuration from the platform.
        
        Returns:
            Device configuration including alert thresholds
        """
        try:
            response = self._session.get(
                f"{self.endpoint}/api/devices/{self.device_id}/config"
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise DeviceConnectionError(f"Failed to get config: {e}")
    
    def start_telemetry_loop(
        self,
        interval: int = 30,
        get_metrics: callable = None
    ):
        """
        Start a continuous telemetry reporting loop.
        
        Args:
            interval: Seconds between telemetry reports
            get_metrics: Callable that returns a dict of metrics to send
        """
        while True:
            try:
                if get_metrics:
                    metrics = get_metrics()
                    self.send_telemetry(**metrics)
                else:
                    self.heartbeat()
            except Exception as e:
                print(f"Telemetry loop error: {e}")
            time.sleep(interval)


class DeviceConnectionError(Exception):
    """Raised when device fails to connect to the platform."""
    pass


class TelemetryError(Exception):
    """Raised when telemetry transmission fails."""
    pass
