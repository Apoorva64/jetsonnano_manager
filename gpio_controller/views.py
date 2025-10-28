import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import GPIOConnection, JetsonNanoDevice
from .serializers import (
    GPIOConnectionSerializer,
    JetsonNanoDeviceSerializer,
    ResetActionSerializer,
    ForceRecoveryActionSerializer,
)
from .services import get_gpio_service

logger = logging.getLogger(__name__)


class GPIOConnectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing physical GPIO connections.
    
    Each connection represents a pair of GPIO pins:
    - reset: Pin for reset control
    - force_recovery: Pin for force recovery control
    
    Endpoints:
    - GET /api/connections/ - List all connections
    - POST /api/connections/ - Create a new connection
    - GET /api/connections/{id}/ - Get connection details
    - PUT /api/connections/{id}/ - Update connection
    - DELETE /api/connections/{id}/ - Delete connection
    - POST /api/connections/{id}/reset/ - Pulse the reset pin
    - POST /api/connections/{id}/force-recovery/ - Trigger force recovery sequence
    - POST /api/connections/{id}/set-pin/ - Set a pin state
    """
    
    queryset = GPIOConnection.objects.all()
    serializer_class = GPIOConnectionSerializer
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'reset':
            return ResetActionSerializer
        elif self.action == 'force_recovery':
            return ForceRecoveryActionSerializer
        return GPIOConnectionSerializer
    
    def perform_create(self, serializer):
        """Setup GPIO pins when a connection is created."""
        connection = serializer.save()
        gpio_service = get_gpio_service()
        gpio_service.setup_pins(connection.reset, connection.force_recovery)
        logger.info(f"Created connection {connection.name} and setup GPIO pins")
    
    @action(detail=True, methods=['post'], url_path='reset')
    def reset(self, request, pk=None):
        """
        Trigger a reset pulse on the reset pin.
        
        POST /api/connections/{id}/reset/
        Body: {
            "duration": 0.5  # Optional, default 0.5 seconds
        }
        """
        connection = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        duration = serializer.validated_data.get('duration', 0.5)
        gpio_service = get_gpio_service()
        
        success = gpio_service.pulse_pin(connection.reset, duration=duration)
        
        response_data = {
            'connection_id': connection.id,
            'connection_name': connection.name,
            'action': 'reset',
            'reset_pin': connection.reset,
            'recovery_pin': connection.force_recovery,
            'success': success,
            'message': f'Reset signal sent on GPIO{connection.reset}' if success else 'Failed to send reset signal',
            'timestamp': timezone.now(),
        }
        
        return Response(
            response_data,
            status=status.HTTP_200_OK if success else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=True, methods=['post'], url_path='force-recovery')
    def force_recovery(self, request, pk=None):
        """
        Trigger force recovery sequence (hold recovery pin, pulse reset).
        
        POST /api/connections/{id}/force-recovery/
        Body: {
            "hold_time": 2.0  # Optional, default 2.0 seconds
        }
        """
        connection = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        hold_time = serializer.validated_data.get('hold_time', 2.0)
        gpio_service = get_gpio_service()
        
        success = gpio_service.force_recovery_sequence(
            connection.force_recovery,
            connection.reset,
            hold_time=hold_time
        )
        
        response_data = {
            'connection_id': connection.id,
            'connection_name': connection.name,
            'action': 'force_recovery',
            'reset_pin': connection.reset,
            'recovery_pin': connection.force_recovery,
            'success': success,
            'message': 'Force recovery sequence completed' if success else 'Failed to trigger force recovery',
            'timestamp': timezone.now(),
        }
        
        return Response(
            response_data,
            status=status.HTTP_200_OK if success else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=True, methods=['post'], url_path='set-pin')
    def set_pin(self, request, pk=None):
        """
        Set a pin state (HIGH/LOW).
        
        POST /api/connections/{id}/set-pin/
        Body: {
            "pin": "reset",  # or "force_recovery"
            "state": true    # true for HIGH, false for LOW
        }
        """
        connection = self.get_object()
        
        pin_name = request.data.get('pin')
        state = request.data.get('state')
        
        if pin_name not in ['reset', 'force_recovery']:
            return Response(
                {'error': 'Invalid pin. Must be "reset" or "force_recovery"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if state is None or not isinstance(state, bool):
            return Response(
                {'error': 'Invalid state. Must be true (HIGH) or false (LOW)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pin = connection.reset if pin_name == 'reset' else connection.force_recovery
        gpio_service = get_gpio_service()
        
        success = gpio_service.set_pin_state(pin, state)
        
        response_data = {
            'connection_id': connection.id,
            'connection_name': connection.name,
            'action': 'set_pin',
            'pin': pin_name,
            'pin_number': pin,
            'state': 'HIGH' if state else 'LOW',
            'reset_pin': connection.reset,
            'recovery_pin': connection.force_recovery,
            'success': success,
            'message': f'Pin {pin_name} set to {"HIGH" if state else "LOW"}' if success else 'Failed to set pin state',
            'timestamp': timezone.now(),
        }
        
        return Response(
            response_data,
            status=status.HTTP_200_OK if success else status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class JetsonNanoDeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Jetson Nano devices.
    
    Devices can be connected to GPIO connections to control them.
    
    Endpoints:
    - GET /api/devices/ - List all devices
    - POST /api/devices/ - Create a new device
    - GET /api/devices/{id}/ - Get device details
    - PUT /api/devices/{id}/ - Update device
    - DELETE /api/devices/{id}/ - Delete device
    - POST /api/devices/{id}/connect/ - Connect device to a GPIO connection
    - POST /api/devices/{id}/disconnect/ - Disconnect device from GPIO connection
    """
    
    queryset = JetsonNanoDevice.objects.all()
    serializer_class = JetsonNanoDeviceSerializer
    
    @action(detail=True, methods=['post'])
    def connect(self, request, pk=None):
        """
        Connect this device to a GPIO connection.
        
        POST /api/devices/{id}/connect/
        Body: {
            "connection_id": 1
        }
        """
        device = self.get_object()
        connection_id = request.data.get('connection_id')
        
        try:
            connection = GPIOConnection.objects.get(id=connection_id)
            device.connected_to = connection
            device.save()
            
            return Response(
                {
                    'device_id': device.id,
                    'device_name': device.name,
                    'connected_to': connection.name,
                    'message': f'Device connected to {connection.name}',
                    'success': True,
                    'timestamp': timezone.now(),
                },
                status=status.HTTP_200_OK
            )
        except GPIOConnection.DoesNotExist:
            return Response(
                {'error': f'GPIO connection with id {connection_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """
        Disconnect this device from its GPIO connection.
        
        POST /api/devices/{id}/disconnect/
        """
        device = self.get_object()
        
        if not device.connected_to:
            return Response(
                {'error': 'Device is not connected to any GPIO connection'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        connection_name = device.connected_to.name
        device.connected_to = None
        device.save()
        
        return Response(
            {
                'device_id': device.id,
                'device_name': device.name,
                'was_connected_to': connection_name,
                'message': f'Device disconnected from {connection_name}',
                'success': True,
                'timestamp': timezone.now(),
            },
            status=status.HTTP_200_OK
        )
