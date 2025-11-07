"""Mock _thread module for emulator"""
import threading as _threading

def start_new_thread(function, args, kwargs=None):
    """Start a new thread"""
    if kwargs is None:
        kwargs = {}
    thread = _threading.Thread(target=function, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread

def allocate_lock():
    """Create a lock"""
    return _threading.Lock()

def get_ident():
    """Get thread identifier"""
    return _threading.get_ident()
