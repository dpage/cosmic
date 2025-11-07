"""Mock urequests module for emulator - wraps requests library"""
try:
    import requests as _requests
except ImportError:
    print("ERROR: requests library not installed. Run: pip install requests")
    raise

class Response:
    def __init__(self, response):
        self._response = response
        self.status_code = response.status_code
        self.text = response.text

    def close(self):
        self._response.close()

def get(url, headers=None, timeout=None):
    """Mock urequests.get using requests library"""
    response = _requests.get(url, headers=headers, timeout=timeout)
    return Response(response)

def post(url, data=None, json=None, headers=None, timeout=None):
    """Mock urequests.post using requests library"""
    response = _requests.post(url, data=data, json=json, headers=headers, timeout=timeout)
    return Response(response)
