from django.db import models


class GPIOConnection(models.Model):
    """
    Represents a physical GPIO pin pair connection on Raspberry Pi.
    
    Two pins form a connection:
    - reset: Pin used for reset control
    - force_recovery: Pin used for force recovery control
    
    These connections are physical and can be connected to any Jetson Nano device.
    The connection is identified by a name/label for reference.
    """
    
    name = models.CharField(max_length=100, unique=True, help_text="Label for this GPIO connection pair (e.g., 'Jetson-1', 'Device-A')")
    reset = models.IntegerField(help_text="BCM GPIO pin number for reset control")
    force_recovery = models.IntegerField(help_text="BCM GPIO pin number for force recovery control")
    description = models.TextField(blank=True, help_text="Description of what this connection controls or where it goes")
    is_enabled = models.BooleanField(default=True, help_text="Whether this connection is enabled and available for control")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "GPIO Connection"
        verbose_name_plural = "GPIO Connections"
        constraints = [
            models.UniqueConstraint(fields=['reset', 'force_recovery'], name='unique_pin_pair'),
        ]

    def __str__(self):
        return f"{self.name} (Reset: GPIO{self.reset}, Recovery: GPIO{self.force_recovery})"


class JetsonNanoDevice(models.Model):
    """
    Represents a Jetson Nano device that can be connected to GPIO connections.
    
    A device tracks which GPIO connection is currently connected to it,
    but the physical connection exists independently.
    """
    
    name = models.CharField(max_length=100, unique=True, help_text="Name of the Jetson Nano device")
    connected_to = models.ForeignKey(
        GPIOConnection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The GPIO connection this device is currently connected to"
    )
    # USB connection identifier for devices that expose a serial/USB interface
    # Examples: '/dev/ttyUSB0', 'usb-0000:00:14.0-1.2', or a serial number
    usb_connection = models.CharField(max_length=200, blank=True, help_text="Optional USB connection identifier (path, serial or port)")
    description = models.TextField(blank=True, help_text="Description of this device or its location")
    is_active = models.BooleanField(default=True, help_text="Whether this device is currently active/accessible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Jetson Nano Device"
        verbose_name_plural = "Jetson Nano Devices"

    def __str__(self):
        connected = f" → {self.connected_to.name}" if self.connected_to else " (not connected)"
        usb = f" [USB: {self.usb_connection}]" if self.usb_connection else ""
        return f"{self.name}{connected}{usb}"
