import requests
import logging
from xml.etree import ElementTree as ET
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Custom exception for BluOS API errors
class BluOSAPIError(Exception):
    """Exception raised for errors in the BluOS API."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def create_session(retries = 3, backoff_factor = 0.3, status_forcelist = (500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total = retries,
        read = retries,
        connect = retries,
        backoff_factor = backoff_factor,
        status_forcelist = status_forcelist,
    )
    adapter = HTTPAdapter(max_retries = retries)
    session.mount('http://', adapter)
    return session

# Global session for module
session = create_session()

def send_command(device_ip, command, params=None, timeout=None):
    """
    Sends a command to the BluOS device.

    Args:
        device_ip (str): IP address of the BluOS device.
        command (str): Command to execute.
        params (dict, optional): Dictionary of query parameters.
        timeout (int or float, optional): Timeout for the request in seconds.

    Returns:
        ElementTree.Element: Parsed XML response from the device.

    Raises:
        BluOSAPIError: If the request fails or the response contains an error.
    """
    try:
        url = f'http://{device_ip}:11000/{command}'
        logger.debug(f"Sending request to URL: {url} with params: {params} and timeout: {timeout}")
        response = session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        logger.info(f"Executed command '{command}' successfully.")

        if not response.content.strip():
            return None

        # Parse the XML response
        try:
            root = ET.fromstring(response.content)
            return root
        except ET.ParseError as e:
            logger.error(f"Error parsing XML response for command '{command}': {e}")
            raise BluOSAPIError(f"XML parse error: {e}")

    except requests.exceptions.Timeout:
        logger.error(f"Request timed out for command '{command}'")
        raise BluOSAPIError("Request timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception for command '{command}': {e}")
        raise BluOSAPIError(f"Request error: {e}")

def get_status(device_ip, timeout=100):
    """
    Retrieves the status of the BluOS device.

    Args:
        device_ip (str): IP address of the BluOS device.
        timeout (int or float, optional): Timeout for the request in seconds.

    Returns:
        ElementTree.Element: Parsed XML status responds.

    Raises:
        BluOSAPIError: If the request fails or the response contains an error.
    """
    params = {'timeout': timeout}
    return send_command(device_ip, 'Status', params=params, timeout=timeout + 5)  # Adding buffer to timeout

def play(device_ip, seek=0):
    """
    Starts playback on the BluOS device.

    Args:
        device_ip (str): IP address of the BluOS device.
        seek (int, optional): Position to seek to in milliseconds.

    Returns:
        ElementTree.Element: Parsed XML response.

    Raises:
        BluOSAPIError: If the request fails or the response contains an error.
    """
    params = {'seek': seek} if seek else None
    return send_command(device_ip, 'Play', params=params)

def pause(device_ip):
    """
    Pauses playback on the BluOS device.

    Args:
        device_ip (str): IP address of the BluOS device.

    Returns:
        ElementTree.Element: Parsed XML response.

    Raises:
        BluOSAPIError: If the request fails or the response contains an error.
    """
    return send_command(device_ip, 'Pause')


def set_volume(device_ip, level=None, abs_db=None, mute=None, tell_slaves=0):
    """
    Sets the volume level, mute state, or absolute dB level.

    Args:
        device_ip (str): IP address of the BluOS device.
        level (int, optional): Volume level (0-100).
        abs_db (float, optional): Absolute volume level in dB.
        mute (int, optional): Mute state, 0 for unmute, 1 for mute.
        tell_slaves (int, optional): Apply to group (1) or not (0).
    
    Returns:
        ElementTree.Element: Parsed XML response.
    """
    params = {'tell_slaves': tell_slaves}
    if level is not None:
        params['level'] = level
    if abs_db is not None:
        params['abs_db'] = abs_db
    if mute is not None:
        params['mute'] = mute

    return send_command(device_ip, 'Volume', params=params)

def mute(device_ip, mute_state=1, tell_slaves=0):
    """
    Mutes or unmutes the player.

    Args:
        device_ip (str): IP address of the BluOS device.
        mute_state (int): 1 to mute, 0 to unmute.
        tell_slaves (int, optional): Apply to group (1) or not (0).
    
    Returns:
        ElementTree.Element: Parsed XML response.
    """
    params = {
        'mute': mute_state,
        'tell_slaves': tell_slaves
    }
    return send_command(device_ip, 'Volume', params=params)

def adjust_volume(device_ip, db_change, tell_slaves=0):
    """
    Adjusts the volume by a relative dB amount.

    Args:
        device_ip (str): IP address of the BluOS device.
        db_change (float): Amount to adjust the volume in dB (positive or negative).
        tell_slaves (int, optional): Apply to group (1) or not (0).

    Returns:
        ElementTree.Element: Parsed XML response.
    """
    params = {
        'db': db_change,
        'tell_slaves': tell_slaves
    }
    return send_command(device_ip, 'Volume', params=params)

def skip(device_ip):
    return send_command(device_ip, 'Skip')

def back(device_ip):
    return send_command(device_ip, 'Back')

def shuffle(device_ip, state=1):
    params = {'state': state}
    return send_command(device_ip, 'Shuffle', params=params)

def repeat(device_ip, state=1):
    params = {'state': state}
    return send_command(device_ip, 'Repeat', params=params)