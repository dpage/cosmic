"""Mock network module for emulator - uses host network"""
import socket as _socket

STA_IF = 0

class WLAN:
    def __init__(self, interface):
        self.interface = interface
        self._active = False
        self._connected = False
        self.ssid = None
        self.password = None

    def active(self, state=None):
        if state is not None:
            self._active = state
        return self._active

    def connect(self, ssid, password):
        """Mock connection - just check if we have internet"""
        self.ssid = ssid
        self.password = password
        # Test if we have internet connectivity
        try:
            _socket.create_connection(("8.8.8.8", 53), timeout=3)
            self._connected = True
        except OSError:
            self._connected = False

    def isconnected(self):
        """Check if connected to network"""
        if not self._connected:
            return False
        # Verify we still have connectivity
        try:
            _socket.create_connection(("8.8.8.8", 53), timeout=1)
            return True
        except OSError:
            self._connected = False
            return False

    def ifconfig(self):
        """Return network configuration"""
        # Get host machine's IP
        try:
            s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = "127.0.0.1"

        # Return format: (ip, netmask, gateway, dns)
        return (ip, "255.255.255.0", ip.rsplit('.', 1)[0] + ".1", "8.8.8.8")
