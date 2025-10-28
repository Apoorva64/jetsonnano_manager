from django.core.management.base import BaseCommand
from gpio_controller.models import GPIOConnection, JetsonNanoDevice
from gpio_controller.services import get_gpio_service


class Command(BaseCommand):
    help = 'Initialize GPIO connections and Jetson Nano devices for control'

    def handle(self, *args, **options):
        # Fixed pin pairs from user specification: 26,19 13,6 5,11 9,10 22,27 17,4 3,2
        pin_pairs = [
            (26, 19),
            (13, 6),
            (5, 11),
            (9, 10),
            (22, 27),
            (17, 4),
            (3, 2),
        ]

        # Default USB ports (typical for Raspberry Pi)
        default_usb_ports = [
            '/dev/ttyUSB0',
            '/dev/ttyUSB1',
            '/dev/ttyUSB2',
            '/dev/ttyUSB3',
            '/dev/ttyUSB4',
            '/dev/ttyUSB5',
            '/dev/ttyUSB6',
        ]

        usb_ports = options.get('usb_ports', default_usb_ports)
        gpio_service = get_gpio_service()

        self.stdout.write('Using fixed pin pairs: 26:19, 13:6, 5:11, 9:10, 22:27, 17:4, 3:2')

        created_connections = 0
        skipped_connections = 0
        created_devices = 0

        for i, (reset_pin, recovery_pin) in enumerate(pin_pairs, 1):
            # Check if connection already exists
            existing_connection = GPIOConnection.objects.filter(
                reset=reset_pin,
                force_recovery=recovery_pin
            ).first()

            if existing_connection:
                self.stdout.write(
                    f'Skipping existing connection: {existing_connection.name} (GPIO{reset_pin}:GPIO{recovery_pin})')
                connection = existing_connection
                skipped_connections += 1
            else:
                # Create new connection
                connection_name = f'Jetson-{reset_pin}-{recovery_pin}'
                connection = GPIOConnection.objects.create(
                    name=connection_name,
                    reset=reset_pin,
                    force_recovery=recovery_pin,
                    description=f'Jetson Nano connection - Reset: GPIO{reset_pin}, Recovery: GPIO{recovery_pin}'
                )

                self.stdout.write(
                    f'Created connection: {connection.name} (Reset: GPIO{reset_pin}, Recovery: GPIO{recovery_pin})')
                created_connections += 1

            # Always setup GPIO pins for this connection (output mode, initial HIGH)
            gpio_service.setup_pins(connection.reset, connection.force_recovery)
            self.stdout.write(
                f'  ✓ GPIO pins initialized for {connection.name} (Reset: GPIO{connection.reset}, Recovery: GPIO{connection.force_recovery})')

            # Create corresponding device if it doesn't exist
            device_name = f'Jetson-Nano-{reset_pin}-{recovery_pin}'
            existing_device = JetsonNanoDevice.objects.filter(name=device_name).first()

            if existing_device:
                self.stdout.write(f'Device {device_name} already exists')
            else:
                device = JetsonNanoDevice.objects.create(
                    name=device_name,
                    connected_to=connection,
                    description=f'Jetson Nano device {i} connected via GPIO and USB'
                )

                self.stdout.write(f'Created device: {device.name} connected to {connection.name}')
                created_devices += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Initialization complete: {created_connections} connections created, {skipped_connections} skipped, {created_devices} devices created'
            )
        )
