"""Mock machine module for emulator"""
import time as _time

# Machine reset causes
PWRON_RESET = 1
HARD_RESET = 2
WDT_RESET = 3
DEEPSLEEP_RESET = 4
SOFT_RESET = 5

def reset():
    """Reset the device - in emulator, just exit"""
    print("machine.reset() called - exiting emulator")
    import sys
    sys.exit(0)

def soft_reset():
    """Soft reset - in emulator, just exit"""
    print("machine.soft_reset() called - exiting emulator")
    import sys
    sys.exit(0)

def reset_cause():
    """Return the reset cause"""
    return PWRON_RESET

def freq(hz=None):
    """Get or set CPU frequency - mock returns fixed value"""
    if hz is None:
        return 125000000  # 125MHz (typical for RP2040)
    # Ignore setting frequency in emulator

def unique_id():
    """Return unique ID - mock value"""
    return b'\x00\x01\x02\x03\x04\x05\x06\x07'

def idle():
    """Idle the CPU - in emulator, just sleep briefly"""
    _time.sleep(0.001)

def sleep():
    """Light sleep - in emulator, just sleep briefly"""
    _time.sleep(0.01)

def deepsleep(time_ms=0):
    """Deep sleep - in emulator, just sleep"""
    if time_ms > 0:
        _time.sleep(time_ms / 1000.0)

def disable_irq():
    """Disable interrupts - no-op in emulator"""
    pass

def enable_irq():
    """Enable interrupts - no-op in emulator"""
    pass

class Pin:
    """Mock Pin class"""
    IN = 0
    OUT = 1
    PULL_UP = 1
    PULL_DOWN = 2

    def __init__(self, id, mode=-1, pull=-1, value=None):
        self.id = id
        self._mode = mode
        self._pull = pull
        self._value = value if value is not None else 0

    def value(self, v=None):
        """Get or set pin value"""
        if v is None:
            return self._value
        self._value = v
        return None

    def on(self):
        """Turn pin on"""
        self._value = 1

    def off(self):
        """Turn pin off"""
        self._value = 0

    def mode(self, mode=None):
        """Get or set pin mode"""
        if mode is None:
            return self._mode
        self._mode = mode

class ADC:
    """Mock ADC class"""
    def __init__(self, pin):
        self.pin = pin
        self._value = 0

    def read_u16(self):
        """Read analog value as 16-bit unsigned int"""
        return self._value

class PWM:
    """Mock PWM class"""
    def __init__(self, pin, freq=1000, duty_u16=0):
        self.pin = pin
        self._freq = freq
        self._duty = duty_u16

    def freq(self, f=None):
        """Get or set frequency"""
        if f is None:
            return self._freq
        self._freq = f

    def duty_u16(self, d=None):
        """Get or set duty cycle (16-bit)"""
        if d is None:
            return self._duty
        self._duty = d

    def deinit(self):
        """Deinitialize PWM"""
        pass

class Timer:
    """Mock Timer class"""
    PERIODIC = 1
    ONE_SHOT = 0

    def __init__(self, id=-1):
        self.id = id
        self._callback = None

    def init(self, mode=PERIODIC, period=-1, callback=None):
        """Initialize timer"""
        self._callback = callback

    def deinit(self):
        """Deinitialize timer"""
        self._callback = None

class RTC:
    """Mock Real-Time Clock"""
    def __init__(self):
        pass

    def datetime(self, datetimetuple=None):
        """Get or set datetime"""
        import time as _time
        if datetimetuple is None:
            # Return current time as tuple (year, month, day, weekday, hours, minutes, seconds, subseconds)
            t = _time.localtime()
            return (t.tm_year, t.tm_mon, t.tm_mday, t.tm_wday, t.tm_hour, t.tm_min, t.tm_sec, 0)
        # Setting time is ignored in emulator

# Watchdog timer
class WDT:
    """Mock Watchdog Timer"""
    def __init__(self, timeout=5000):
        self.timeout = timeout

    def feed(self):
        """Feed the watchdog - no-op in emulator"""
        pass
