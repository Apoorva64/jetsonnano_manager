from django.apps import AppConfig
from django.core.management import call_command
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GpioControllerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gpio_controller'
    verbose_name = 'GPIO Controller'

    def ready(self):
        """
        Initialize GPIO connections and devices when the app starts.
        This ensures GPIO pins are properly configured on server startup.
        """
        # Only run initialization in production/development, not during migrations/tests
        if not settings.DEBUG or getattr(settings, 'RUN_GPIO_INIT', True):
            try:
                logger.info("Initializing GPIO connections and devices...")
                call_command('init_gpio_devices', verbosity=1)
                logger.info("GPIO initialization completed successfully")
            except Exception as e:
                logger.error(f"Failed to initialize GPIO: {e}")
                # Don't crash the server if GPIO init fails
                pass
