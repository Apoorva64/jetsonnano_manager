import logging
import time
from typing import Optional, Tuple

# Try to import RPi.GPIO, fall back to mock for non-RPi systems (development)
try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except RuntimeError:
    # GPIO not available (not running on RPi or permission issues)
    HAS_GPIO = False
except ImportError:
    # RPi.GPIO not installed (development environment)
    HAS_GPIO = False


logger = logging.getLogger(__name__)
# set logger level if needed
logging.basicConfig(level=logging.DEBUG)


class GPIOService:
    """
    Service to manage GPIO pin operations for controlling physical connections.
    
    A connection consists of two GPIO pins (pin_a and pin_b) that can be
    controlled independently or in coordinated sequences.
    """

    def __init__(self):
        """Initialize GPIO service."""
        self.initialized = False
        self._init_gpio()

    def _init_gpio(self):
        """Initialize GPIO pins if available."""
        if not HAS_GPIO:
            logger.warning("RPi.GPIO not available. Running in development mode.")
            return

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            self.initialized = True
            logger.info("GPIO initialized in BCM mode")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            self.initialized = False

    def setup_pins(self, reset_pin: int, recovery_pin: int):
        """
        Setup output pins for a connection.
        
        Args:
            reset_pin: GPIO pin for reset control
            recovery_pin: GPIO pin for force recovery control
        """
        if not HAS_GPIO:
            logger.debug(f"Mock setup pins: reset={reset_pin}, recovery={recovery_pin}")
            return

        try:
            if self.initialized:
                GPIO.setup(reset_pin, GPIO.OUT, initial=GPIO.HIGH)
                GPIO.setup(recovery_pin, GPIO.OUT, initial=GPIO.HIGH)
                logger.info(f"Setup pins: reset={reset_pin}, recovery={recovery_pin}")
        except Exception as e:
            logger.error(f"Failed to setup pins: {e}")

    def cleanup(self):
        """Cleanup GPIO resources."""
        if HAS_GPIO and self.initialized:
            try:
                GPIO.cleanup()
                logger.info("GPIO cleanup complete")
            except Exception as e:
                logger.error(f"Error during GPIO cleanup: {e}")

    def pulse_pin(self, pin: int, duration: float = 0.5) -> bool:
        """
        Pulse a pin LOW then back HIGH.
        
        Args:
            pin: GPIO pin number
            duration: Duration in seconds to hold pin low (default 0.5s)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_GPIO:
            logger.info(f"Mock pulse GPIO{pin} for {duration}s")
            return True

        try:
            if self.initialized:
                # Ensure pin is set up as output before using it
                GPIO.output(pin, GPIO.LOW)
                logger.debug(f"Pulse started on GPIO{pin}")
                time.sleep(duration)
                GPIO.output(pin, GPIO.HIGH)
                logger.info(f"Pin GPIO{pin} pulsed (duration {duration}s)")
                return True
        except Exception as e:
            logger.error(f"Failed to pulse pin: {e}")
            return False

        return False

    def hold_pin_low(self, pin: int, duration: float = 2.0) -> bool:
        """
        Hold a pin LOW for a specified duration.
        
        Args:
            pin: GPIO pin number
            duration: Duration in seconds to hold pin low
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_GPIO:
            logger.info(f"Mock hold GPIO{pin} LOW for {duration}s")
            return True

        try:
            if self.initialized:
                # Ensure pin is set up as output before using it
                GPIO.output(pin, GPIO.LOW)
                logger.debug(f"Holding GPIO{pin} LOW")
                time.sleep(duration)
                GPIO.output(pin, GPIO.HIGH)
                logger.info(f"Released GPIO{pin} after {duration}s hold")
                return True
        except Exception as e:
            logger.error(f"Failed to hold pin: {e}")
            return False

        return False

    def sequence_ab(self, pin_a: int, pin_b: int, hold_time: float = 2.0, pulse_duration: float = 0.5) -> bool:
        """
        Execute sequence: hold pin_a LOW, then pulse pin_b while holding pin_a.
        Useful for force recovery patterns.
        
        Args:
            pin_a: GPIO pin A number
            pin_b: GPIO pin B number
            hold_time: Duration in seconds to hold pin_a low
            pulse_duration: Duration of pin_b pulse
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_GPIO:
            logger.info(f"Mock sequence_ab: hold GPIO{pin_a} for {hold_time}s, pulse GPIO{pin_b} ({pulse_duration}s)")
            return True

        try:
            if self.initialized:
                # Hold pin_a LOW
                GPIO.output(pin_a, GPIO.LOW)
                logger.debug(f"Sequence A->B: holding GPIO{pin_a} LOW")
                time.sleep(hold_time)
                
                # While pin_a held, pulse pin_b
                GPIO.output(pin_b, GPIO.LOW)
                logger.debug(f"Sequence A->B: pulsing GPIO{pin_b}")
                time.sleep(pulse_duration)
                GPIO.output(pin_b, GPIO.HIGH)
                
                # Release pin_a
                time.sleep(0.5)
                GPIO.output(pin_a, GPIO.HIGH)
                logger.info(f"Sequence A->B complete: GPIO{pin_a} held {hold_time}s, GPIO{pin_b} pulsed {pulse_duration}s")
                return True
        except Exception as e:
            logger.error(f"Failed to execute sequence_ab: {e}")
            return False

        return False

    def sequence_ba(self, pin_a: int, pin_b: int, hold_time: float = 2.0, pulse_duration: float = 0.5) -> bool:
        """
        Execute sequence: hold pin_b LOW, then pulse pin_a while holding pin_b.
        
        Args:
            pin_a: GPIO pin A number
            pin_b: GPIO pin B number
            hold_time: Duration in seconds to hold pin_b low
            pulse_duration: Duration of pin_a pulse
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_GPIO:
            logger.info(f"Mock sequence_ba: hold GPIO{pin_b} for {hold_time}s, pulse GPIO{pin_a} ({pulse_duration}s)")
            return True

        try:
            if self.initialized:
                # Hold pin_b LOW
                GPIO.output(pin_b, GPIO.LOW)
                logger.debug(f"Sequence B->A: holding GPIO{pin_b} LOW")
                time.sleep(hold_time)
                
                # While pin_b held, pulse pin_a
                GPIO.output(pin_a, GPIO.LOW)
                logger.debug(f"Sequence B->A: pulsing GPIO{pin_a}")
                time.sleep(pulse_duration)
                GPIO.output(pin_a, GPIO.HIGH)
                
                # Release pin_b
                time.sleep(0.5)
                GPIO.output(pin_b, GPIO.HIGH)
                logger.info(f"Sequence B->A complete: GPIO{pin_b} held {hold_time}s, GPIO{pin_a} pulsed {pulse_duration}s")
                return True
        except Exception as e:
            logger.error(f"Failed to execute sequence_ba: {e}")
            return False

        return False

    def force_recovery_sequence(self, force_recovery_pin: int, reset_pin: int, hold_time: float = 2.0) -> bool:
        """
        Execute force recovery sequence: hold force recovery pin LOW, then pulse reset pin.
        
        Args:
            force_recovery_pin: GPIO pin for force recovery
            reset_pin: GPIO pin for reset
            hold_time: Duration in seconds to hold force recovery pin low
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.sequence_ab(force_recovery_pin, reset_pin, hold_time=hold_time)

    def set_pin_state(self, pin: int, state: bool) -> bool:
        """
        Set a pin to HIGH (True) or LOW (False).
        
        Args:
            pin: GPIO pin number
            state: True for HIGH, False for LOW
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_GPIO:
            logger.info(f"Mock set GPIO{pin} to {'HIGH' if state else 'LOW'}")
            return True

        try:
            if self.initialized:
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
                logger.debug(f"GPIO{pin} set to {'HIGH' if state else 'LOW'}")
                return True
        except Exception as e:
            logger.error(f"Failed to set pin state: {e}")
            return False

        return False


# Global instance
_gpio_service = None


def get_gpio_service() -> GPIOService:
    """Get or create the global GPIO service instance."""
    global _gpio_service
    if _gpio_service is None:
        _gpio_service = GPIOService()
    return _gpio_service


def cleanup_gpio():
    """Cleanup GPIO resources."""
    global _gpio_service
    if _gpio_service:
        _gpio_service.cleanup()
        _gpio_service = None
