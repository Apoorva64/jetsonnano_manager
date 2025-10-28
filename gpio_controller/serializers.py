from rest_framework import serializers
from .models import GPIOConnection, JetsonNanoDevice


class GPIOConnectionSerializer(serializers.ModelSerializer):
    """Serializer for GPIO connection listing and creation."""
    
    class Meta:
        model = GPIOConnection
        fields = ['id', 'name', 'reset', 'force_recovery', 'description', 'is_enabled', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class JetsonNanoDeviceSerializer(serializers.ModelSerializer):
    """Serializer for Jetson Nano device listing and creation."""
    connected_to_name = serializers.CharField(source='connected_to.name', read_only=True)
    
    class Meta:
        model = JetsonNanoDevice
        fields = ['id', 'name', 'connected_to', 'connected_to_name', 'usb_connection', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ResetActionSerializer(serializers.Serializer):
    """Serializer for reset control action."""
    duration = serializers.FloatField(default=0.5, min_value=0.1, max_value=5.0, help_text="Duration in seconds to hold reset pin low")
    success = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True)


class ForceRecoveryActionSerializer(serializers.Serializer):
    """Serializer for force recovery control action."""
    hold_time = serializers.FloatField(default=2.0, min_value=0.5, max_value=10.0, help_text="Duration in seconds to hold recovery pin low")
    success = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True)


class ConnectionActionResponseSerializer(serializers.Serializer):
    """Serializer for connection action responses."""
    connection_id = serializers.IntegerField()
    connection_name = serializers.CharField()
    action = serializers.CharField()
    reset_pin = serializers.IntegerField()
    recovery_pin = serializers.IntegerField()
    success = serializers.BooleanField()
    message = serializers.CharField()
    timestamp = serializers.DateTimeField()
