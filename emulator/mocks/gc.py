"""Mock gc (garbage collector) module for emulator"""
import gc as _gc

# Re-export real gc functions
collect = _gc.collect
enable = _gc.enable
disable = _gc.disable
isenabled = _gc.isenabled

def mem_free():
    """Return free memory - mock value"""
    # MicroPython function - return a plausible value for RP2040
    return 200000  # ~200KB free (RP2040 has 264KB total)

def mem_alloc():
    """Return allocated memory - mock value"""
    # MicroPython function
    return 64000  # ~64KB allocated

def threshold(amount=None):
    """Get or set GC threshold"""
    # MicroPython has this, standard Python doesn't
    if amount is None:
        return -1  # Return mock threshold
    # Setting threshold is no-op in emulator
