from django.core.management.base import BaseCommand
from gpio_controller.models import JetsonNanoDevice
from gpio_controller.services import get_gpio_service


class Command(BaseCommand):
    help = 'Initialize Jetson Nano devices with GPIO pin pairs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--setup',
            action='store_true',
            help='Setup GPIO pins for all devices',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all devices',
        )

    def handle(self, *args, **options):
        # Default GPIO mappings: (device_name, reset_pin, recovery_pin)
        devices = [
            ('Jetson Nano 1', 26, 19),
            ('Jetson Nano 2', 13, 6),
            ('Jetson Nano 3', 5, 11),
            ('Jetson Nano 4', 9, 10),
            ('Jetson Nano 5', 22, 27),
            ('Jetson Nano 6', 17, 4),
            ('Jetson Nano 7', 3, 2),
        ]

        if options['clear']:
            count, _ = JetsonNanoDevice.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {count} devices')
            )
            return

        gpio_service = get_gpio_service()
        created_count = 0
        existing_count = 0

        for name, reset_pin, recovery_pin in devices:
            device, created = JetsonNanoDevice.objects.get_or_create(
                name=name,
                defaults={
                    'reset_pin': reset_pin,
                    'recovery_pin': recovery_pin,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created device: {device.name} (Reset: GPIO{reset_pin}, Recovery: GPIO{recovery_pin})')
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Device already exists: {device.name}')
                )

            # Setup GPIO pins if requested
            if options['setup']:
                gpio_service.setup_pins(reset_pin, recovery_pin)
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ GPIO pins setup for {device.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Initialization complete: {created_count} created, {existing_count} existing'
            )
        )
